"use client";

import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ShoppingBag, TrendingUp, TrendingDown, Wallet } from "lucide-react";
import { MONTHLY_KPI_DATA, type MonthlyKpi } from "@/constants/omsMockData";

function fmt(n: number) {
  return n.toLocaleString("ko-KR") + "원";
}

function fmtCount(n: number) {
  return n.toLocaleString("ko-KR") + "건";
}

interface KpiCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
  highlight?: boolean;
  accent?: "red" | "blue" | "default";
}

function KpiCard({ label, value, icon, highlight, accent = "default" }: KpiCardProps) {
  const accentCls = {
    red: "text-rose-600",
    blue: "text-blue-600",
    default: "text-slate-800",
  }[accent];

  return (
    <Card className={highlight ? "border-slate-800 shadow-md" : ""}>
      <CardContent className="pt-5 pb-5">
        <div className="flex items-start justify-between mb-3">
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</span>
          <div className="p-1.5 rounded-md bg-slate-100 text-slate-500">{icon}</div>
        </div>
        <p className={`font-bold leading-none truncate ${highlight ? "text-2xl" : "text-xl"} ${accentCls}`}>
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

const YEARS = [...new Set(MONTHLY_KPI_DATA.map((d) => d.year))].sort((a, b) => b - a);
const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);

export function MonthlySummary() {
  const [year, setYear] = useState(MONTHLY_KPI_DATA[0].year);
  const [month, setMonth] = useState(MONTHLY_KPI_DATA[0].month);

  const data: MonthlyKpi | undefined = useMemo(
    () => MONTHLY_KPI_DATA.find((d) => d.year === year && d.month === month),
    [year, month]
  );

  const netRevenue = data ? data.totalRevenue - data.cancelReturnAmount : 0;

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-800">당월 전체 채널 지표 요약</h2>
          <p className="text-xs text-slate-400 mt-0.5">채널 통합 월별 KPI</p>
        </div>
        <div className="flex gap-2">
          <Select value={String(year)} onValueChange={(v) => setYear(Number(v))}>
            <SelectTrigger className="w-24 h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {YEARS.map((y) => (
                <SelectItem key={y} value={String(y)} className="text-xs">{y}년</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={String(month)} onValueChange={(v) => setMonth(Number(v))}>
            <SelectTrigger className="w-20 h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {MONTHS.map((m) => (
                <SelectItem key={m} value={String(m)} className="text-xs">{m}월</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {data ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          <KpiCard
            label="전체 주문 건수"
            value={fmtCount(data.totalOrderCount)}
            icon={<ShoppingBag className="w-4 h-4" />}
            accent="blue"
          />
          <KpiCard
            label="전체 주문 매출"
            value={fmt(data.totalRevenue)}
            icon={<TrendingUp className="w-4 h-4" />}
          />
          <KpiCard
            label="취소/반품 건수"
            value={fmtCount(data.cancelReturnCount)}
            icon={<TrendingDown className="w-4 h-4" />}
            accent="red"
          />
          <KpiCard
            label="취소/반품 금액"
            value={fmt(data.cancelReturnAmount)}
            icon={<TrendingDown className="w-4 h-4" />}
            accent="red"
          />
          <KpiCard
            label="당월 최종 매출"
            value={fmt(netRevenue)}
            icon={<Wallet className="w-4 h-4" />}
            highlight
          />
        </div>
      ) : (
        <div className="h-28 flex items-center justify-center text-sm text-slate-400 bg-slate-50 rounded-lg border border-dashed border-slate-200">
          해당 월 데이터 없음
        </div>
      )}
    </section>
  );
}
