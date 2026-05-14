from .base import BaseScraper


class ElevenStreetScraper(BaseScraper):
    async def login(self):
        # 11번가 셀러오피스 직접 로그인 URL
        await self.page.goto("https://soffice.11st.co.kr/view/login", timeout=60000)
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        # 홈페이지로 리다이렉트된 경우 로그인 링크 찾기
        if "login" not in self.page.url and "main" not in self.page.url:
            login_link = await self.page.query_selector("a[href*='login'], .btn_login, a:has-text('로그인')")
            if login_link:
                await login_link.click()
                await self.page.wait_for_load_state("domcontentloaded")

        await self.page.wait_for_selector("input[name='sellerId'], #sellerId, input[placeholder*='아이디']", timeout=20000)
        await self.page.fill("input[name='sellerId'], #sellerId, input[placeholder*='아이디']", self.config["id"])
        await self.page.fill("input[name='sellerPwd'], #sellerPwd, input[type='password']", self.config["password"])
        await self.page.click("#loginBtn, button[type='submit'], .btn_login, input[type='submit']")
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
