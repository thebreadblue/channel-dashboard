# 더브레드블루 채널 대시보드 — 프로젝트 정리

> 마지막 업데이트: 2026-05-20

---

## 개요

9개 판매채널의 신규주문 / 미답변 문의 / 미답변 리뷰를 자동으로 수집해서 웹 대시보드에 표시하고, 매일 오후 2시에 구글챗으로 요약 알림을 보내는 시스템.

---

## 구성 요소

```
channel-dashboard/
├── main.py                  # 스크래퍼 실행 진입점
├── notifier.py              # 구글챗 알림 발송
├── export_cookies.py        # 채널별 로컬 쿠키 추출 스크립트
├── scrapers/
│   ├── base.py              # 공통 베이스 (login, count_from_page 등)
│   ├── smartstore.py
│   ├── kakao.py
│   ├── toss.py
│   ├── eleven.py
│   ├── gmarket.py
│   ├── aliexpress.py
│   ├── baemin.py
│   ├── coupang.py
│   └── kurly.py
├── frontend/                # Next.js 대시보드
│   ├── app/
│   ├── components/
│   │   ├── ChannelStatusGrid.tsx   # 채널별 당일 현황 (실제 데이터 연결)
│   │   ├── MonthlySummary.tsx      # 당월 KPI (현재 목업 데이터)
│   │   └── BulkOrderLinks.tsx     # 대량주문 퀵링크
│   ├── constants/omsMockData.ts
│   └── lib/fetchChannelData.ts    # results.json fetch & 매핑
├── data/
│   └── results.json         # 스크래퍼 수집 결과 (GitHub에 커밋됨)
└── .github/workflows/
    ├── scrape.yml           # 1시간마다 스크래퍼 실행
    ├── notify.yml           # 매일 14:00 KST 구글챗 알림
    └── deploy-frontend.yml  # Next.js → GitHub Pages 배포
```

---

## 채널 현황

| 채널 | 로그인 URL | ID Secret | PW Secret | 로그인 상태 |
|------|-----------|-----------|-----------|------------|
| 스마트스토어 | sell.smartstore.naver.com | `SMARTSTORE_ID` | `SMARTSTORE_PW` | ❌ 차단 (Naver 봇 차단) |
| 카카오쇼핑 | shopping-sell.kakao.com | `KAKAO_ID` | `KAKAO_PW` | ⚠️ 미확인 |
| 토스쇼핑 | shopping-seller.toss.im | `TOSS_ID` | `TOSS_PW` | ⚠️ 미확인 |
| 11번가 | soffice.11st.co.kr | `ELEVEN_ID` | `ELEVEN_PW` | ✅ 작동 중 |
| G마켓(ESM+) | esmplus.com | `GMARKET_ID` | `GMARKET_PW` | ⚠️ 미확인 |
| 알리익스프레스 | sell.aliexpress.com | `ALIEXPRESS_ID` | `ALIEXPRESS_PW` | ⚠️ 미확인 |
| 배민 | scm-mart.baemin.com | `BAEMIN_ID` | `BAEMIN_PW` | ⚠️ 미확인 |
| 쿠팡 | wing.coupang.com | `COUPANG_ID` | `COUPANG_PW` | ❌ WAF 영구 차단 |
| 컬리 | partner.kurly.com | `KURLY_ID` | `KURLY_PW` | ❌ 로그인 실패 |

---

## GitHub Actions Secrets 목록

GitHub → Settings → Secrets and variables → Actions 에서 관리.

### 채널 ID/PW
```
SMARTSTORE_ID / SMARTSTORE_PW
KAKAO_ID / KAKAO_PW
TOSS_ID / TOSS_PW
ELEVEN_ID / ELEVEN_PW
GMARKET_ID / GMARKET_PW
ALIEXPRESS_ID / ALIEXPRESS_PW
BAEMIN_ID / BAEMIN_PW
COUPANG_ID / COUPANG_PW
KURLY_ID / KURLY_PW
```

### 알림
```
GOOGLE_CHAT_WEBHOOK    # 구글챗 웹훅 URL
```

### 쿠키 (추가 예정)
```
SMARTSTORE_COOKIES     # 스마트스토어 세션 쿠키 (base64)
KAKAO_COOKIES
TOSS_COOKIES
ELEVEN_COOKIES
GMARKET_COOKIES
ALI_COOKIES
BAEMIN_COOKIES
KURLY_COOKIES
```

---

## 자동화 스케줄

