from .base import BaseScraper

SELLER_BASE = "https://www.oasis.co.kr:9886"


class OasisScraper(BaseScraper):
    async def login(self):
        if await self.try_cookie_login("OASIS_COOKIES", f"{SELLER_BASE}/order/seller/list"):
            return

        await self.page.goto(f"{SELLER_BASE}/login")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(2000)

        # 판매자 로그인 폼
        await self.page.wait_for_selector(
            "#userId, input[name='userId'], input[placeholder*='아이디'], input[type='text']",
            timeout=15000,
        )
        await self.page.fill(
            "#userId, input[name='userId'], input[placeholder*='아이디'], input[type='text']",
            self.config["id"],
        )
        await self.page.fill(
            "#userPw, input[name='userPw'], input[type='password']",
            self.config["password"],
        )
        await self.page.click("button[type='submit'], input[type='submit'], button:has-text('로그인')")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        today = self.today_kst()
        today_compact = today.replace("-", "")
        await self.page.goto(
            f"{SELLER_BASE}/order/seller/list"
            f"?orderStatus=NEW&startDate={today_compact}&endDate={today_compact}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page(".total-count, #totalCount, .count strong")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[2].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        await self.page.goto(f"{SELLER_BASE}/inquiry/seller/list?answered=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        count = await self.count_from_page(".total-count, #totalCount, .count strong")
        self.result["summary"]["inquiries_unanswered"] = count

    async def get_reviews(self):
        await self.page.goto(f"{SELLER_BASE}/review/seller/list?replied=N")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)

        count = await self.count_from_page(".total-count, #totalCount, .count strong")
        self.result["summary"]["reviews_unanswered"] = count
