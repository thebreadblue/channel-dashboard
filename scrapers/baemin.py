from .base import BaseScraper


class BaeminScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://scm-mart.baemin.com/auth/login")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("input[type='email'], input[name='email'], input[placeholder*='이메일']", self.config["id"])
        await self.page.fill("input[type='password']", self.config["password"])
        await self.page.click("button[type='submit'], button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        # 이메일 인증 코드 요청하는 경우 처리 불가 → 에러로 기록
        if "verify" in self.page.url or "otp" in self.page.url:
            raise Exception("2차 인증(OTP/이메일) 필요 - 수동 로그인 후 세션 저장 필요")

    async def get_orders(self):
        await self.page.goto("https://scm-mart.baemin.com/order/list?status=PAY_COMPLETE")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, .count strong, [class*='count']")
        self.result["summary"]["orders_new"] = count

        rows = await self.page.query_selector_all("tbody tr, [class*='order-row']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "결제완료",
                })

    async def get_inquiries(self):
        await self.page.goto("https://scm-mart.baemin.com/cs/inquiry?status=UNANSWERED")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, [class*='count']")
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
        await self.page.goto("https://scm-mart.baemin.com/cs/review")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, [class*='count']")
        self.result["summary"]["reviews_unanswered"] = count

        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