| 워크플로우 | 스케줄 | 설명 |
|-----------|--------|------|
| `scrape.yml` | 매시간 (cron) | 9개 채널 순차 스크래핑 → `data/results.json` 커밋 |
| `notify.yml` | 매일 14:00 KST (05:00 UTC) | results.json 읽어서 구글챗으로 요약 알림 |
| `deploy-frontend.yml` | main 푸시 시 | Next.js 빌드 → GitHub Pages 배포 |

---

## 대시보드

- **URL**: https://thebreadblue.github.io/channel-dashboard/
- **프레임워크**: Next.js 16 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **배포**: GitHub Pages (static export)

### 섹션별 데이터 상태
| 섹션 | 데이터 | 상태 |
|------|--------|------|
| 채널별 당일 현황 | GitHub raw URL에서 results.json fetch | ✅ 실제 데이터 |
| 당월 전체 채널 지표 | omsMockData.ts | ⚠️ 목업 데이터 (미연결) |
| 대량주문 퀵링크 | omsMockData.ts (정적) | ✅ 정상 |

---

## 알려진 이슈 및 제약

### 1. GitHub Actions IP 차단 (핵심 문제)
GitHub Actions는 미국 서버에서 실행됨. 한국 쇼핑몰 상당수가 해외 IP + 헤드리스 브라우저를 봇으로 인식해 로그인을 차단하거나 홈으로 리다이렉트함.

**현상**: `status: ok`로 표시되지만 실제로는 로그인 페이지(홈)에 머물러 있어 수치가 0으로 수집됨.

**확인된 사례**: 스마트스토어 로그 → URL이 `#/home/about`(미로그인 랜딩)에 머무름.

**해결책**: 쿠키 인증 방식 (아래 참조)

### 2. 쿠팡 WAF 영구 차단
Akamai WAF가 GitHub Actions IP를 영구 차단. 스크래핑 불가. 추후 쿠팡 Wing API 연동 예정.

### 3. 카운트 수집 방식
CSS 셀렉터가 실패할 경우 → 페이지 텍스트에서 `총 N건` 패턴 매칭 → tbody 행 수 카운트 순으로 시도. SPA 특성상 정확도 한계 있음.

### 4. 당월 KPI 목업
MonthlySummary 컴포넌트가 아직 실제 데이터에 연결되지 않음. omsMockData.ts의 하드코딩된 수치 표시 중.

---

## 쿠키 인증 설정 방법 (로그인 차단 우회)

GitHub Actions에서 로그인이 막히는 채널은 로컬에서 쿠키를 추출해 GitHub Secret에 저장하면 해결됨.

### 1단계 — 쿠키 추출 (채널별로 반복)

```bash
cd /Users/rora/Desktop/channel-dashboard

python export_cookies.py smartstore   # 스마트스토어
python export_cookies.py kakao        # 카카오
python export_cookies.py toss         # 토스
python export_cookies.py eleven       # 11번가
python export_cookies.py gmarket      # G마켓
python export_cookies.py ali          # 알리익스프레스
python export_cookies.py baemin       # 배민
python export_cookies.py kurly        # 컬리
```

각 명령어 실행 시:
1. 브라우저가 열림
2. 해당 채널에 **직접 로그인**
3. 터미널로 돌아와 **Enter**
4. 출력된 긴 문자열 복사

### 2단계 — GitHub Secret 저장

GitHub → `thebreadblue/channel-dashboard` → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| 채널 | Secret 이름 |
|------|------------|
| 스마트스토어 | `SMARTSTORE_COOKIES` |
| 카카오 | `KAKAO_COOKIES` |
| 토스 | `TOSS_COOKIES` |
| 11번가 | `ELEVEN_COOKIES` |
| G마켓 | `GMARKET_COOKIES` |
| 알리익스프레스 | `ALI_COOKIES` |
| 배민 | `BAEMIN_COOKIES` |
| 컬리 | `KURLY_COOKIES` |

### 쿠키 유효기간
대부분 **수주~수개월**. 만료되면 Actions 로그에 "쿠키 만료" 메시지 출력 후 ID/PW 로그인으로 폴백.

---

## 향후 작업 목록

- [ ] 전체 채널에 쿠키 인증 코드 추가 (현재 스마트스토어만 구현)
- [ ] 당월 KPI를 실제 데이터로 연결 (또는 섹션 제거)
- [ ] 쿠팡 Wing API 연동
- [ ] 쿠키 만료 감지 시 슬랙/구글챗 알림
- [ ] 로컬 실행 방식 전환 검토 (GitHub Actions IP 차단 근본 해결)
