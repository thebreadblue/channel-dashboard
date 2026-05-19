import os
from .base import BaseScraper


class KurlyScraper(BaseScraper):
    async def login(self):
        # 루트로 이동해서 리다이렉트 따라가기
        await self.page.goto("https://partner.kurly.com")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)

        os.makedirs("screenshots", exist_ok=True)
        await self.page.screenshot(path="screenshots/컬리_login_page.png", full_page=True)

        # 컬리 파트너: email 또는 ID 필드 (더 넓은 셀렉터)
        await self.page.wait_for_selector("input", timeout=20000)
        await self.page.wait_for_timeout(500)

        # 첫 번째 input에 ID/이메일 입력
        inputs = await self.page.query_selector_all("input")
        if len(inputs) >= 1:
            await inputs[0].click()
            await inputs[0].fill(self.config["id"])
        if len(inputs) >= 2:
            await inputs[1].click()
            await inputs[1].fill(self.config["password"])

        await self.page.screenshot(path="screenshots/컬리_filled.png", full_page=True)

        await self.page.click("button[type='submit'], button:has-text('로그인'), button:has-text('Login')")
        await self.page.wait_for_load_state("networkidle", timeout=20000)
        await self.page.screenshot(path="screenshots/컬리_after_login.png", full_page=True)

    async def get_orders(self):
        today = self.today_kst()
        await self.page.goto(f"https://partner.kurly.com/#/order/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.safe_int(".total-count, .count, [class*='count']")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr, [class*='order-item']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        today = self.today_kst()
        await self.page.goto(f"https://partner.kurly.com/#/cs/inquiry?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()

        count = await self.safe_int(".total-count, [class*='count']")
        self.result["summary"]["inquiries_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["inquiries"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })

    async def get_reviews(self):
        today = self.today_kst()
        await self.page.goto(f"https://partner.kurly.com/#/review/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()

        count = await self.safe_int(".total-count, [class*='count']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "rating": "",
                    "status": "미답변",
                })
