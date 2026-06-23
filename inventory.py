"""재고 관리 및 원가 계산 모듈"""

import json
import os
from datetime import datetime
from data import INGREDIENTS, RECIPES

STOCK_FILE = "stock.json"
SALES_LOG_FILE = "sales_log.json"

LOW_STOCK_THRESHOLD = 0.20  # 20%


def load_stock() -> dict:
    """현재 재고를 파일에서 불러옵니다. 없으면 초기 데이터 사용."""
    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 초기 데이터에서 재고만 복사
    return {name: dict(info) for name, info in INGREDIENTS.items()}


def save_stock(stock: dict):
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(stock, f, ensure_ascii=False, indent=2)


def calc_cost(menu_name: str, stock: dict) -> dict:
    """메뉴 한 그릇의 식자재 원가를 계산합니다."""
    recipe = RECIPES.get(menu_name)
    if not recipe:
        raise ValueError(f"존재하지 않는 메뉴: {menu_name}")

    breakdown = {}
    total_cost = 0.0
    for ingredient, amount in recipe["ingredients"].items():
        info = stock[ingredient]
        cost = info["cost_per_unit"] * amount
        breakdown[ingredient] = {
            "amount": amount,
            "unit": info["unit"],
            "cost": round(cost),
        }
        total_cost += cost

    return {
        "menu": menu_name,
        "price": recipe["price"],
        "total_cost": round(total_cost),
        "margin": round(recipe["price"] - total_cost),
        "margin_rate": round((recipe["price"] - total_cost) / recipe["price"] * 100, 1),
        "breakdown": breakdown,
    }


def sell(menu_name: str, qty: int = 1) -> dict:
    """
    판매 처리: 재고 차감 후 재고 상태 반환.
    Returns: {cost_info, low_stock_items}
    """
    recipe = RECIPES.get(menu_name)
    if not recipe:
        raise ValueError(f"존재하지 않는 메뉴: {menu_name}")

    stock = load_stock()

    # 재고 충분 여부 확인
    for ingredient, amount in recipe["ingredients"].items():
        required = amount * qty
        if stock[ingredient]["stock"] < required:
            raise ValueError(
                f"재고 부족: {ingredient} (필요 {required}{stock[ingredient]['unit']}, "
                f"현재 {stock[ingredient]['stock']}{stock[ingredient]['unit']})"
            )

    # 재고 차감
    for ingredient, amount in recipe["ingredients"].items():
        stock[ingredient]["stock"] -= amount * qty

    save_stock(stock)
    _log_sale(menu_name, qty)

    cost_info = calc_cost(menu_name, stock)
    low_stock = check_low_stock(stock)

    return {"cost_info": cost_info, "low_stock_items": low_stock}


def check_low_stock(stock: dict = None) -> list[dict]:
    """재고가 20% 이하인 식자재 목록을 반환합니다."""
    if stock is None:
        stock = load_stock()

    low = []
    for name, info in stock.items():
        max_stock = info.get("max_stock", INGREDIENTS[name]["max_stock"])
        ratio = info["stock"] / max_stock
        if ratio <= LOW_STOCK_THRESHOLD:
            low.append({
                "name": name,
                "stock": info["stock"],
                "max_stock": max_stock,
                "unit": info["unit"],
                "ratio": round(ratio * 100, 1),
                "category": info.get("category", INGREDIENTS[name]["category"]),
            })
    return low


def get_stock_summary(stock: dict = None) -> list[dict]:
    """전체 재고 현황 요약을 반환합니다."""
    if stock is None:
        stock = load_stock()
    summary = []
    for name, info in stock.items():
        max_stock = info.get("max_stock", INGREDIENTS[name]["max_stock"])
        ratio = info["stock"] / max_stock * 100
        status = "🔴 긴급" if ratio <= 20 else ("🟡 주의" if ratio <= 40 else "🟢 정상")
        summary.append({
            "name": name,
            "stock": info["stock"],
            "max_stock": max_stock,
            "unit": info["unit"],
            "ratio": round(ratio, 1),
            "status": status,
            "category": info.get("category", INGREDIENTS[name].get("category", "")),
        })
    return summary


def restock(ingredient: str, amount: float):
    """식자재 재고를 보충합니다."""
    stock = load_stock()
    if ingredient not in stock:
        raise ValueError(f"존재하지 않는 식자재: {ingredient}")
    stock[ingredient]["stock"] = min(
        stock[ingredient]["stock"] + amount,
        stock[ingredient].get("max_stock", INGREDIENTS[ingredient]["max_stock"])
    )
    save_stock(stock)


def _log_sale(menu_name: str, qty: int):
    logs = []
    if os.path.exists(SALES_LOG_FILE):
        with open(SALES_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "menu": menu_name,
        "qty": qty,
        "price": RECIPES[menu_name]["price"] * qty,
    })
    with open(SALES_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def get_sales_summary() -> dict:
    """오늘의 판매 요약을 반환합니다."""
    if not os.path.exists(SALES_LOG_FILE):
        return {}
    with open(SALES_LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)

    today = datetime.now().date().isoformat()
    today_logs = [l for l in logs if l["timestamp"].startswith(today)]

    summary = {}
    for log in today_logs:
        menu = log["menu"]
        if menu not in summary:
            summary[menu] = {"qty": 0, "revenue": 0}
        summary[menu]["qty"] += log["qty"]
        summary[menu]["revenue"] += log["price"]
    return summary
