from .base import BaseScraper


class SmartstoreScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://nid.naver.com/nidlogin.login?url=https://sell.smartstore.naver.com")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("#id", self.config["id"])
        await self.page.fill("#pw", self.config["password"])
        await self.page.click(".btn_login")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        try:
            skip = await self.page.query_selector("a.btn_cancel, button.btn_skip")
            if skip:
                await skip.click()
                await self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    async def get_orders(self):
        today = self.today_kst()
        # SPA 해시 라우팅에 날짜 파라미터 전달 시도
        await self.page.goto(
            f"https://sell.smartstore.naver.com/#/orders/list"
            f"?startDate={today}&endDate={today}&orderStatus=PAY_DONE"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        # URL 파라미터 미반영 시 UI 날짜 필터 적용
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page(".count strong, .total-count strong, [class*='count']")
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
        today = self.today_kst()
        await self.page.goto(
            f"https://sell.smartstore.naver.com/#/qna/list"
            f"?answerStatus=UNANSWERERD&startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page(".total-count strong, .count strong")
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
            f"https://sell.smartstore.naver.com/#/review/list"
            f"?replyStatus=UNRESPONDED&startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page(".total-count strong, .count strong")
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
