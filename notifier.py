"""재고 부족 시 공급업체 이메일 자동 발송 모듈"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "우리식당")


def _get_supplier(category: str) -> tuple[str, str] | None:
    """카테고리에 해당하는 공급업체 (업체명, 이메일) 반환"""
    env_key = f"SUPPLIER_{category}"
    value = os.getenv(env_key, "")
    if not value or ":" not in value:
        return None
    name, email = value.split(":", 1)
    return name.strip(), email.strip()


def send_order_email(supplier_name: str, supplier_email: str, items: list[dict]) -> bool:
    """공급업체에 발주 이메일 발송"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"  [이메일 미설정] {supplier_name}({supplier_email})에게 발송할 내용:")
        for item in items:
            order_qty = item["max_stock"] - item["stock"]
            print(f"    - {item['name']}: {order_qty}{item['unit']} 주문 요청")
        return False

    now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    subject = f"[{SENDER_NAME}] 식자재 발주 요청 - {now}"

    rows = ""
    for item in items:
        order_qty = item["max_stock"] - item["stock"]
        rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ddd;">{item['name']}</td>
            <td style="padding:8px;border:1px solid #ddd;text-align:center;">{item['stock']}{item['unit']}</td>
            <td style="padding:8px;border:1px solid #ddd;text-align:center;">{item['ratio']}%</td>
            <td style="padding:8px;border:1px solid #ddd;text-align:center;color:#e53e3e;font-weight:bold;">{order_qty}{item['unit']}</td>
        </tr>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;">
    <h2 style="color:#2b6cb0;">📦 식자재 발주 요청</h2>
    <p>안녕하세요, <strong>{supplier_name}</strong> 담당자님.<br>
    <strong>{SENDER_NAME}</strong>에서 아래 식자재 발주를 요청드립니다.</p>

    <table style="border-collapse:collapse;width:100%;margin:16px 0;">
        <thead>
            <tr style="background:#2b6cb0;color:white;">
                <th style="padding:10px;border:1px solid #ddd;">식자재</th>
                <th style="padding:10px;border:1px solid #ddd;">현재 재고</th>
                <th style="padding:10px;border:1px solid #ddd;">재고율</th>
                <th style="padding:10px;border:1px solid #ddd;">주문 수량</th>
            </tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table>

    <p>빠른 납품 부탁드립니다. 감사합니다.<br><br>
    <strong>{SENDER_NAME}</strong><br>
    <small style="color:#888;">{now} 자동 발송</small></p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = supplier_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [supplier_email], msg.as_string())
        return True
    except Exception as e:
        print(f"  [이메일 발송 실패] {supplier_email}: {e}")
        return False


