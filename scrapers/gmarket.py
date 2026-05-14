from .base import BaseScraper


class GmarketScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://www.esmplus.com/Member/SignIn")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("#txtLoginID, input[name='id']", self.config["id"])
        await self.page.fill("#txtLoginPWD, input[name='pw'], input[type='password']", self.config["password"])
        await self.page.click("#btnLogin, button[type='submit'], .btn_login")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

    async def get_orders(self):
        # ESM+ 주문관리 - 신규주문
        await self.page.goto("https://www.esmplus.com/Deliver/DeliverList?OrderStatus=1")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total_count strong, #lblTotalCount, .count em")
        self.result["summary"]["orders_new"] = count

        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 4:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[2].inner_text()).strip(),
                    "buyer": (await cells[3].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        await self.page.goto("https://www.esmplus.com/CS/CSList?AnsStatus=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total_count strong, #lblTotalCount")
        self.result["summary"]["inquiries_unanswered"] = count

        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["inquiries"].append({
                    "product": (await cells[1].inner_text()).strip(),
                    "content": (await cells[2].inner_text()).strip()[:100],
                    "status": "미답변",
                })

    async def get_reviews(self):
        await self.page.goto("https://www.esmplus.com/Review/ReviewList?AnsStatus=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total_count strong, #lblTotalCount")
        self.result["summary"]["reviews_unanswered"] = count

        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["reviews"].append({
                    "product": (await cells[1].inner_text()).strip(),
                    "content": (await cells[2].inner_text()).strip()[:100],
                    "rating": "",
                    "status": "미답변",
                })
