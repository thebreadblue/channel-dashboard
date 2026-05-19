from .base import BaseScraper


class KakaoScraper(BaseScraper):
    async def login(self):
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

        count = await self.safe_int("[class*='totalCount'], [class*='total-count'], .count")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
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
        await self.page.goto(f"https://shopping-sell.kakao.com/inquiry/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.safe_int("[class*='totalCount'], [class*='total-count']")
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
        await self.page.goto(f"https://shopping-sell.kakao.com/review/list?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.safe_int("[class*='totalCount'], [class*='total-count']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
