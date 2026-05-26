import os
import re
import json
import base64
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
                try:
                    await el.click(click_count=3)
                    await el.fill(today, timeout=5000)
                except Exception:
                    pass
                break

        # 종료 날짜 (시작과 별도 필드인 경우)
        for sel in [
            "#endDate", "#toDate", "#end_date", "#edate",
            "input[placeholder*='종료']", "input[placeholder*='to']",
        ]:
            el = await self.page.query_selector(sel)
            if el:
                try:
                    await el.click(click_count=3)
                    await el.fill(today, timeout=5000)
                except Exception:
                    pass
                break

        # 조회/검색 버튼
        for sel in [
            "button:has-text('조회')", "button:has-text('검색')",
            ".btn-search", ".btn_search", "button:has-text('Search')",
        ]:
            el = await self.page.query_selector(sel)
            if el:
                try:
                    await el.click()
                    await self.page.wait_for_timeout(3000)
                except Exception:
                    pass
                break

    async def try_cookie_login(self, env_key: str, target_url: str, fail_if_url_contains: str = "login") -> bool:
        """쿠키로 로그인 시도. 성공하면 True, 실패/쿠키 없으면 False."""
        cookies_b64 = os.environ.get(env_key, "")
        if not cookies_b64:
            return False
        try:
            cookies = json.loads(base64.b64decode(cookies_b64).decode())
            await self.page.context.add_cookies(cookies)
            await self.page.goto(target_url)
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_timeout(2000)
            url = self.page.url.lower()
            if fail_if_url_contains and fail_if_url_contains in url:
                print(f"[{self.name}] 쿠키 만료 → ID/PW 폴백")
                return False
            print(f"[{self.name}] 쿠키 로그인 성공")
            return True
        except Exception as e:
            print(f"[{self.name}] 쿠키 로드 실패: {e}")
            return False

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

    async def count_from_page(self, css_selector: str = "") -> int:
        """CSS 셀렉터 → 페이지 텍스트 패턴 → tbody 행 수 순으로 카운트 추출"""
        # 1. CSS 셀렉터
        if css_selector:
            val = await self.safe_int(css_selector)
            if val > 0:
                return val

        # 2. 페이지 텍스트 패턴 ('N건씩 보기' 같은 UI 텍스트 제외하기 위해 '총/전체' prefix 우선)
        try:
            text = await self.page.evaluate("() => document.body.innerText")
            print(f"  [count_debug:{self.name}] url={self.page.url[:80]}")
            print(f"  [count_debug:{self.name}] text_sample={text[:300]!r}")
            for pattern in [
                r"총\s*([\d,]+)\s*건",
                r"전체\s*([\d,]+)\s*건",
                r"검색결과\s*([\d,]+)",
                r"검색 결과\s*([\d,]+)",
            ]:
                m = re.search(pattern, text)
                if m:
                    val = int(m.group(1).replace(",", ""))
                    print(f"  [count_debug:{self.name}] matched pattern={pattern!r} → {val}")
                    return val
        except Exception as e:
            print(f"  [count_debug:{self.name}] evaluate error: {e}")

        # 3. tbody 행 수 (마지막 수단)
        try:
            rows = await self.page.query_selector_all("tbody tr")
            n = len(rows)
            print(f"  [count_debug:{self.name}] tbody rows={n}")
            if n > 0:
                return n
        except Exception:
            pass

        return 0
