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
    talktalk_unanswered?: number;
    qna_unanswered?: number;
    inquiry_unanswered?: number;
    pluschat_unanswered?: number;
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
  와디즈: "wadiz",
  오아이스: "oasis",
};

export async function fetchChannelOverrides(): Promise<
  Record<string, { newOrders: number; inquiries: Record<string, number>; error: boolean }>
> {
  try {
    const res = await fetch(RESULTS_URL, { cache: "no-store" });
    if (!res.ok) return {};
    const data: ResultsJson = await res.json();

    const overrides: Record<string, { newOrders: number; inquiries: Record<string, number>; error: boolean }> = {};
    for (const ch of data.channels) {
      const id = NAME_TO_ID[ch.name];
      if (!id) continue;

      const s = ch.summary ?? {};
      const error = ch.status === "error";

      if (id === "smartstore") {
        overrides[id] = {
          newOrders: s.orders_new ?? 0,
          error,
          inquiries: {
            톡톡: s.talktalk_unanswered ?? 0,
            문의: s.qna_unanswered ?? 0,
            고객문의: s.inquiry_unanswered ?? (s.inquiries_unanswered ?? 0),
          },
        };
      } else if (id === "kakao") {
        overrides[id] = {
          newOrders: s.orders_new ?? 0,
          error,
          inquiries: {
            플친채팅: s.pluschat_unanswered ?? (s.inquiries_unanswered ?? 0),
          },
        };
      } else {
        const total = (s.inquiries_unanswered ?? 0) + (s.reviews_unanswered ?? 0);
        overrides[id] = {
          newOrders: s.orders_new ?? 0,
          error,
          inquiries: { 고객문의: total },
        };
      }
    }
    return overrides;
  } catch {
    return {};
  }
}

export function applyOverrides(
  channels: ChannelStatus[],
  overrides: Record<string, { newOrders: number; inquiries: Record<string, number>; error: boolean }>
): ChannelStatus[] {
  return channels.map((ch) => {
    const ov = overrides[ch.id];
    if (!ov) return ch;

    // 에러 시 수집오류 배지 단일 표시
    if (ov.error) {
      return { ...ch, newOrders: 0, cancelReturns: 0, inquiries: [{ type: "수집오류", count: 1 }] };
    }

    // inquiry 타입별로 mock의 순서를 유지하면서 수치 덮어쓰기
    const updatedInquiries = ch.inquiries.map((inq) => ({
      ...inq,
      count: ov.inquiries[inq.type] ?? inq.count,
    }));

    return {
      ...ch,
      newOrders: ov.newOrders,
      cancelReturns: 0,
      inquiries: updatedInquiries,
    };
  });
}
