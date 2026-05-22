import os
import json
import base64
from .base import BaseScraper


class KakaoScraper(BaseScraper):
    async def login(self):
        # 쿠키 인증 우선
        cookies_b64 = os.environ.get("KAKAO_COOKIES", "")
        if cookies_b64:
            try:
                cookies = json.loads(base64.b64decode(cookies_b64).decode())
                await self.page.context.add_cookies(cookies)
                await self.page.goto("https://shopping-sell.kakao.com/hub")
                await self.page.wait_for_load_state("domcontentloaded")
                await self.page.wait_for_timeout(2000)
                if "login" not in self.page.url and "accounts" not in self.page.url:
                    print("[카카오] 쿠키 로그인 성공")
                    return
                print("[카카오] 쿠키 만료 — ID/PW 로그인 시도")
            except Exception as e:
                print(f"[카카오] 쿠키 로드 실패: {e}")

        await self.page.goto("https://accounts.kakao.com/login?continue=https%3A%2F%2Fshopping-sell.kakao.com%2Fhub")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        await self.page.wait_for_selector("input[placeholder*='카카오메일'], input[placeholder*='아이디'], input[placeholder*='이메일']", timeout=15000)
        await self.page.fill("input[placeholder*='카카오메일'], input[placeholder*='아이디'], input[placeholder*='이메일']", self.config["id"])
        await self.page.fill("input[type='password'], input[placeholder*='비밀번호']", self.config["password"])
        await self.page.click("button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        today = self.today_kst()
        await self.page.goto(f"https://shopping-sell.kakao.com/order/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page("[class*='totalCount'], [class*='total-count'], .count")
        self.result["summary"]["orders_new"] = count

    async def get_inquiries(self):
        today = self.today_kst()

        # 카카오쇼핑 상품 문의
        await self.page.goto(f"https://shopping-sell.kakao.com/inquiry/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        inquiry_count = await self.count_from_page("[class*='totalCount'], [class*='total-count']")
        self.result["summary"]["inquiries_unanswered"] = inquiry_count

        # 카카오 채널(플친) 미답변 채팅
        await self.page.goto("https://bizmessage.kakao.com/chat/list")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        pluschat_count = await self.count_from_page("[class*='unread'], [class*='badge'], .count-badge")
        self.result["summary"]["pluschat_unanswered"] = pluschat_count

    async def get_reviews(self):
        today = self.today_kst()
        await self.page.goto(f"https://shopping-sell.kakao.com/review/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page("[class*='totalCount'], [class*='total-count']")
        self.result["summary"]["reviews_unanswered"] = count
