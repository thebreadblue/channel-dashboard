from .base import BaseScraper


class GmarketScraper(BaseScraper):
    async def login(self):
        if await self.try_cookie_login("GMARKET_COOKIES", "https://www.esmplus.com/Home"):
            return

        await self.page.goto("https://www.esmplus.com/")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        await self.page.wait_for_selector(
            "#txtMemberID, input[name='memberID'], input[placeholder*='아이디']",
            timeout=15000
        )
        await self.page.fill(
            "#txtMemberID, input[name='memberID'], input[placeholder*='아이디']",
            self.config["id"]
        )
        await self.page.fill(
            "#txtMemberPWD, input[name='memberPWD'], input[type='password']",
            self.config["password"]
        )
        await self.page.click("button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        today = self.today_kst()
        await self.page.goto(
            f"https://www.esmplus.com/Home/v2/order-integration"
            f"?startDate={today}&endDate={today}&orderStatus=NEW"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page("#lblTotalCount, .count em, .total_count strong, [class*='totalCount']")
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
        today = self.today_kst()
        await self.page.goto(
            f"https://www.esmplus.com/CS/CSList"
            f"?AnsStatus=N&BeginDt={today}&EndDt={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page("#lblTotalCount, .count em")
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
        today = self.today_kst()
        await self.page.goto(
            f"https://www.esmplus.com/Review/ReviewList"
            f"?AnsStatus=N&BeginDt={today}&EndDt={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page("#lblTotalCount, .count em")
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
