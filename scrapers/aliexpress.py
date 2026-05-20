from .base import BaseScraper


class AliexpressScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://login.aliexpress.com/")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)

        await self.page.wait_for_selector(
            "input[type='email'], input[type='text'], input[placeholder*='Email'], input[placeholder*='email'], input[placeholder*='phone']",
            timeout=20000
        )
        await self.page.fill(
            "input[type='email'], input[type='text'], input[placeholder*='Email'], input[placeholder*='email'], input[placeholder*='phone']",
            self.config["id"]
        )
        await self.page.click("button:has-text('Continue'), button[type='submit']")
        await self.page.wait_for_timeout(2000)

        await self.page.wait_for_selector("input[type='password']", timeout=15000)
        await self.page.fill("input[type='password']", self.config["password"])
        await self.page.click("button:has-text('Sign in'), button:has-text('로그인'), button[type='submit']")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        today = self.today_kst()
        await self.page.goto(
            f"https://sell.aliexpress.com/order/list.htm"
            f"?status=0&startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page(".total-count, [class*='count']")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        await self.page.goto("https://msg.aliexpress.com/buyerMsgList.htm")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.apply_date_filter()

        items = await self.page.query_selector_all("[class*='msg-item'], .message-item")
        self.result["summary"]["inquiries_unanswered"] = len(items)
        for item in items[:10]:
            self.result["inquiries"].append({
                "content": (await item.inner_text()).strip()[:100],
                "status": "미답변",
            })

    async def get_reviews(self):
        today = self.today_kst()
        await self.page.goto(
            f"https://sell.aliexpress.com/review/index.htm"
            f"?startDate={today}&endDate={today}"
        )
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        await self.page.wait_for_timeout(2000)
        await self.apply_date_filter()

        count = await self.count_from_page(".total-count, [class*='count']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
