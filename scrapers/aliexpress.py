from .base import BaseScraper


class AliexpressScraper(BaseScraper):
    async def login(self):
        # 알리익스프레스 셀러 로그인 직접 URL
        await self.page.goto("https://login.aliexpress.com/")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)

        await self.page.wait_for_selector(
            "#fm-login-id, input[name='loginId'], input[placeholder*='Email'], input[placeholder*='email']",
            timeout=20000
        )
        await self.page.fill(
            "#fm-login-id, input[name='loginId'], input[placeholder*='Email'], input[placeholder*='email']",
            self.config["id"]
        )
        await self.page.fill("#fm-login-password, input[name='password'], input[type='password']", self.config["password"])
        await self.page.click("#fm-login-submit, button[type='submit'], .fm-btn")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        await self.page.goto("https://sell.aliexpress.com/order/list.htm")
        await self.page.wait_for_load_state("networkidle", timeout=15000)
        count = await self.safe_int(".total-count, [class*='count']")
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
        items = await self.page.query_selector_all("[class*='msg-item'], .message-item")
        self.result["summary"]["inquiries_unanswered"] = len(items)
        for item in items[:10]:
            self.result["inquiries"].append({
                "content": (await item.inner_text()).strip()[:100],
                "status": "미답변",
            })

    async def get_reviews(self):
        await self.page.goto("https://sell.aliexpress.com/review/index.htm")
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
