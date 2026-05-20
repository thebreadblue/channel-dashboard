#!/usr/bin/env python3
"""
채널별 세션 쿠키 추출기 — 로컬에서 1회 실행
출력된 값을 GitHub Secret에 저장하면 Actions에서 쿠키로 로그인

사용법:
  python export_cookies.py smartstore
  python export_cookies.py kakao
  python export_cookies.py toss
  python export_cookies.py eleven
  python export_cookies.py gmarket
  python export_cookies.py ali
  python export_cookies.py baemin
  python export_cookies.py kurly
"""
import asyncio
import json
import base64
import sys
from playwright.async_api import async_playwright

CHANNELS = {
    "smartstore": ("https://sell.smartstore.naver.com", "SMARTSTORE_COOKIES"),
    "kakao":       ("https://shopping-sell.kakao.com/hub", "KAKAO_COOKIES"),
    "toss":        ("https://shopping-seller.toss.im", "TOSS_COOKIES"),
    "eleven":      ("http://soffice.11st.co.kr/view/main", "ELEVEN_COOKIES"),
    "gmarket":     ("https://www.esmplus.com/Home", "GMARKET_COOKIES"),
    "ali":         ("https://sell.aliexpress.com", "ALI_COOKIES"),
    "baemin":      ("https://scm-mart.baemin.com", "BAEMIN_COOKIES"),
    "kurly":       ("https://partner.kurly.com", "KURLY_COOKIES"),
}

async def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CHANNELS:
        print(f"사용법: python export_cookies.py <채널>")
        print(f"채널 목록: {', '.join(CHANNELS.keys())}")
        return

    name = sys.argv[1]
    url, secret_name = CHANNELS[name]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="ko-KR", timezone_id="Asia/Seoul")
        page = await context.new_page()

        await page.goto(url)
        print(f"\n[{name}] 브라우저에서 직접 로그인하세요.")
        print("로그인 완료 후 여기서 Enter를 누르세요...")
        input()

        cookies = await context.cookies()
        encoded = base64.b64encode(
            json.dumps(cookies, ensure_ascii=False).encode()
        ).decode()

        print(f"\n아래 값을 GitHub → Settings → Secrets → Actions → '{secret_name}' 에 저장:\n")
        print("=" * 60)
        print(encoded)
        print("=" * 60)
        print(f"\n총 {len(cookies)}개 쿠키 추출 완료.")
        await browser.close()

asyncio.run(main())
