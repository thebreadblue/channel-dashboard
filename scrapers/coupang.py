from .base import BaseScraper


class CoupangScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://supplier.coupang.com/login")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("input[name='username'], input[type='text'], #username", self.config["id"])
        await self.page.fill("input[name='password'], input[type='password'], #password", self.config["password"])
        await self.page.click("button[type='submit'], input[type='submit'], .login-btn")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

    async def get_orders(self):
        await self.page.goto("https://supplier.coupang.com/order/list?status=ACCEPT")
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
        await self.page.goto("https://supplier.coupang.com/cs/inquiry?answered=N")
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
        await self.page.goto("https://supplier.coupang.com/review/list?replyYn=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, [class*='totalCount']")
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