def send_daily_close_email(report: dict) -> bool:
    """하루 마감 리포트를 식당 관리자 이메일로 발송."""
    owner_email = os.getenv("OWNER_EMAIL", SMTP_USER)
    if not SMTP_USER or not SMTP_PASSWORD or not owner_email:
        print("[마감 리포트] 이메일 미설정 — 콘솔 출력:")
        print(f"  날짜: {report['date']}  매출: {report['total_revenue']:,}원  판매: {report['total_qty']}그릇")
        for name, d in report['ingredient_usage'].items():
            print(f"  {name}: {d['used']}{d['unit']} 사용 / 원가 {d['cost']:,}원")
        return False

    date_str = report["date"]
    total_revenue = report["total_revenue"]
    total_qty = report["total_qty"]
    total_cost = report["total_ingredient_cost"]
    margin = total_revenue - total_cost

    # 판매 현황 행
    sales_rows = "".join(
        f"<tr><td>{menu}</td><td>{d['qty']}그릇</td><td>{d['revenue']:,}원</td></tr>"
        for menu, d in report["sales"].items()
    ) or "<tr><td colspan='3' style='color:#aaa;text-align:center;'>판매 없음</td></tr>"

    # 식자재 사용량 행 (카테고리 정렬)
    usage_rows = "".join(
        f"<tr><td style='color:#888;font-size:0.85em;'>{d['category']}</td>"
        f"<td>{name}</td><td>{d['used']}{d['unit']}</td><td>{d['cost']:,}원</td></tr>"
        for name, d in sorted(report["ingredient_usage"].items(), key=lambda x: x[1]["category"])
    ) or "<tr><td colspan='4' style='color:#aaa;text-align:center;'>사용 없음</td></tr>"

    # 재고 부족 경고
    low = report.get("low_stock", [])
    low_html = ""
    if low:
        items_html = "".join(
            f"<li>{i['name']} — {i['ratio']}% 남음 ({i['stock']}{i['unit']})</li>"
            for i in low
        )
        low_html = f"""
        <div style="background:#fdecea;border-left:4px solid #e53e3e;padding:14px 18px;border-radius:6px;margin:16px 0;">
          <strong style="color:#c0392b;">⚠️ 자동 발주 대상 식자재 ({len(low)}개)</strong>
          <ul style="margin:8px 0 0 16px;color:#555;">{items_html}</ul>
        </div>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:620px;margin:0 auto;">
    <div style="background:linear-gradient(135deg,#2b6cb0,#1a4a7c);color:white;padding:24px;border-radius:12px 12px 0 0;">
      <h1 style="margin:0;font-size:1.4rem;">🍲 {SENDER_NAME} 일일 마감 리포트</h1>
      <p style="margin:6px 0 0;opacity:0.8;">{date_str} 오후 5시 자동 마감</p>
    </div>
    <div style="background:white;padding:24px;border:1px solid #e9ecef;border-top:none;">

      <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
        {_stat_box("💰 총 매출", f"{total_revenue:,}원", "#2b6cb0")}
        {_stat_box("🍜 총 판매", f"{total_qty}그릇", "#2d7a3e")}
        {_stat_box("🧾 식자재 원가", f"{total_cost:,}원", "#b07d00")}
        {_stat_box("📈 마진", f"{total_revenue and round(margin/total_revenue*100,1) or 0}%", "#6b46c1")}
      </div>

      <h3 style="border-bottom:2px solid #e9ecef;padding-bottom:8px;">판매 현황</h3>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <thead><tr style="background:#f8f9fa;">
          <th style="padding:9px;text-align:left;">메뉴</th>
          <th style="padding:9px;text-align:left;">수량</th>
          <th style="padding:9px;text-align:left;">매출</th>
        </tr></thead>
        <tbody>{sales_rows}</tbody>
      </table>

      <h3 style="border-bottom:2px solid #e9ecef;padding-bottom:8px;">식자재 사용량</h3>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <thead><tr style="background:#f8f9fa;">
          <th style="padding:9px;text-align:left;">분류</th>
          <th style="padding:9px;text-align:left;">식자재</th>
          <th style="padding:9px;text-align:left;">사용량</th>
          <th style="padding:9px;text-align:left;">원가</th>
        </tr></thead>
        <tbody>{usage_rows}</tbody>
        <tr style="background:#f8f9fa;font-weight:700;">
          <td colspan="3" style="padding:9px;">총 식자재 원가</td>
          <td style="padding:9px;">{total_cost:,}원</td>
        </tr>
      </table>

      {low_html}

      <p style="color:#aaa;font-size:0.8rem;margin-top:20px;">
        이 메일은 {SENDER_NAME} 재고관리 시스템이 매일 오후 5시에 자동 발송합니다.
      </p>
    </div>
    </body></html>
    """

    subject = f"[{SENDER_NAME}] {date_str} 일일 마감 리포트"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = owner_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [owner_email], msg.as_string())
        print(f"[마감 리포트] {owner_email} 발송 완료")
        return True
    except Exception as e:
        print(f"[마감 리포트 발송 실패] {e}")
        return False


def _stat_box(label: str, value: str, color: str) -> str:
    return f"""
    <div style="flex:1;min-width:120px;background:#f8f9fa;border-radius:8px;padding:14px;text-align:center;">
      <div style="font-size:0.75rem;color:#888;margin-bottom:4px;">{label}</div>
      <div style="font-size:1.2rem;font-weight:700;color:{color};">{value}</div>
    </div>"""


def notify_low_stock(low_stock_items: list[dict]) -> dict[str, list]:
    """
    재고 부족 식자재를 카테고리별로 묶어 공급업체에 발주 요청.
    Returns: {카테고리: [처리된 식자재 목록]}
    """
    from suppliers import save_order_log, get_suppliers_by_category

    if not low_stock_items:
        return {}

    # 카테고리별로 그룹화
    by_category: dict[str, list] = {}
    for item in low_stock_items:
        cat = item["category"]
        by_category.setdefault(cat, []).append(item)

    results = {}
    for category, items in by_category.items():
        # DB 공급업체 우선, 없으면 .env 폴백
        db_suppliers = get_suppliers_by_category(category)
        if db_suppliers:
            supplier_name = db_suppliers[0]["name"]
            supplier_email = db_suppliers[0].get("email", "")
        else:
            env_supplier = _get_supplier(category)
            if env_supplier:
                supplier_name, supplier_email = env_supplier
            else:
                supplier_name, supplier_email = "", ""

        if supplier_email:
            print(f"  → {category} 공급업체 '{supplier_name}'({supplier_email})에 발주 이메일 발송 중...")
            success = send_order_email(supplier_name, supplier_email, items)
            method = "email"
            if success:
                print(f"    ✓ 발송 완료")
        else:
            print(f"  [공급업체 미설정] 카테고리 '{category}' - 공급업체 관리에서 이메일을 등록하세요")
            method = "미발송"

        # 발주 로그 저장
        save_order_log(
            items=[{"name": i["name"], "unit": i["unit"],
                    "stock": i["stock"], "max_stock": i["max_stock"],
                    "order_qty": round(i["max_stock"] - i["stock"], 3),
                    "ratio": i["ratio"]}
                   for i in items],
            supplier_name=supplier_name,
            category=category,
            method=method,
        )
        results[category] = items

    return results
