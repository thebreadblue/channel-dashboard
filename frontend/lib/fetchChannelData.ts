import type { ChannelStatus } from "@/constants/omsMockData";

const RESULTS_URL =
  "https://raw.githubusercontent.com/thebreadblue/channel-dashboard/main/data/results.json";

interface ScrapedChannel {
  name: string;
  status: string;
  summary: {
    orders_new: number;
    inquiries_unanswered: number;
    reviews_unanswered: number;
  };
}

interface ResultsJson {
  updated_at: string;
  channels: ScrapedChannel[];
}

// 스크래퍼 채널명 → 프론트 ID 매핑
const NAME_TO_ID: Record<string, string> = {
  스마트스토어: "smartstore",
  카카오: "kakao",
  토스쇼핑: "toss",
  "11번가": "eleven",
  "G마켓(ESM+)": "esm",
  알리익스프레스: "ali",
  배민: "baemin",
  쿠팡: "coupang",
  컬리: "kurly",
};

export async function fetchChannelOverrides(): Promise<
  Record<string, { newOrders: number; inquiries: number; reviews: number; error: boolean }>
> {
  try {
    const res = await fetch(RESULTS_URL, { cache: "no-store" });
    if (!res.ok) return {};
    const data: ResultsJson = await res.json();

    const overrides: Record<string, { newOrders: number; inquiries: number; reviews: number; error: boolean }> = {};
    for (const ch of data.channels) {
      const id = NAME_TO_ID[ch.name];
      if (!id) continue;
      overrides[id] = {
        newOrders: ch.summary?.orders_new ?? 0,
        inquiries: ch.summary?.inquiries_unanswered ?? 0,
        reviews: ch.summary?.reviews_unanswered ?? 0,
        error: ch.status === "error",
      };
    }
    return overrides;
  } catch {
    return {};
  }
}

export function applyOverrides(
  channels: ChannelStatus[],
  overrides: Record<string, { newOrders: number; inquiries: number; reviews: number; error: boolean }>
): ChannelStatus[] {
  return channels.map((ch) => {
    const ov = overrides[ch.id];
    if (!ov) return ch;
    const totalInq = ov.inquiries + ov.reviews;
    return {
      ...ch,
      newOrders: ov.newOrders,
      cancelReturns: 0,
      inquiries: [{ type: ov.error ? "수집오류" : "미답변", count: totalInq }],
    };
  });
}
