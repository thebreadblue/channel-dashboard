import os
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
        await self.page.goto("https://shopping-seller.toss.im/login")
        await self.page.wait_for_load_state("load")
        await self.page.wait_for_timeout(3000)

        await self.page.wait_for_selector("input", timeout=20000)
        await self.page.wait_for_timeout(1000)

        os.makedirs("screenshots", exist_ok=True)
        await self.page.screenshot(path="screenshots/toss_before_fill.png")

        await self._fill_react_input(0, self.config["id"])
        await self.page.wait_for_timeout(500)
        await self._fill_react_input(1, self.config["password"])
        await self.page.wait_for_timeout(500)

        await self.page.screenshot(path="screenshots/toss_after_fill.png")

        await self.page.click("button:has-text('로그인')")
        # SPA는 networkidle에 도달하지 않을 수 있어 domcontentloaded + 대기로 처리
        await self.page.wait_for_load_state("domcontentloaded", timeout=20000)
        await self.page.wait_for_timeout(3000)

        await self.page.screenshot(path="screenshots/toss_after_login.png")

    async def get_orders(self):
        await self.page.goto("https://shopping-seller.toss.im/orders")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(4000)
        count = await self.safe_int("[class*='count'], [class*='badge']")
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
        await self.page.goto("https://shopping-seller.toss.im/inquiries")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(4000)
        count = await self.safe_int("[class*='count']")
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
        await self.page.goto("https://shopping-seller.toss.im/reviews")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(4000)
        count = await self.safe_int("[class*='count']")
        self.result["summary"]["reviews_unanswered"] = count
        rows = await self.page.query_selector_all("tbody tr")
        for row in rows[:10]:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                self.result["reviews"].append({
                    "content": (await cells[1].inner_text()).strip()[:100],
                    "status": "미답변",
                })
