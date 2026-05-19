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
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "kakao",
    name: "카카오쇼핑",
    color: "#FEE500",
    adminUrl: "https://shopping-sell.kakao.com/hub",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "toss",
    name: "토스쇼핑",
    color: "#0064FF",
    adminUrl: "https://shopping-seller.toss.im",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "eleven",
    name: "11번가",
    color: "#FF0000",
    adminUrl: "http://soffice.11st.co.kr/view/main",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "esm",
    name: "G마켓 (ESM+)",
    color: "#EA1917",
    adminUrl: "https://www.esmplus.com",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "ali",
    name: "알리익스프레스",
    color: "#FF6A00",
    adminUrl: "https://sell.aliexpress.com",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "baemin",
    name: "배달의민족",
    color: "#00C4B4",
    adminUrl: "https://scm-mart.baemin.com",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "coupang",
    name: "쿠팡",
    color: "#1A1A1A",
    adminUrl: "https://wing.coupang.com",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
  {
    id: "kurly",
    name: "마켓컬리",
    color: "#5F0080",
    adminUrl: "https://partner.kurly.com",
    newOrders: 0,
    cancelReturns: 0,
    inquiries: [{ type: "고객문의", count: 0 }],
  },
];

export const BULK_ORDER_CHANNELS: BulkOrderChannel[] = [
  { id: "bmart", name: "B마트", adminUrl: "https://mart.baemin.com" },
  { id: "kurly", name: "컬리", adminUrl: "https://partner.kurly.com" },
  { id: "shilla", name: "신라", adminUrl: "https://www.shilladfs.com" },
];
