from .base import BaseScraper


class WadizScraper(BaseScraper):
    async def login(self):
        if await self.try_cookie_login("WADIZ_COOKIES", "https://www.wadiz.kr/web/main"):
            return

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
        # 와디즈 스토어 프로젝트 목록
        await self.page.goto("https://www.wadiz.kr/web/maker/projects?type=store")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(3000)
        await self.screenshot("orders")

        count = await self.count_from_page(
            "[class*='totalCount'], [class*='total-count'], [class*='count'], .badge"
        )
        self.result["summary"]["orders_new"] = count

    async def get_inquiries(self):
        # 와디즈 문의 (메이커센터 고객문의)
        await self.page.goto("https://www.wadiz.kr/web/maker/cs/inquiries")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        count = await self.count_from_page(
            "[class*='totalCount'], [class*='total-count'], [class*='count']"
        )
        self.result["summary"]["inquiries_unanswered"] = count

    async def get_reviews(self):
        # 와디즈 리뷰
        await self.page.goto("https://www.wadiz.kr/web/maker/cs/reviews")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        count = await self.count_from_page(
            "[class*='totalCount'], [class*='total-count'], [class*='count']"
        )
        self.result["summary"]["reviews_unanswered"] = count
