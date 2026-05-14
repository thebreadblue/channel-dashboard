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
            await self.login()
            await self.get_orders()
            await self.get_inquiries()
            await self.get_reviews()
        except Exception as e:
            self.result["status"] = "error"
            self.result["error"] = str(e)
            print(f"[{self.name}] 오류: {e}")
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
