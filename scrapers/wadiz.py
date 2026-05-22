from .base import BaseScraper


class WadizScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://www.wadiz.kr/web/main")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(1500)

        # 로그인 버튼 클릭
        for sel in ["a:has-text('로그인')", "button:has-text('로그인')", ".login-btn", "[href*='login']"]:
            el = await self.page.query_selector(sel)
            if el:
                await el.click()
                await self.page.wait_for_load_state("domcontentloaded")
                await self.page.wait_for_timeout(1500)
                break

        # 이메일/비밀번호 입력
        await self.page.wait_for_selector(
            "input[type='email'], input[name='email'], input[placeholder*='이메일']",
            timeout=15000,
        )
        await self.page.fill(
            "input[type='email'], input[name='email'], input[placeholder*='이메일']",
            self.config["id"],
        )
        await self.page.fill(
            "input[type='password'], input[placeholder*='비밀번호']",
            self.config["password"],
        )
        await self.page.click("button[type='submit'], button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        today = self.today_kst()
        # 와디즈 스토어 주문 관리
        await self.page.goto(
            f"https://biz.wadiz.kr/store/orders?startDate={today}&endDate={today}&status=NEW"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page("[class*='totalCount'], [class*='total'], .count strong")
        self.result["summary"]["orders_new"] = count

    async def get_inquiries(self):
        # 와디즈 고객 문의
        await self.page.goto("https://biz.wadiz.kr/store/inquiries?answered=false")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        count = await self.count_from_page("[class*='totalCount'], [class*='total'], .count strong")
        self.result["summary"]["inquiries_unanswered"] = count

    async def get_reviews(self):
        # 와디즈 리뷰 미답변
        await self.page.goto("https://biz.wadiz.kr/store/reviews?replied=false")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        count = await self.count_from_page("[class*='totalCount'], [class*='total'], .count strong")
        self.result["summary"]["reviews_unanswered"] = count
