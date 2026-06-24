"""Flask 웹 대시보드 + 오후 5시 자동 마감 스케줄러 + 로그인/회원 관리"""

import os
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, jsonify, request,
                   redirect, url_for, session, flash)
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from inventory import (
    calc_cost, sell, check_low_stock, get_stock_summary,
    restock, get_sales_summary, get_daily_usage_report, load_stock
)
from notifier import notify_low_stock, send_daily_close_email
from excel_handler import (generate_template, parse_upload,
                           apply_receive, get_receive_logs)
from auth import (init_admin, login as auth_login, register as auth_register,
                  approve_user, reject_user, delete_user,
                  get_pending_users, get_all_staff, change_password)
from data import RECIPES

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())

# 최초 실행 시 관리자 계정 생성
init_admin()

_last_close: dict = {}


# ── 인증 데코레이터 ────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        if session.get("role") != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ── 인증 라우트 ───────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        result = auth_login(username, password)
        if result is None:
            return render_template("login.html", error="invalid")
        if isinstance(result, dict) and "error" in result:
            return render_template("login.html", error=result["error"])
        session["user_id"] = result["id"]
        session["username"] = result["username"]
        session["name"] = result["name"]
        session["role"] = result["role"]
        return redirect(url_for("index"))
    return render_template("login.html", error=None)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not name or not username or not password:
        return render_template("login.html", reg_error="모든 항목을 입력해주세요.")
    result = auth_register(username, password, name)
    if "error" in result:
        return render_template("login.html", reg_error=result["error"])
    return render_template("login.html", reg_success=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── 식자재 입고 ───────────────────────────────────────

@app.route("/receive")
@login_required
def receive_page():
    try:
        logs = get_receive_logs()
    except Exception:
        logs = []
    return render_template("receive.html", logs=logs)


@app.route("/receive/template")
@login_required
def receive_template():
    from flask import send_file
    category = request.args.get("category", "")
    supplier = request.args.get("supplier", "")
    buf = generate_template(supplier_name=supplier, category=category)
    filename = f"입고명세서_{category or '전체'}_{supplier or '한씨막국수'}.xlsx"
    return send_file(buf, as_attachment=True,
                     download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/receive/preview", methods=["POST"])
@login_required
def receive_preview():
    if "file" not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    f = request.files["file"]
    try:
        parsed = parse_upload(f.stream)
        # 카테고리 정보 추가
        from data import INGREDIENTS
        for item in parsed["items"]:
            item["category"] = INGREDIENTS.get(item["name"], {}).get("category", "")
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/receive/apply", methods=["POST"])
@login_required
def receive_apply():
    data = request.get_json()
    memo = data.pop("memo", "")
    try:
        result = apply_receive(data, memo=memo)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ── 관리자 — 직원 관리 ────────────────────────────────

@app.route("/admin/users")
@admin_required
def admin_users():
    flash_msg = session.pop("flash", None)
    return render_template("admin_users.html",
                           pending=get_pending_users(),
                           staff=get_all_staff(),
                           flash=flash_msg,
                           pw_error=None, pw_success=False)


@app.route("/admin/users/approve/<int:user_id>", methods=["POST"])
@admin_required
def admin_approve(user_id):
    approve_user(user_id)
    session["flash"] = "✓ 승인이 완료됐습니다."
    return redirect(url_for("admin_users"))


@app.route("/admin/users/reject/<int:user_id>", methods=["POST"])
@admin_required
def admin_reject(user_id):
    reject_user(user_id)
    session["flash"] = "계정이 거절(정지) 처리됐습니다."
    return redirect(url_for("admin_users"))


@app.route("/admin/users/delete/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete(user_id):
    delete_user(user_id)
    session["flash"] = "계정이 삭제됐습니다."
    return redirect(url_for("admin_users"))


@app.route("/admin/change-password", methods=["POST"])
@admin_required
def admin_change_password():
    current = request.form.get("current_password", "")
    new_pw  = request.form.get("new_password", "")
    new_pw2 = request.form.get("new_password2", "")
    if new_pw != new_pw2:
        return render_template("admin_users.html",
                               pending=get_pending_users(), staff=get_all_staff(),
                               flash=None, pw_error="새 비밀번호가 일치하지 않습니다.")
    result = change_password(session["user_id"], current, new_pw)
    if "error" in result:
        return render_template("admin_users.html",
                               pending=get_pending_users(), staff=get_all_staff(),
                               flash=None, pw_error=result["error"])
    return render_template("admin_users.html",
                           pending=get_pending_users(), staff=get_all_staff(),
                           flash=None, pw_success=True)


# ── 메인 대시보드 ─────────────────────────────────────

@app.route("/")
@login_required
def index():
    pending_count = len(get_pending_users()) if session.get("role") == "admin" else 0
    return render_template("index.html",
                           user_name=session.get("name"),
                           user_role=session.get("role"),
                           pending_count=pending_count)


# ── API ──────────────────────────────────────────────

@app.route("/api/stock")
@login_required
def api_stock():
    return jsonify(get_stock_summary())


@app.route("/api/costs")
@login_required
def api_costs():
    stock = load_stock()
    return jsonify({name: calc_cost(name, stock) for name in RECIPES})


@app.route("/api/sales")
@login_required
def api_sales():
    return jsonify(get_sales_summary())


@app.route("/api/sell", methods=["POST"])
@login_required
def api_sell():
    data = request.get_json()
    try:
        result = sell(data.get("menu", ""), int(data.get("qty", 1)))
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/restock", methods=["POST"])
@login_required
def api_restock():
    data = request.get_json()
    try:
        restock(data.get("ingredient", ""), float(data.get("amount", 0)))
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/order", methods=["POST"])
@login_required
def api_order():
    low = check_low_stock()
    if not low:
        return jsonify({"sent": False, "message": "재고 부족 없음"})
    notify_low_stock(low)
    return jsonify({"sent": True, "categories": list({i["category"] for i in low})})


@app.route("/api/close", methods=["POST"])
@admin_required
def api_close():
    daily_close_job()
    return jsonify({"ok": True, "result": _last_close})


@app.route("/api/close/report")
@login_required
def api_close_report():
    return jsonify(get_daily_usage_report())


@app.route("/api/schedule")
@login_required
def api_schedule():
    job = scheduler.get_job("daily_close")
    next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M") if job and job.next_run_time else "-"
    return jsonify({
        "close_time": f"{CLOSE_HOUR:02d}:{CLOSE_MIN:02d}",
        "next_run": next_run,
        "last_close": _last_close,
    })


# ── 스케줄러 ──────────────────────────────────────────

def daily_close_job():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 일일 마감 작업 시작")
    report = get_daily_usage_report()
    send_daily_close_email(report)
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


CLOSE_HOUR = int(os.getenv("CLOSE_HOUR", 17))
CLOSE_MIN  = int(os.getenv("CLOSE_MIN", 0))

scheduler = BackgroundScheduler(timezone="Asia/Seoul")
scheduler.add_job(daily_close_job, trigger="cron",
                  hour=CLOSE_HOUR, minute=CLOSE_MIN, id="daily_close")
scheduler.start()
print(f"✓ 자동 마감 스케줄 등록: 매일 {CLOSE_HOUR:02d}:{CLOSE_MIN:02d}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
