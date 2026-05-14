from .base import BaseScraper


class AliexpressScraper(BaseScraper):
    async def login(self):
        await self.page.goto("https://login.alibaba.com/icbu/login.htm?site=aliexpress&return_url=https://sell.aliexpress.com")
        await self.page.wait_for_load_state("domcontentloaded")

        await self.page.fill("input[name='account'], input[type='email'], #fm-login-id", self.config["id"])
        await self.page.fill("input[name='password'], input[type='password'], #fm-login-password", self.config["password"])
        await self.page.click("button[type='submit'], .login-btn, #login-form button")
        await self.page.wait_for_load_state("networkidle", timeout=20000)

    async def get_orders(self):
        await self.page.goto("https://sell.aliexpress.com/order/list.htm?status=NEW_ORDER")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, .count-text, [class*='count']")
        self.result["summary"]["orders_new"] = count

        rows = await self.page.query_selector_all("tbody tr, [class*='order-item']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 3:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "신규주문",
                })

    async def get_inquiries(self):
        await self.page.goto("https://msg.aliexpress.com/buyerMsgList.htm?filter=buyer_unanswer")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, [class*='count']")
        self.result["summary"]["inquiries_unanswered"] = count

        items = await self.page.query_selector_all("[class*='msg-item'], .message-item")
        for item in items[:10]:
            content = await item.inner_text()
            self.result["inquiries"].append({
                "content": content.strip()[:100],
                "status": "미답변",
            })

    async def get_reviews(self):
        await self.page.goto("https://sell.aliexpress.com/review/index.htm")
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        count = await self.safe_int(".total-count, [class*='count']")
        self.result["summary"]["reviews_unanswered"] = count

        rows = await self.page.query_selector_all("tbody tr, [class*='review-item']")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
