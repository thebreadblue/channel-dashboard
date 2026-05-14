from .base import BaseScraper


class TossScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://shopping-seller.toss.im/login")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        # placeholder 속성 없음 → 순서로 접근
        await self.page.wait_for_selector("input", timeout=15000)
        inputs = self.page.locator("input")
        await inputs.nth(0).fill(self.config["id"])
        await inputs.nth(1).fill(self.config["password"])
        await self.page.click("button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        await self.page.goto("https://shopping-seller.toss.im/orders")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int("[class*='count'], [class*='badge']")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "결제완료",
                })

    async def get_inquiries(self):
        await self.page.goto("https://shopping-seller.toss.im/inquiries")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int("[class*='count']")
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
        await self.page.goto("https://shopping-seller.toss.im/reviews")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int("[class*='count']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
