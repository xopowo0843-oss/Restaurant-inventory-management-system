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


def notify_low_stock(low_stock_items: list[dict]) -> dict[str, list]:
    """
    재고 부족 식자재를 카테고리별로 묶어 공급업체에 발주 요청.
    Returns: {카테고리: [처리된 식자재 목록]}
    """
    if not low_stock_items:
        return {}

    # 카테고리별로 그룹화
    by_category: dict[str, list] = {}
    for item in low_stock_items:
        cat = item["category"]
        by_category.setdefault(cat, []).append(item)

    results = {}
    for category, items in by_category.items():
        supplier = _get_supplier(category)
        if not supplier:
            print(f"  [공급업체 미설정] 카테고리 '{category}' - .env에 SUPPLIER_{category} 설정 필요")
            results[category] = items
            continue

        supplier_name, supplier_email = supplier
        print(f"  → {category} 공급업체 '{supplier_name}'({supplier_email})에 발주 이메일 발송 중...")
        success = send_order_email(supplier_name, supplier_email, items)
        if success:
            print(f"    ✓ 발송 완료")
        results[category] = items

    return results
