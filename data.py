"""
한씨막국수 메뉴 및 식자재 데이터
"""

# 식자재 재고 현황
# cost_per_unit: 단위(g/ml/개)당 원가(원)
INGREDIENTS = {
    # 면류
    "메밀면":       {"stock": 10000, "max_stock": 10000, "unit": "g",  "cost_per_unit": 5,   "category": "면류"},
    "칼국수면":     {"stock": 8000,  "max_stock": 8000,  "unit": "g",  "cost_per_unit": 3,   "category": "면류"},

    # 육류/수산
    "명태":         {"stock": 10000, "max_stock": 10000, "unit": "g",  "cost_per_unit": 12,  "category": "수산"},
    "암퇘지삼겹살": {"stock": 15000, "max_stock": 15000, "unit": "g",  "cost_per_unit": 20,  "category": "육류"},
    "사골":         {"stock": 20000, "max_stock": 20000, "unit": "g",  "cost_per_unit": 4,   "category": "육류"},
    "한우사골":     {"stock": 10000, "max_stock": 10000, "unit": "g",  "cost_per_unit": 8,   "category": "육류"},

    # 육수/국물
    "가다랑어육수": {"stock": 30000, "max_stock": 30000, "unit": "ml", "cost_per_unit": 1,   "category": "육수"},
    "한우사골육수": {"stock": 30000, "max_stock": 30000, "unit": "ml", "cost_per_unit": 2,   "category": "육수"},
    "한우막국수육수":{"stock": 30000, "max_stock": 30000, "unit": "ml", "cost_per_unit": 1,  "category": "육수"},

    # 채소/과일
    "배":           {"stock": 5000,  "max_stock": 5000,  "unit": "g",  "cost_per_unit": 5,   "category": "채소"},
    "오이":         {"stock": 3000,  "max_stock": 3000,  "unit": "g",  "cost_per_unit": 3,   "category": "채소"},
    "청양고추":     {"stock": 1000,  "max_stock": 1000,  "unit": "g",  "cost_per_unit": 8,   "category": "채소"},
    "대파":         {"stock": 3000,  "max_stock": 3000,  "unit": "g",  "cost_per_unit": 4,   "category": "채소"},
    "마늘":         {"stock": 1000,  "max_stock": 1000,  "unit": "g",  "cost_per_unit": 12,  "category": "채소"},
    "생강":         {"stock": 500,   "max_stock": 500,   "unit": "g",  "cost_per_unit": 10,  "category": "채소"},
    "양파":         {"stock": 5000,  "max_stock": 5000,  "unit": "g",  "cost_per_unit": 2,   "category": "채소"},

    # 양념/기타
    "된장":         {"stock": 3000,  "max_stock": 3000,  "unit": "g",  "cost_per_unit": 6,   "category": "양념"},
    "고추가루":     {"stock": 2000,  "max_stock": 2000,  "unit": "g",  "cost_per_unit": 15,  "category": "양념"},
    "영양산고추가루":{"stock": 1000, "max_stock": 1000,  "unit": "g",  "cost_per_unit": 20,  "category": "양념"},
    "참기름":       {"stock": 1000,  "max_stock": 1000,  "unit": "ml", "cost_per_unit": 40,  "category": "양념"},
    "식초":         {"stock": 2000,  "max_stock": 2000,  "unit": "ml", "cost_per_unit": 2,   "category": "양념"},
    "간장":         {"stock": 2000,  "max_stock": 2000,  "unit": "ml", "cost_per_unit": 5,   "category": "양념"},
    "소금":         {"stock": 2000,  "max_stock": 2000,  "unit": "g",  "cost_per_unit": 1,   "category": "양념"},
    "설탕":         {"stock": 2000,  "max_stock": 2000,  "unit": "g",  "cost_per_unit": 2,   "category": "양념"},
    "겨자":         {"stock": 500,   "max_stock": 500,   "unit": "g",  "cost_per_unit": 10,  "category": "양념"},

    # 계란/기타 토핑
    "계란":         {"stock": 120,   "max_stock": 120,   "unit": "개", "cost_per_unit": 200, "category": "기타"},
    "김":           {"stock": 100,   "max_stock": 100,   "unit": "장", "cost_per_unit": 50,  "category": "기타"},
}

# 메뉴별 레시피 (한 그릇/1인분당 소요량)
RECIPES = {
    "곰국시": {
        "price": 10000,
        "ingredients": {
            "칼국수면":     150,
            "한우사골":     300,
            "한우사골육수": 700,
            "대파":         15,
            "마늘":         8,
            "소금":         3,
            "계란":         1,
        }
    },
    "온막국수": {
        "price": 9000,
        "ingredients": {
            "메밀면":       150,
            "명태":         80,
            "가다랑어육수": 650,
            "대파":         10,
            "간장":         15,
            "소금":         2,
            "계란":         1,
            "김":           1,
        }
    },
    "물막국수": {
        "price": 9000,
        "ingredients": {
            "메밀면":       150,
            "명태":         60,
            "한우막국수육수": 650,
            "오이":         30,
            "배":           40,
            "식초":         15,
            "겨자":         5,
            "소금":         2,
            "계란":         1,
        }
    },
    "비빔막국수": {
        "price": 9000,
        "ingredients": {
            "메밀면":       150,
            "영양산고추가루": 20,
            "고추가루":     10,
            "배":           40,
            "오이":         30,
            "계란":         1,
            "참기름":       8,
            "간장":         10,
            "설탕":         8,
            "식초":         10,
            "마늘":         5,
            "김":           1,
        }
    },
    "수육 대": {
        "price": 36000,
        "ingredients": {
            "암퇘지삼겹살": 600,
            "된장":         50,
            "마늘":         20,
            "생강":         15,
            "양파":         100,
            "대파":         30,
        }
    },
    "수육 중": {
        "price": 27000,
        "ingredients": {
            "암퇘지삼겹살": 450,
            "된장":         40,
            "마늘":         15,
            "생강":         10,
            "양파":         80,
            "대파":         20,
        }
    },
    "수육 소": {
        "price": 18000,
        "ingredients": {
            "암퇘지삼겹살": 300,
            "된장":         30,
            "마늘":         10,
            "생강":         8,
            "양파":         60,
            "대파":         15,
        }
    },
}

# 카테고리별 공급업체 (.env의 SUPPLIER_카테고리명 으로 설정)
SUPPLIER_CATEGORIES = {
    "면류": "면류",
    "수산": "수산",
    "육류": "육류",
    "육수": "육류",
    "채소": "채소",
    "양념": "기타",
    "기타": "기타",
}
