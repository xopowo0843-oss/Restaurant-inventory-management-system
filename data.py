"""
초기 데이터: 메뉴, 식자재, 레시피(메뉴별 소요 식자재)
실제 운영 시 이 파일을 수정하거나 JSON/DB로 교체 가능합니다.
"""

# 식자재 재고 현황
# 단위: g(그램), ml(밀리리터), 개
# max_stock: 최대 재고량 (발주 기준)
INGREDIENTS = {
    # cost_per_unit: 단위(g/ml/개)당 원가(원)
    # 예: 돼지고기 1kg=18,000원 → 1g=18원
    "소뼈":        {"stock": 10000, "max_stock": 10000, "unit": "g",  "cost_per_unit": 5,    "category": "육류"},
    "돼지고기":    {"stock": 5000,  "max_stock": 5000,  "unit": "g",  "cost_per_unit": 18,   "category": "육류"},
    "소고기":      {"stock": 3000,  "max_stock": 3000,  "unit": "g",  "cost_per_unit": 45,   "category": "육류"},
    "국수면":      {"stock": 8000,  "max_stock": 8000,  "unit": "g",  "cost_per_unit": 3,    "category": "곡류"},
    "쌀":          {"stock": 15000, "max_stock": 15000, "unit": "g",  "cost_per_unit": 2,    "category": "곡류"},
    "대파":        {"stock": 2000,  "max_stock": 2000,  "unit": "g",  "cost_per_unit": 4,    "category": "채소"},
    "마늘":        {"stock": 1000,  "max_stock": 1000,  "unit": "g",  "cost_per_unit": 12,   "category": "채소"},
    "생강":        {"stock": 500,   "max_stock": 500,   "unit": "g",  "cost_per_unit": 10,   "category": "채소"},
    "김치":        {"stock": 5000,  "max_stock": 5000,  "unit": "g",  "cost_per_unit": 6,    "category": "채소"},
    "깍두기":      {"stock": 3000,  "max_stock": 3000,  "unit": "g",  "cost_per_unit": 5,    "category": "채소"},
    "계란":        {"stock": 60,    "max_stock": 60,    "unit": "개", "cost_per_unit": 200,  "category": "기타"},
    "참기름":      {"stock": 500,   "max_stock": 500,   "unit": "ml", "cost_per_unit": 40,   "category": "기타"},
    "소금":        {"stock": 2000,  "max_stock": 2000,  "unit": "g",  "cost_per_unit": 1,    "category": "기타"},
    "후추":        {"stock": 200,   "max_stock": 200,   "unit": "g",  "cost_per_unit": 20,   "category": "기타"},
    "국간장":      {"stock": 1000,  "max_stock": 1000,  "unit": "ml", "cost_per_unit": 8,    "category": "기타"},
    "육수":        {"stock": 30000, "max_stock": 30000, "unit": "ml", "cost_per_unit": 1,    "category": "기타"},
}

# 메뉴별 레시피 (한 그릇당 소요량)
# 단위는 INGREDIENTS의 단위와 동일
RECIPES = {
    "돼지국밥": {
        "price": 9000,
        "ingredients": {
            "돼지고기": 150,
            "쌀":       200,
            "육수":     800,
            "대파":     20,
            "마늘":     10,
            "생강":     5,
            "깍두기":   100,
            "소금":     5,
            "후추":     1,
            "국간장":   10,
        }
    },
    "소고기국밥": {
        "price": 12000,
        "ingredients": {
            "소고기":   120,
            "소뼈":     200,
            "쌀":       200,
            "육수":     800,
            "대파":     20,
            "마늘":     10,
            "깍두기":   100,
            "소금":     5,
            "후추":     1,
            "국간장":   15,
        }
    },
    "잔치국수": {
        "price": 7000,
        "ingredients": {
            "국수면":   150,
            "육수":     600,
            "대파":     15,
            "마늘":     8,
            "계란":     1,
            "김치":     80,
            "참기름":   5,
            "소금":     3,
            "국간장":   10,
        }
    },
    "비빔국수": {
        "price": 8000,
        "ingredients": {
            "국수면":   150,
            "대파":     10,
            "마늘":     5,
            "김치":     100,
            "계란":     1,
            "참기름":   8,
            "소금":     2,
        }
    },
}

# 카테고리별 공급업체 매핑
# .env 파일의 SUPPLIER_카테고리명 으로 설정됩니다
SUPPLIER_CATEGORIES = {
    "육류": "육류",
    "채소": "채소",
    "곡류": "곡류",
    "기타": "기타",
}
