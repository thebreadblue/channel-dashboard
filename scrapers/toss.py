from .base import BaseScraper


class TossScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://shopping-seller.toss.im/login")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("input[type='email'], input[name='email'], input[placeholder*='이메일']", self.config["id"])
        await self.page.fill("input[type='password']", self.config["password"])
        await self.page.click("button[type='submit'], button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

    async def get_orders(self):
        await self.page.goto("https://shopping-seller.toss.im/orders?status=PAYMENT_COMPLETE")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int("[class*='count'], [class*='badge'], .total")
        self.result["summary"]["orders_new"] = count

        rows = await self.page.query_selector_all("tbody tr, [class*='orderItem']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "결제완료",
                })

    async def get_inquiries(self):
        await self.page.goto("https://shopping-seller.toss.im/inquiries?answered=false")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int("[class*='count'], .total")
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
        # 토스쇼핑 리뷰 페이지
        await self.page.goto("https://shopping-seller.toss.im/reviews")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int("[class*='count'], .total")
        self.result["summary"]["reviews_unanswered"] = count

        rows = await self.page.query_selector_all("tbody tr, [class*='reviewItem']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
