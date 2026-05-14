from .base import BaseScraper


class ElevenStreetScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://soffice.11st.co.kr/view/main", timeout=60000)
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        await self.page.wait_for_selector("#sellerId, input[name='sellerId']", timeout=20000)
        await self.page.fill("#sellerId, input[name='sellerId']", self.config["id"])
        await self.page.fill("#sellerPwd, input[name='sellerPwd']", self.config["password"])
        await self.page.click("#loginBtn, button[type='submit'], .btn_login")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        await self.page.goto("https://soffice.11st.co.kr/view/order/orderList")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int(".total_count strong, #totalCnt")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 4:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[2].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        await self.page.goto("https://soffice.11st.co.kr/view/cs/inquiryList")
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
        await self.page.goto("https://soffice.11st.co.kr/view/review/buyReviewList")
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
                    "status": "미답변",
                })
