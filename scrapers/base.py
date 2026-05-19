import os
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod

KST = timezone(timedelta(hours=9))


def now_kst():
    return datetime.now(KST).isoformat()


class BaseScraper(ABC):
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.page = None
        self.result = {
            "name": name,
            "url": config.get("url", ""),
            "status": "ok",
            "error": None,
            "updated_at": None,
            "summary": {
                "orders_new": 0,
                "inquiries_unanswered": 0,
                "reviews_unanswered": 0,
            },
            "orders": [],
            "inquiries": [],
            "reviews": [],
        }

    def today_kst(self) -> str:
        return datetime.now(KST).strftime("%Y-%m-%d")

    async def apply_date_filter(self):
        """오늘 날짜 필터 UI 적용 — 날짜 input을 찾아 채우고 조회 버튼 클릭"""
        today = self.today_kst()

        # 시작 날짜
        for sel in [
            "input[type='date']",
            "#startDate", "#fromDate", "#start_date", "#sdate",
            "input[placeholder*='시작']", "input[placeholder*='from']",
        ]:
            el = await self.page.query_selector(sel)
            if el:
                await el.triple_click()
                await el.fill(today)
                break

        # 종료 날짜 (시작과 별도 필드인 경우)
        for sel in [
            "#endDate", "#toDate", "#end_date", "#edate",
            "input[placeholder*='종료']", "input[placeholder*='to']",
        ]:
            el = await self.page.query_selector(sel)
            if el:
                await el.triple_click()
                await el.fill(today)
                break

        # 조회/검색 버튼
        for sel in [
            "button:has-text('조회')", "button:has-text('검색')",
            ".btn-search", ".btn_search", "button:has-text('Search')",
        ]:
            el = await self.page.query_selector(sel)
            if el:
                await el.click()
                await self.page.wait_for_timeout(2000)
                break

    async def screenshot(self, tag: str):
        """디버그 스크린샷 저장"""
        try:
            os.makedirs("screenshots", exist_ok=True)
            await self.page.screenshot(
                path=f"screenshots/{self.name}_{tag}.png", full_page=True
            )
        except Exception:
            pass

    @abstractmethod
    async def login(self):
        pass

    async def get_orders(self):
        pass

    async def get_inquiries(self):
        pass

    async def get_reviews(self):
        pass

    async def scrape(self, browser):
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        try:
            self.page = await context.new_page()
            self.page.set_default_timeout(30000)
            await self.login()
            await self.get_orders()
            await self.get_inquiries()
            await self.get_reviews()
        except Exception as e:
            self.result["status"] = "error"
            self.result["error"] = str(e)
            print(f"[{self.name}] 오류: {e}")
            try:
                await self.screenshot("error")
            except Exception:
                pass
        finally:
            self.result["updated_at"] = now_kst()
            await context.close()
        return self.result

    async def safe_text(self, selector: str, default="") -> str:
        try:
            el = await self.page.query_selector(selector)
            return (await el.inner_text()).strip() if el else default
        except Exception:
            return default

    async def safe_int(self, selector: str, default=0) -> int:
        text = await self.safe_text(selector)
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else default
