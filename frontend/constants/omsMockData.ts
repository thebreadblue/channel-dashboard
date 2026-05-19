export interface MonthlyKpi {
  year: number;
  month: number;
  totalOrderCount: number;
  totalRevenue: number;
  cancelReturnCount: number;
  cancelReturnAmount: number;
}

export interface InquiryItem {
  type: string;
  count: number;
}

export interface ChannelStatus {
  id: string;
  name: string;
  color: string;
  adminUrl: string;
  newOrders: number;
  cancelReturns: number;
  inquiries: InquiryItem[];
}

export interface BulkOrderChannel {
  id: string;
  name: string;
  adminUrl: string;
}

export const MONTHLY_KPI_DATA: MonthlyKpi[] = [
  { year: 2026, month: 5, totalOrderCount: 1284, totalRevenue: 38520000, cancelReturnCount: 37, cancelReturnAmount: 1120000 },
  { year: 2026, month: 4, totalOrderCount: 1102, totalRevenue: 33150000, cancelReturnCount: 29, cancelReturnAmount: 870000 },
  { year: 2026, month: 3, totalOrderCount: 1350, totalRevenue: 40500000, cancelReturnCount: 42, cancelReturnAmount: 1260000 },
  { year: 2025, month: 12, totalOrderCount: 2100, totalRevenue: 63000000, cancelReturnCount: 68, cancelReturnAmount: 2040000 },
  { year: 2025, month: 11, totalOrderCount: 1780, totalRevenue: 53400000, cancelReturnCount: 54, cancelReturnAmount: 1620000 },
];

export const CHANNEL_STATUS_DATA: ChannelStatus[] = [
  {
    id: "smartstore",
    name: "네이버 스마트스토어",
    color: "#03C75A",
    adminUrl: "https://sell.smartstore.naver.com",
    newOrders: 23,
    cancelReturns: 3,
    inquiries: [
      { type: "고객문의", count: 5 },
      { type: "톡톡문의", count: 8 },
    ],
  },
  {
    id: "kakao",
    name: "카카오쇼핑",
    color: "#FEE500",
    adminUrl: "https://shopping-sell.kakao.com/hub",
    newOrders: 11,
    cancelReturns: 1,
    inquiries: [
      { type: "플친채팅", count: 4 },
    ],
  },
  {
    id: "esm",
    name: "ESM (G마켓)",
    color: "#EA1917",
    adminUrl: "https://www.esmplus.com",
    newOrders: 18,
    cancelReturns: 2,
    inquiries: [
      { type: "고객문의", count: 6 },
    ],
  },
  {
    id: "eleven",
    name: "11번가",
    color: "#FF0000",
    adminUrl: "http://soffice.11st.co.kr/view/main",
    newOrders: 9,
    cancelReturns: 0,
    inquiries: [
      { type: "고객문의", count: 2 },
    ],
  },
  {
    id: "toss",
    name: "토스쇼핑",
    color: "#0064FF",
    adminUrl: "https://shopping-seller.toss.im",
    newOrders: 7,
    cancelReturns: 1,
    inquiries: [
      { type: "고객문의", count: 1 },
    ],
  },
  {
    id: "wadiz",
    name: "와디즈",
    color: "#FF5B37",
    adminUrl: "https://www.wadiz.kr/web/wmaker/main",
    newOrders: 14,
    cancelReturns: 0,
    inquiries: [
      { type: "고객문의", count: 3 },
    ],
  },
  {
    id: "ali",
    name: "알리익스프레스",
    color: "#FF6A00",
    adminUrl: "https://sell.aliexpress.com",
    newOrders: 5,
    cancelReturns: 0,
    inquiries: [
      { type: "고객문의", count: 0 },
    ],
  },
  {
    id: "oasis",
    name: "오아시스",
    color: "#00B050",
    adminUrl: "https://partner.oasis.co.kr",
    newOrders: 6,
    cancelReturns: 0,
    inquiries: [
      { type: "고객문의", count: 1 },
    ],
  },
  {
    id: "plto",
    name: "플토 (이데이몰)",
    color: "#6366F1",
    adminUrl: "https://www.edaymall.co.kr",
    newOrders: 3,
    cancelReturns: 0,
    inquiries: [
      { type: "고객문의", count: 0 },
    ],
  },
];

export const BULK_ORDER_CHANNELS: BulkOrderChannel[] = [
  { id: "bmart", name: "B마트", adminUrl: "https://mart.baemin.com" },
  { id: "kurly", name: "컬리", adminUrl: "https://partner.kurly.com" },
  { id: "shilla", name: "신라", adminUrl: "https://www.shilladfs.com" },
];
