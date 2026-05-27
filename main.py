import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.async_api import async_playwright

from scrapers.smartstore import SmartstoreScraper
from scrapers.kakao import KakaoScraper
from scrapers.toss import TossScraper
from scrapers.eleven import ElevenStreetScraper
from scrapers.gmarket import GmarketScraper
from scrapers.aliexpress import AliexpressScraper
from scrapers.wadiz import WadizScraper
from scrapers.oasis import OasisScraper

KST = timezone(timedelta(hours=9))

CHANNELS = [
    {
        "scraper": SmartstoreScraper,
        "name": "스마트스토어",
        "url": "https://sell.smartstore.naver.com",
        "id": os.environ.get("SMARTSTORE_ID", ""),
        "password": os.environ.get("SMARTSTORE_PW", ""),
    },
    {
        "scraper": KakaoScraper,
        "name": "카카오",
        "url": "https://shopping-sell.kakao.com/hub",
        "id": os.environ.get("KAKAO_ID", ""),
        "password": os.environ.get("KAKAO_PW", ""),
    },
    {
        "scraper": GmarketScraper,
        "name": "G마켓(ESM+)",
        "url": "https://www.esmplus.com/Home",
        "id": os.environ.get("GMARKET_ID", ""),
        "password": os.environ.get("GMARKET_PW", ""),
    },
    {
        "scraper": ElevenStreetScraper,
        "name": "11번가",
        "url": "http://soffice.11st.co.kr/view/main",
        "id": os.environ.get("ELEVEN_ID", ""),
        "password": os.environ.get("ELEVEN_PW", ""),
    },
    {
        "scraper": TossScraper,
        "name": "토스쇼핑",
        "url": "https://shopping-seller.toss.im/home",
        "id": os.environ.get("TOSS_ID", ""),
        "password": os.environ.get("TOSS_PW", ""),
    },
    {
        "scraper": WadizScraper,
        "name": "와디즈",
        "url": "https://www.wadiz.kr/web/main",
        "id": os.environ.get("WADIZ_ID", ""),
        "password": os.environ.get("WADIZ_PW", ""),
    },
    {
        "scraper": AliexpressScraper,
        "name": "알리익스프레스",
        "url": "https://sell.aliexpress.com",
        "id": os.environ.get("ALIEXPRESS_ID", ""),
        "password": os.environ.get("ALIEXPRESS_PW", ""),
        "manual": True,  # 보안 정책으로 자동 수집 불가 → 수동확인
    },
    {
        "scraper": OasisScraper,
        "name": "오아이스",
        "url": "https://www.oasis.co.kr:9886/order/seller/list",
        "id": os.environ.get("OASIS_ID", ""),
        "password": os.environ.get("OASIS_PW", ""),
    },
]


async def run_scraper(browser, channel_config):
    # 수동확인 채널은 스크래핑 없이 manual 상태로 반환
    if channel_config.get("manual"):
        print(f"[{channel_config['name']}] 수동확인 채널 — 스킵")
        return {
            "name": channel_config["name"],
            "url": channel_config["url"],
            "status": "manual",
            "error": None,
            "updated_at": datetime.now(KST).isoformat(),
            "summary": {"orders_new": 0, "inquiries_unanswered": 0, "reviews_unanswered": 0},
            "orders": [],
            "inquiries": [],
            "reviews": [],
        }

    ScraperClass = channel_config["scraper"]
    config = {
        "id": channel_config["id"],
        "password": channel_config["password"],
        "url": channel_config["url"],
    }
    scraper = ScraperClass(channel_config["name"], config)
    print(f"[{channel_config['name']}] 시작...")
    result = await scraper.scrape(browser)
    print(f"[{channel_config['name']}] 완료: {result['status']}")
    return result


async def main():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )

        # 채널별 순차 실행 (로그인 충돌 방지)
        for channel in CHANNELS:
            result = await run_scraper(browser, channel)
            results.append(result)

        await browser.close()

    output = {
        "updated_at": datetime.now(KST).isoformat(),
        "channels": results,
    }

    out_path = Path(__file__).parent / "data" / "results.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장 완료: {out_path}")
    print(f"수집 시각: {output['updated_at']}")

    ok = sum(1 for r in results if r["status"] == "ok")
    error = sum(1 for r in results if r["status"] == "error")
    print(f"성공: {ok}개 / 실패: {error}개")


if __name__ == "__main__":
    asyncio.run(main())
