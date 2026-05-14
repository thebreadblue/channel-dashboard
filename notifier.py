"""
Google Chat 일일 요약 알림 (매일 14:00 KST)
- 전체 채널 항상 발송
- 이전 스냅샷 대비 숫자가 바뀐 채널은 변동 표시
"""
import json
import os
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
RESULTS_PATH = Path("data/results.json")
SNAPSHOT_PATH = Path("data/snapshot.json")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_summary(data) -> dict:
    """채널별 summary dict"""
    channels = data if isinstance(data, list) else data.get("channels", [])
    return {
        ch["name"]: {
            "orders_new": ch["summary"].get("orders_new", 0),
            "inquiries_unanswered": ch["summary"].get("inquiries_unanswered", 0),
            "reviews_unanswered": ch["summary"].get("reviews_unanswered", 0),
            "status": ch.get("status", "ok"),
        }
        for ch in channels
        if isinstance(ch, dict)
    }


def build_message(current: dict, previous: dict, now_str: str) -> str:
    lines = [f"📊 판매채널 요약 리포트 ({now_str})\n"]
    for name, s in current.items():
        if s["status"] != "ok":
            lines.append(f"*{name}*")
            lines.append("⚠️ 수집 오류 — 어드민에서 직접 확인")
            lines.append("")
            continue

        prev = previous.get(name, {})
        changed = s != prev and bool(prev)

        changed_mark = " 🔔" if changed else ""
        lines.append(f"*{name}*{changed_mark}")
        lines.append(
            f"신규주문 {s['orders_new']}, "
            f"미답변 문의 {s['inquiries_unanswered']}, "
            f"미답변 리뷰 {s['reviews_unanswered']}"
        )
        lines.append("")
    return "\n".join(lines).strip()


def send_google_chat(webhook_url: str, text: str):
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status


def main():
    webhook_url = os.environ.get("GOOGLE_CHAT_WEBHOOK")
    if not webhook_url:
        print("GOOGLE_CHAT_WEBHOOK 환경변수 없음 — 알림 스킵")
        return

    current_data = load_json(RESULTS_PATH)
    if not current_data:
        print(f"{RESULTS_PATH} 없음 — 알림 스킵")
        return

    current = build_summary(current_data)
    previous_data = load_json(SNAPSHOT_PATH)
    previous = build_summary(previous_data) if previous_data else {}

    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    message = build_message(current, previous, now_str)

    status = send_google_chat(webhook_url, message)
    print(f"[{now_str}] Google Chat 발송 완료 (HTTP {status})")
    print(message)

    # 현재 상태를 다음 비교 기준으로 저장
    SNAPSHOT_PATH.write_text(
        json.dumps(current_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"스냅샷 업데이트: {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
