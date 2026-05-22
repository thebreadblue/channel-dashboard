"use client";

import { useEffect, useState, useCallback } from "react";
import { ExternalLink, RefreshCw } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CHANNEL_STATUS_DATA, type ChannelStatus } from "@/constants/omsMockData";
import { fetchChannelOverrides, applyOverrides } from "@/lib/fetchChannelData";

function StatPill({
  label,
  value,
  highlight,
}: {
  label: string;
  value: number;
  highlight?: boolean;
}) {
  return (
    <div className="flex flex-col items-center gap-0.5">
      <span
        className={`text-lg font-bold leading-none ${
          highlight && value > 0 ? "text-rose-600" : value > 0 ? "text-blue-600" : "text-slate-300"
        }`}
      >
        {value}
      </span>
      <span className="text-[10px] text-slate-400 font-medium">{label}</span>
    </div>
  );
}

function ChannelCard({ ch }: { ch: ChannelStatus }) {
  const totalInquiries = ch.inquiries.reduce((s, i) => s + i.count, 0);
  const initial = ch.name.replace(/[^가-힣A-Za-z0-9]/g, "")[0] ?? "?";
  const isError = ch.inquiries.some((i) => i.type === "수집오류");

  return (
    <Card className={`transition-shadow ${isError ? "border-slate-200 bg-slate-50 opacity-50" : "hover:shadow-md"}`}>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold text-white shrink-0"
              style={{ backgroundColor: ch.color }}
            >
              {initial}
            </div>
            <span className="text-sm font-semibold text-slate-800 leading-tight">{ch.name}</span>
          </div>
          <a
            href={ch.adminUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="h-7 w-7 flex items-center justify-center rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="flex items-center justify-around pt-1 pb-1 border-t border-slate-100">
          <StatPill label="신규주문" value={ch.newOrders} />
          <div className="w-px h-8 bg-slate-100" />
          <StatPill label="취소/반품" value={ch.cancelReturns} highlight />
          <div className="w-px h-8 bg-slate-100" />
          <StatPill label="문의" value={totalInquiries} />
        </div>

        {ch.inquiries.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {ch.inquiries.map((inq) => (
              <Badge
                key={inq.type}
                variant={inq.count > 0 ? "default" : "secondary"}
                className={`text-[10px] px-2 py-0.5 font-medium ${
                  inq.count > 0
                    ? inq.type === "수집오류"
                      ? "bg-red-50 text-red-600 border border-red-200 hover:bg-red-50"
                      : "bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-50"
                    : "bg-slate-50 text-slate-400 border border-slate-100"
                }`}
              >
                {inq.type} {inq.count > 0 && <span className="ml-1 font-bold">{inq.count}</span>}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ChannelStatusGrid() {
  const [channels, setChannels] = useState<ChannelStatus[]>(CHANNEL_STATUS_DATA);
  const [updatedAt, setUpdatedAt] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const [overrides, raw] = await Promise.all([
      fetchChannelOverrides(),
      fetch("https://raw.githubusercontent.com/thebreadblue/channel-dashboard/main/data/results.json", {
        cache: "no-store",
      })
        .then((r) => r.json())
        .catch(() => null),
    ]);
    if (Object.keys(overrides).length > 0) {
      setChannels(applyOverrides(CHANNEL_STATUS_DATA, overrides));
    }
    if (raw?.updated_at) setUpdatedAt(raw.updated_at);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const subtitle = loading
    ? "데이터 불러오는 중..."
    : updatedAt
    ? `최종 수집: ${new Date(updatedAt).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })}`
    : "1시간마다 자동 갱신";

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-800">채널별 당일 현황</h2>
          <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
        </div>
        <button
          onClick={refresh}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-50 hover:border-slate-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
          새로고침
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {channels.map((ch) => (
          <ChannelCard key={ch.id} ch={ch} />
        ))}
      </div>
    </section>
  );
}
