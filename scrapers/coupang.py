from .base import BaseScraper


class CoupangScraper(BaseScraper):
    """
    쿠팡 서플라이어: Akamai WAF가 GitHub Actions IP를 차단 (Access Denied).
    Playwright 자동화 불가 → 어드민 링크만 제공, 수동 확인 안내.
    """
    async def login(self):
        raise Exception("쿠팡 WAF(Akamai) IP 차단 - GitHub Actions에서 자동 로그인 불가. 어드민에서 직접 확인하세요.")

    async def get_orders(self):
        pass

    async def get_inquiries(self):
        pass

    async def get_reviews(self):
        pass
