from .base import BaseScraper


class TossScraper(BaseScraper):
    async def _fill_react_input(self, index: int, value: str):
        """React 제어 input에 값 주입 — native setter로 onChange 트리거"""
        await self.page.evaluate(
            """(args) => {
                const inputs = document.querySelectorAll('input');
                const el = inputs[args.index];
                if (!el) return;
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                setter.call(el, args.value);
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            {"index": index, "value": value},
        )

    async def login(self):
        if await self.try_cookie_login("TOSS_COOKIES", "https://shopping-seller.toss.im/home"):
            return

        await self.page.goto("https://shopping-seller.toss.im/login")
        await self.page.wait_for_load_state("load")
        await self.page.wait_for_timeout(3000)

        await self.page.wait_for_selector("input", timeout=20000)
        await self.page.wait_for_timeout(1000)

        await self._fill_react_input(0, self.config["id"])
        await self.page.wait_for_timeout(500)
        await self._fill_react_input(1, self.config["password"])
        await self.page.wait_for_timeout(500)

        await self.page.click("button:has-text('로그인')")
        await self.page.wait_for_load_state("domcontentloaded", timeout=20000)
        await self.page.wait_for_timeout(3000)

    async def get_orders(self):
        today = self.today_kst()
        await self.page.goto(f"https://shopping-seller.toss.im/orders?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()
        await self.screenshot("orders")

        count = await self.count_from_page("[class*='count'], [class*='badge']")
        self.result["summary"]["orders_new"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["orders"].append({
                    "order_no": (await cells[0].inner_text()).strip(),
                    "product": (await cells[1].inner_text()).strip(),
                    "status": "결제완료",
                })

    async def get_inquiries(self):
        today = self.today_kst()
        await self.page.goto(f"https://shopping-seller.toss.im/inquiries?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()

        count = await self.count_from_page("[class*='count']")
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
        today = self.today_kst()
        await self.page.goto(f"https://shopping-seller.toss.im/reviews?startDate={today}&endDate={today}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(3000)
        await self.apply_date_filter()

        count = await self.count_from_page("[class*='count']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
