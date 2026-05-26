import os
import httpx
from .base import BaseScraper, now_kst

API_BASE = "https://openapi.11st.co.kr/openapi/rest"


class ElevenStreetApi:
    """11번가 Open API 클라이언트"""

    def __init__(self, api_key: str):
        self.headers = {"openapikey": api_key, "Accept": "application/json"}

    def _get(self, path: str, params: dict = None) -> dict:
        res = httpx.get(
            f"{API_BASE}{path}",
            headers=self.headers,
            params=params or {},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()

    def new_orders(self, today: str) -> int:
        # 결제완료(1) 주문 수
        data = self._get("/product/orderdetail", {
            "ordStatus": "1",
            "ordStartDy": today,
            "ordEndDy": today,
            "pageNum": "1",
            "pageSize": "1",
        })
        return int(data.get("ProductOrderDetailResponse", {}).get("totalCount", 0))

    def cancel_returns(self, today: str) -> int:
        # 취소/교환/반품 건수
        data = self._get("/product/clmdetail", {
            "clmStartDy": today,
            "clmEndDy": today,
            "pageNum": "1",
            "pageSize": "1",
        })
        return int(data.get("ProductClaimDetailResponse", {}).get("totalCount", 0))

    def inquiries(self, today: str) -> int:
        data = self._get("/product/qna", {
            "ansStatus": "N",
            "startDy": today,
            "endDy": today,
            "pageNum": "1",
            "pageSize": "1",
        })
        return int(data.get("ProductQnaResponse", {}).get("totalCount", 0))


class ElevenStreetScraper(BaseScraper):
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        api_key = os.environ.get("ELEVEN_API_KEY", "")
        self._api = ElevenStreetApi(api_key) if api_key else None

    async def scrape(self, browser):
        if self._api:
            print("[11번가] Open API 사용")
            try:
                return self._scrape_via_api()
            except Exception as e:
                print(f"[11번가] API 오류 ({e}) → 스크래퍼 폴백")
        return await super().scrape(browser)

    def _scrape_via_api(self) -> dict:
        today = self.today_kst()
        today_11 = today.replace("-", "")
        try:
            self.result["summary"]["orders_new"] = self._api.new_orders(today_11)
            self.result["summary"]["cancelReturns"] = self._api.cancel_returns(today_11)
            self.result["summary"]["inquiries_unanswered"] = self._api.inquiries(today_11)
            self.result["status"] = "ok"
        except Exception as e:
            self.result["status"] = "error"
            self.result["error"] = str(e)
        finally:
            self.result["updated_at"] = now_kst()
        return self.result

    # ── 스크래퍼 폴백 ──────────────────────────────────────────

    async def login(self):
        if await self.try_cookie_login("ELEVEN_COOKIES", "http://soffice.11st.co.kr/view/main"):
            return

        await self.page.goto("https://soffice.11st.co.kr/view/login", timeout=60000)
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        if "login" not in self.page.url and "main" not in self.page.url:
            login_link = await self.page.query_selector("a[href*='login'], .btn_login, a:has-text('로그인')")
            if login_link:
                await login_link.click()
                await self.page.wait_for_load_state("domcontentloaded")

        await self.page.wait_for_selector("input[name='sellerId'], #sellerId, input[placeholder*='아이디']", timeout=20000)
        await self.page.fill("input[name='sellerId'], #sellerId, input[placeholder*='아이디']", self.config["id"])
        await self.page.fill("input[name='sellerPwd'], #sellerPwd, input[type='password']", self.config["password"])
        await self.page.click("#loginBtn, button[type='submit'], .btn_login, input[type='submit']")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        today = self.today_kst()
        today_11 = today.replace("-", "")
        await self.page.goto(
            f"https://soffice.11st.co.kr/view/order/orderList"
            f"?startDt={today_11}&endDt={today_11}&orderStatus=NEW"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page(".total_count strong, #totalCnt")
        self.result["summary"]["orders_new"] = count

    async def get_inquiries(self):
        today = self.today_kst()
        today_11 = today.replace("-", "")
        await self.page.goto(
            f"https://soffice.11st.co.kr/view/cs/inquiryList"
            f"?startDt={today_11}&endDt={today_11}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page(".total_count strong, #totalCnt")
        self.result["summary"]["inquiries_unanswered"] = count

    async def get_reviews(self):
        today = self.today_kst()
        today_11 = today.replace("-", "")
        await self.page.goto(
            f"https://soffice.11st.co.kr/view/review/buyReviewList"
            f"?startDt={today_11}&endDt={today_11}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page(".total_count strong, #totalCnt")
        self.result["summary"]["reviews_unanswered"] = count
