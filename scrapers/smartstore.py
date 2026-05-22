import os
import json
import base64
import time
import hashlib
import hmac
import httpx
from .base import BaseScraper


class NaverCommerceApi:
    """네이버 커머스 API 클라이언트 (Client Credentials 방식)"""

    BASE = "https://api.commerce.naver.com/external"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None
        self._token_exp: float = 0

    def _sign(self, timestamp: int) -> str:
        msg = f"{self.client_id}_{timestamp}"
        sig = hmac.new(
            self.client_secret.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.b64encode(sig).decode()

    def _ensure_token(self):
        if self._token and time.time() < self._token_exp - 60:
            return
        ts = int(time.time() * 1000)
        res = httpx.post(
            f"{self.BASE}/v1/oauth2/token",
            data={
                "client_id": self.client_id,
                "timestamp": ts,
                "client_secret_sign": self._sign(ts),
                "grant_type": "client_credentials",
                "type": "SELF",
            },
            timeout=10,
        )
        res.raise_for_status()
        data = res.json()
        self._token = data["access_token"]
        self._token_exp = time.time() + data.get("expires_in", 3600)

    def _get(self, path: str, params: dict = None) -> dict:
        self._ensure_token()
        res = httpx.get(
            f"{self.BASE}{path}",
            headers={"Authorization": f"Bearer {self._token}"},
            params=params or {},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()

    def new_orders_today(self, today: str) -> int:
        data = self._get(
            "/v1/pay-order/seller/orders/count",
            {"paymentDateFrom": f"{today}T00:00:00.000+09:00",
             "paymentDateTo": f"{today}T23:59:59.999+09:00",
             "paymentStatus": "PAYED"},
        )
        return data.get("count", 0)

    def talktalk_unanswered(self) -> int:
        # 네이버 톡톡 미답변 채팅 (채팅방 기반)
        data = self._get("/v1/talktalk/seller/chats", {"statusList": "CHAT_OPEN", "size": 1})
        return data.get("totalCount", 0)

    def qna_unanswered(self, today: str) -> int:
        data = self._get(
            "/v1/question/seller/questions",
            {"answered": "false", "writtenFrom": today, "writtenTo": today, "size": 1},
        )
        return data.get("totalCount", 0)

    def reviews_unanswered(self, today: str) -> int:
        data = self._get(
            "/v1/reviews/seller",
            {"replied": "false", "writtenFrom": today, "writtenTo": today, "size": 1},
        )
        return data.get("totalCount", 0)


class SmartstoreScraper(BaseScraper):
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        client_id = os.environ.get("SMARTSTORE_CLIENT_ID", "")
        client_secret = os.environ.get("SMARTSTORE_CLIENT_SECRET", "")
        self._api = NaverCommerceApi(client_id, client_secret) if client_id and client_secret else None

    async def login(self):
        # 쿠키 인증 우선 (Naver 봇 차단 우회)
        cookies_b64 = os.environ.get("SMARTSTORE_COOKIES", "")
        if cookies_b64:
            try:
                cookies = json.loads(base64.b64decode(cookies_b64).decode())
                await self.page.context.add_cookies(cookies)
                await self.page.goto("https://sell.smartstore.naver.com/#/home/dashboard")
                await self.page.wait_for_load_state("domcontentloaded")
                await self.page.wait_for_timeout(2000)
                if "#/home/about" not in self.page.url:
                    print(f"[스마트스토어] 쿠키 로그인 성공")
                    return
                print("[스마트스토어] 쿠키 만료 — ID/PW 로그인 시도")
            except Exception as e:
                print(f"[스마트스토어] 쿠키 로드 실패: {e}")

        # 폴백: ID/PW 로그인
        await self.page.goto("https://nid.naver.com/nidlogin.login?url=https://sell.smartstore.naver.com")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.fill("#id", self.config["id"])
        await self.page.fill("#pw", self.config["password"])
        await self.page.click(".btn_login")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        try:
            skip = await self.page.query_selector("a.btn_cancel, button.btn_skip")
            if skip:
                await skip.click()
                await self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    async def scrape(self, browser):
        # API 사용 가능 시 브라우저 없이 수행
        if self._api:
            print("[스마트스토어] Naver Commerce API 사용")
            try:
                return await self._scrape_via_api()
            except Exception as e:
                print(f"[스마트스토어] API 오류 ({e}) → 스크래퍼 폴백")

        return await super().scrape(browser)

    async def _scrape_via_api(self):
        from scrapers.base import now_kst
        today = self.today_kst()
        try:
            orders_new = self._api.new_orders_today(today)
            talktalk = self._api.talktalk_unanswered()
            qna = self._api.qna_unanswered(today)
            reviews = self._api.reviews_unanswered(today)

            self.result["summary"]["orders_new"] = orders_new
            self.result["summary"]["talktalk_unanswered"] = talktalk
            self.result["summary"]["qna_unanswered"] = qna
            self.result["summary"]["inquiry_unanswered"] = reviews
            self.result["summary"]["inquiries_unanswered"] = qna + reviews
            self.result["status"] = "ok"
        except Exception as e:
            self.result["status"] = "error"
            self.result["error"] = str(e)
        finally:
            self.result["updated_at"] = now_kst()
        return self.result

    async def get_orders(self):
        today = self.today_kst()
        await self.page.goto(
            f"https://sell.smartstore.naver.com/#/orders/list"
            f"?startDate={today}&endDate={today}&orderStatus=PAY_DONE"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page(".count strong, .total-count strong, [class*='count']")
        self.result["summary"]["orders_new"] = count

    async def get_inquiries(self):
        today = self.today_kst()

        # 상품 Q&A (문의)
        await self.page.goto(
            f"https://sell.smartstore.naver.com/#/qna/list"
            f"?answerStatus=UNANSWERERD&startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        qna_count = await self.count_from_page(".total-count strong, .count strong")
        self.result["summary"]["qna_unanswered"] = qna_count

        # 고객문의 (CS 문의)
        await self.page.goto(
            f"https://sell.smartstore.naver.com/#/cs/list"
            f"?answerStatus=UNANSWERERD&startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        cs_count = await self.count_from_page(".total-count strong, .count strong")
        self.result["summary"]["inquiry_unanswered"] = cs_count

        # 톡톡 (스마트스토어 판매자 톡톡 채팅 미답변)
        await self.page.goto("https://sell.smartstore.naver.com/#/talktalk/list")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        talktalk_count = await self.count_from_page(".badge-count, [class*='unread'], .total-count strong")
        self.result["summary"]["talktalk_unanswered"] = talktalk_count

        # 호환성: 기존 필드도 유지
        self.result["summary"]["inquiries_unanswered"] = qna_count + cs_count

    async def get_reviews(self):
        today = self.today_kst()
        await self.page.goto(
            f"https://sell.smartstore.naver.com/#/review/list"
            f"?replyStatus=UNRESPONDED&startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        count = await self.count_from_page(".total-count strong, .count strong")
        self.result["summary"]["reviews_unanswered"] = count
