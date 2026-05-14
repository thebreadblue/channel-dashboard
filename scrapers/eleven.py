from .base import BaseScraper


class ElevenStreetScraper(BaseScraper):
    async def login(self):
        await self.page.goto("http://soffice.11st.co.kr/view/main")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("input[name='sellerId'], #id, input[placeholder*='아이디']", self.config["id"])
        await self.page.fill("input[name='sellerPwd'], #pw, input[type='password']", self.config["password"])
        await self.page.click("button[type='submit'], .btn_login, a.login")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

    async def get_orders(self):
        await self.page.goto("http://soffice.11st.co.kr/view/order/list?orderStatus=NEW")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total_count strong, .total strong, #totalCnt")
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
        await self.page.goto("http://soffice.11st.co.kr/view/cs/inquiryList?ansYn=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total_count strong, #totalCnt")
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
        await self.page.goto("http://soffice.11st.co.kr/view/review/list?replyYn=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total_count strong, #totalCnt")
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
