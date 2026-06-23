"""
식당 재고관리 시스템 - 메인 CLI
사용법: python main.py
"""

from inventory import (
    calc_cost, sell, check_low_stock, get_stock_summary,
    restock, get_sales_summary, load_stock
)
from notifier import notify_low_stock
from data import RECIPES


def print_separator(char="─", width=55):
    print(char * width)


def show_menu_costs():
    """메뉴별 원가 분석 출력"""
    stock = load_stock()
    print_separator("═")
    print("  📊 메뉴별 식자재 원가 분석")
    print_separator("═")
    for menu_name in RECIPES:
        info = calc_cost(menu_name, stock)
        print(f"\n  【{info['menu']}】 판매가: {info['price']:,}원")
        print(f"  {'식자재':<10} {'사용량':>8}  {'원가':>8}")
        print_separator()
        for ing, detail in info["breakdown"].items():
            print(f"  {ing:<10} {detail['amount']:>6}{detail['unit']}  {detail['cost']:>6,}원")
        print_separator()
        print(f"  {'총 원가':<10} {'':>8}  {info['total_cost']:>6,}원")
        print(f"  {'마진':<10} {'':>8}  {info['margin']:>6,}원  ({info['margin_rate']}%)")


def show_stock():
    """전체 재고 현황 출력"""
    summary = get_stock_summary()
    print_separator("═")
    print("  📦 현재 재고 현황")
    print_separator("═")
    print(f"  {'식자재':<10} {'현재고':>8} {'최대':>8} {'재고율':>7}  상태")
    print_separator()
    current_cat = ""
    for item in sorted(summary, key=lambda x: x["category"]):
        if item["category"] != current_cat:
            current_cat = item["category"]
            print(f"\n  [{current_cat}]")
        print(
            f"  {item['name']:<10} {item['stock']:>6}{item['unit']:<2} "
            f"{item['max_stock']:>6}{item['unit']:<2} {item['ratio']:>5}%  {item['status']}"
        )


def process_sale():
    """판매 처리 메뉴"""
    print_separator()
    print("  판매할 메뉴를 선택하세요:")
    menu_list = list(RECIPES.keys())
    for i, name in enumerate(menu_list, 1):
        print(f"  {i}. {name} ({RECIPES[name]['price']:,}원)")
    print_separator()

    try:
        choice = int(input("  번호 입력: ").strip())
        if not 1 <= choice <= len(menu_list):
            print("  올바른 번호를 입력하세요.")
            return
        menu_name = menu_list[choice - 1]
        qty = int(input(f"  판매 수량 (기본 1): ").strip() or "1")
    except ValueError:
        print("  숫자를 입력하세요.")
        return

    print(f"\n  [{menu_name} {qty}그릇] 판매 처리 중...")
    try:
        result = sell(menu_name, qty)
        cost = result["cost_info"]
        print(f"  ✓ 판매 완료!")
        print(f"    매출: {cost['price'] * qty:,}원  |  원가: {cost['total_cost'] * qty:,}원  |  마진: {cost['margin'] * qty:,}원")

        low = result["low_stock_items"]
        if low:
            print(f"\n  ⚠️  재고 부족 경고! ({len(low)}개 식자재)")
            for item in low:
                print(f"    - {item['name']}: {item['ratio']}% 남음")
            print()
            answer = input("  공급업체에 자동 발주 이메일을 보낼까요? (y/n): ").strip().lower()
            if answer == "y":
                notify_low_stock(low)
    except ValueError as e:
        print(f"  ❌ 오류: {e}")


def process_restock():
    """재고 보충"""
    stock = load_stock()
    print_separator()
    print("  보충할 식자재를 선택하세요:")
    names = list(stock.keys())
    for i, name in enumerate(names, 1):
        info = stock[name]
        print(f"  {i:2}. {name:<10} 현재: {info['stock']}{info['unit']}")
    print_separator()
    try:
        choice = int(input("  번호 입력: ").strip())
        if not 1 <= choice <= len(names):
            print("  올바른 번호를 입력하세요.")
            return
        name = names[choice - 1]
        amount = float(input(f"  보충량 ({stock[name]['unit']}): ").strip())
        restock(name, amount)
        print(f"  ✓ {name} {amount}{stock[name]['unit']} 보충 완료!")
    except ValueError as e:
        print(f"  ❌ 오류: {e}")


def show_sales_summary():
    """오늘의 판매 요약"""
    summary = get_sales_summary()
    print_separator("═")
    print("  💰 오늘의 판매 현황")
    print_separator("═")
    if not summary:
        print("  오늘 판매 기록이 없습니다.")
        return
    total_revenue = 0
    print(f"  {'메뉴':<12} {'판매수':>6}  {'매출':>10}")
    print_separator()
    for menu, data in summary.items():
        print(f"  {menu:<12} {data['qty']:>5}그릇  {data['revenue']:>8,}원")
        total_revenue += data["revenue"]
    print_separator()
    print(f"  {'합계':<12} {'':>6}  {total_revenue:>8,}원")


def check_and_notify():
    """재고 점검 후 부족 시 자동 발주"""
    low = check_low_stock()
    if not low:
        print("  ✓ 모든 식자재 재고가 충분합니다.")
        return
    print(f"\n  ⚠️  재고 부족 식자재 {len(low)}개 발견:")
    for item in low:
        print(f"    - {item['name']} ({item['category']}): {item['ratio']}% 남음")
    print()
    answer = input("  공급업체에 발주 이메일을 발송할까요? (y/n): ").strip().lower()
    if answer == "y":
        notify_low_stock(low)


def main():
    print("\n" + "═" * 55)
    print("     🍲 식당 재고관리 시스템")
    print("═" * 55)

    while True:
        print("\n  1. 메뉴별 원가 분석")
        print("  2. 재고 현황 보기")
        print("  3. 판매 처리")
        print("  4. 재고 보충")
        print("  5. 오늘 판매 현황")
        print("  6. 재고 점검 및 자동 발주")
        print("  0. 종료")
        print_separator()

        choice = input("  선택: ").strip()
        print()

        if choice == "1":
            show_menu_costs()
        elif choice == "2":
            show_stock()
        elif choice == "3":
            process_sale()
        elif choice == "4":
            process_restock()
        elif choice == "5":
            show_sales_summary()
        elif choice == "6":
            check_and_notify()
        elif choice == "0":
            print("  종료합니다.\n")
            break
        else:
            print("  올바른 번호를 입력하세요.")


if __name__ == "__main__":
    main()
