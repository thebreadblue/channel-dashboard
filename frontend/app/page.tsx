import { Header } from "@/components/layout/Header";
import { MonthlySummary } from "@/components/MonthlySummary";
import { ChannelStatusGrid } from "@/components/ChannelStatusGrid";
import { BulkOrderLinks } from "@/components/BulkOrderLinks";
import { CHANNEL_STATUS_DATA } from "@/constants/omsMockData";

export default function DashboardPage() {
  const totalNewOrders = CHANNEL_STATUS_DATA.reduce((s, ch) => s + ch.newOrders, 0);

  return (
    <>
      <Header title="대시보드" newOrderCount={totalNewOrders} />
      <main className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
        <MonthlySummary />
        <ChannelStatusGrid />
        <BulkOrderLinks />
      </main>
    </>
  );
}
