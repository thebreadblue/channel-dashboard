from .base import BaseScraper


class KakaoScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://accounts.kakao.com/login?continue=https://shopping-sell.kakao.com/hub")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("input[name='loginKey'], input[type='email']", self.config["id"])
        await self.page.fill("input[name='password'], input[type='password']", self.config["password"])
        await self.page.click("button[type='submit'], .btn_confirm")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

    async def get_orders(self):
        await self.page.goto("https://shopping-sell.kakao.com/order/list?status=NEW_ORDER")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, .count-badge, [class*='totalCount']")
        self.result["summary"]["orders_new"] = count

        rows = await self.page.query_selector_all("tbody tr, [class*='orderRow']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        await self.page.goto("https://shopping-sell.kakao.com/inquiry/list?status=UNANSWERED")
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
        await self.page.goto("https://shopping-sell.kakao.com/review/list?status=UNANSWERED")
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
