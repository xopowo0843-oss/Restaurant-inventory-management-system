"""Flask 웹 대시보드 + 오후 5시 자동 마감 스케줄러"""

import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from inventory import (
    calc_cost, sell, check_low_stock, get_stock_summary,
    restock, get_sales_summary, get_daily_usage_report, load_stock
)
from notifier import notify_low_stock, send_daily_close_email
from data import RECIPES

load_dotenv()
app = Flask(__name__)

# 마지막 마감 실행 결과를 메모리에 보관 (재시작 전까지)
_last_close: dict = {}


def daily_close_job():
    """매일 오후 5시 자동 실행: 마감 리포트 발송 + 재고 부족 자동 발주"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 일일 마감 작업 시작")

    report = get_daily_usage_report()

    # 1) 관리자에게 마감 리포트 이메일
    send_daily_close_email(report)

    # 2) 재고 부족 품목 공급업체 자동 발주
    if report["low_stock"]:
        print(f"  재고 부족 {len(report['low_stock'])}개 → 발주 진행")
        notify_low_stock(report["low_stock"])
    else:
        print("  재고 부족 없음 — 발주 생략")

    global _last_close
    _last_close = {
        "date": report["date"],
        "ran_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_revenue": report["total_revenue"],
        "total_qty": report["total_qty"],
        "low_count": len(report["low_stock"]),
    }
    print("[마감 완료]\n")


# ── 스케줄러 설정 ─────────────────────────────────────
CLOSE_HOUR = int(os.getenv("CLOSE_HOUR", 17))   # 기본 오후 5시
CLOSE_MIN  = int(os.getenv("CLOSE_MIN", 0))

scheduler = BackgroundScheduler(timezone="Asia/Seoul")
scheduler.add_job(
    daily_close_job,
    trigger="cron",
    hour=CLOSE_HOUR,
    minute=CLOSE_MIN,
    id="daily_close",
)
scheduler.start()
print(f"✓ 자동 마감 스케줄 등록: 매일 {CLOSE_HOUR:02d}:{CLOSE_MIN:02d}")


# ── API ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stock")
def api_stock():
    return jsonify(get_stock_summary())


@app.route("/api/costs")
def api_costs():
    stock = load_stock()
    return jsonify({name: calc_cost(name, stock) for name in RECIPES})


@app.route("/api/sales")
def api_sales():
    return jsonify(get_sales_summary())


@app.route("/api/sell", methods=["POST"])
def api_sell():
    data = request.get_json()
    try:
        result = sell(data.get("menu", ""), int(data.get("qty", 1)))
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/restock", methods=["POST"])
def api_restock():
    data = request.get_json()
    try:
        restock(data.get("ingredient", ""), float(data.get("amount", 0)))
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/order", methods=["POST"])
def api_order():
    """수동 발주 (웹에서 즉시 발송)"""
    low = check_low_stock()
    if not low:
        return jsonify({"sent": False, "message": "재고 부족 없음"})
    notify_low_stock(low)
    return jsonify({"sent": True, "categories": list({i["category"] for i in low})})


@app.route("/api/close", methods=["POST"])
def api_close():
    """수동 마감 처리 (테스트 또는 조기 마감 시 사용)"""
    daily_close_job()
    return jsonify({"ok": True, "result": _last_close})


@app.route("/api/close/report")
def api_close_report():
    """오늘 마감 리포트 데이터 (화면 표시용)"""
    report = get_daily_usage_report()
    return jsonify(report)


@app.route("/api/schedule")
def api_schedule():
    """스케줄 정보 반환"""
    job = scheduler.get_job("daily_close")
    next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M") if job and job.next_run_time else "-"
    return jsonify({
        "close_time": f"{CLOSE_HOUR:02d}:{CLOSE_MIN:02d}",
        "next_run": next_run,
        "last_close": _last_close,
    })


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
