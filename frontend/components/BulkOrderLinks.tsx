import { ExternalLink, PackageOpen } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BULK_ORDER_CHANNELS } from "@/constants/omsMockData";

export function BulkOrderLinks() {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-slate-800">대량 발주 확인</h2>
        <p className="text-xs text-slate-400 mt-0.5">클릭 시 해당 어드민 페이지로 이동</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {BULK_ORDER_CHANNELS.map((ch) => (
          <Card
            key={ch.id}
            className="hover:shadow-md transition-shadow cursor-pointer group"
          >
            <a href={ch.adminUrl} target="_blank" rel="noopener noreferrer" className="block">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-slate-100 group-hover:bg-slate-200 transition-colors">
                    <PackageOpen className="w-4 h-4 text-slate-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">{ch.name}</p>
                    <p className="text-xs text-slate-400">어드민 바로가기</p>
                  </div>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-300 group-hover:text-slate-500 transition-colors" />
              </CardContent>
            </a>
          </Card>
        ))}
      </div>
    </section>
  );
}
