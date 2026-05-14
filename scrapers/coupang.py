from .base import BaseScraper


class CoupangScraper(BaseScraper):
    async def login(self):
        # 쿠팡은 Keycloak SSO(xauth.coupang.com)로 리다이렉트됨
        await self.page.goto("https://supplier.coupang.com/login")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)

        # Keycloak 로그인 폼
        await self.page.wait_for_selector("#username, input[name='username']", timeout=20000)
        await self.page.fill("#username, input[name='username']", self.config["id"])
        await self.page.fill("#password, input[name='password']", self.config["password"])
        await self.page.click("#kc-login, input[type='submit'], button[type='submit']")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        await self.page.goto("https://supplier.coupang.com/order/list")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int(".total-count, .count strong, [class*='totalCount']")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 4:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[2].inner_text()).strip(),
                    "status": "접수완료",
                })

    async def get_inquiries(self):
        await self.page.goto("https://supplier.coupang.com/cs/inquiry")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int(".total-count, [class*='totalCount']")
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
        await self.page.goto("https://supplier.coupang.com/review/list")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int(".total-count, [class*='totalCount']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
