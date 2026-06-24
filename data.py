"""
한씨막국수 메뉴 및 식자재 데이터
단위 기준: kg / L / 판(계란 30개) / 봉(김 10장)
"""

# cost_per_unit: 단위당 원가(원)
#   kg  기준: 예) 메밀면 1kg = 5,000원
#   L   기준: 예) 가다랑어육수 1L = 1,000원
#   판  기준: 계란 1판(30개) = 6,000원
#   봉  기준: 김 1봉(10장) = 500원
INGREDIENTS = {
    # ── 면류 ────────────────────────────────
    "메밀면":        {"stock": 10,   "max_stock": 10,   "unit": "kg", "cost_per_unit": 5000,  "category": "면류"},
    "칼국수면":      {"stock": 8,    "max_stock": 8,    "unit": "kg", "cost_per_unit": 3000,  "category": "면류"},

    # ── 수산 ────────────────────────────────
    "명태":          {"stock": 10,   "max_stock": 10,   "unit": "kg", "cost_per_unit": 12000, "category": "수산"},

    # ── 육류 ────────────────────────────────
    "암퇘지삼겹살":  {"stock": 15,   "max_stock": 15,   "unit": "kg", "cost_per_unit": 20000, "category": "육류"},
    "사골":          {"stock": 20,   "max_stock": 20,   "unit": "kg", "cost_per_unit": 4000,  "category": "육류"},
    "한우사골":      {"stock": 10,   "max_stock": 10,   "unit": "kg", "cost_per_unit": 8000,  "category": "육류"},

    # ── 육수 ────────────────────────────────
    "가다랑어육수":  {"stock": 30,   "max_stock": 30,   "unit": "L",  "cost_per_unit": 1000,  "category": "육수"},
    "한우사골육수":  {"stock": 30,   "max_stock": 30,   "unit": "L",  "cost_per_unit": 2000,  "category": "육수"},
    "한우막국수육수":{"stock": 30,   "max_stock": 30,   "unit": "L",  "cost_per_unit": 1000,  "category": "육수"},

    # ── 채소 ────────────────────────────────
    "배":            {"stock": 5,    "max_stock": 5,    "unit": "kg", "cost_per_unit": 5000,  "category": "채소"},
    "오이":          {"stock": 3,    "max_stock": 3,    "unit": "kg", "cost_per_unit": 3000,  "category": "채소"},
    "청양고추":      {"stock": 1,    "max_stock": 1,    "unit": "kg", "cost_per_unit": 8000,  "category": "채소"},
    "대파":          {"stock": 3,    "max_stock": 3,    "unit": "kg", "cost_per_unit": 4000,  "category": "채소"},
    "마늘":          {"stock": 1,    "max_stock": 1,    "unit": "kg", "cost_per_unit": 12000, "category": "채소"},
    "생강":          {"stock": 0.5,  "max_stock": 0.5,  "unit": "kg", "cost_per_unit": 10000, "category": "채소"},
    "양파":          {"stock": 5,    "max_stock": 5,    "unit": "kg", "cost_per_unit": 2000,  "category": "채소"},

    # ── 양념 ────────────────────────────────
    "된장":          {"stock": 3,    "max_stock": 3,    "unit": "kg", "cost_per_unit": 6000,  "category": "양념"},
    "고추가루":      {"stock": 2,    "max_stock": 2,    "unit": "kg", "cost_per_unit": 15000, "category": "양념"},
    "영양산고추가루":{"stock": 1,    "max_stock": 1,    "unit": "kg", "cost_per_unit": 20000, "category": "양념"},
    "참기름":        {"stock": 1,    "max_stock": 1,    "unit": "L",  "cost_per_unit": 40000, "category": "양념"},
    "식초":          {"stock": 2,    "max_stock": 2,    "unit": "L",  "cost_per_unit": 2000,  "category": "양념"},
    "간장":          {"stock": 2,    "max_stock": 2,    "unit": "L",  "cost_per_unit": 5000,  "category": "양념"},
    "소금":          {"stock": 2,    "max_stock": 2,    "unit": "kg", "cost_per_unit": 1000,  "category": "양념"},
    "설탕":          {"stock": 2,    "max_stock": 2,    "unit": "kg", "cost_per_unit": 2000,  "category": "양념"},
    "겨자":          {"stock": 0.5,  "max_stock": 0.5,  "unit": "kg", "cost_per_unit": 10000, "category": "양념"},

    # ── 기타 ────────────────────────────────
    # 계란: 1판 = 30개, 6,000원/판
    "계란":          {"stock": 2,    "max_stock": 4,    "unit": "판", "cost_per_unit": 6000,  "category": "기타"},
    # 김: 1봉 = 10장, 500원/봉
    "김":            {"stock": 10,   "max_stock": 20,   "unit": "봉", "cost_per_unit": 500,   "category": "기타"},
}

# ── 메뉴별 레시피 (한 그릇당 사용량) ──────────────────
# 단위는 INGREDIENTS와 동일 (kg / L / 판 / 봉)
RECIPES = {
    "곰국시": {
        "price": 10000,
        "ingredients": {
            "칼국수면":      0.15,    # 150g = 0.15kg
            "한우사골":      0.3,     # 300g = 0.3kg
            "한우사골육수":  0.7,     # 700ml = 0.7L
            "대파":          0.015,   # 15g
            "마늘":          0.008,   # 8g
            "소금":          0.003,   # 3g
            "계란":          0.033,   # 1개 = 1/30판
        }
    },
    "온막국수": {
        "price": 9000,
        "ingredients": {
            "메밀면":        0.15,
            "명태":          0.08,
            "가다랑어육수":  0.65,
            "대파":          0.01,
            "간장":          0.015,
            "소금":          0.002,
            "계란":          0.033,   # 1개
            "김":            0.1,     # 1장 = 0.1봉
        }
    },
    "물막국수": {
        "price": 9000,
        "ingredients": {
            "메밀면":        0.15,
            "명태":          0.06,
            "한우막국수육수":0.65,
            "오이":          0.03,
            "배":            0.04,
            "식초":          0.015,
            "겨자":          0.005,
            "소금":          0.002,
            "계란":          0.033,
        }
    },
    "비빔막국수": {
        "price": 9000,
        "ingredients": {
            "메밀면":        0.15,
            "영양산고추가루":0.02,
            "고추가루":      0.01,
            "배":            0.04,
            "오이":          0.03,
            "계란":          0.033,
            "참기름":        0.008,
            "간장":          0.01,
            "설탕":          0.008,
            "식초":          0.01,
            "마늘":          0.005,
            "김":            0.1,
        }
    },
    "수육 대": {
        "price": 36000,
        "ingredients": {
            "암퇘지삼겹살":  0.6,
            "된장":          0.05,
            "마늘":          0.02,
            "생강":          0.015,
            "양파":          0.1,
            "대파":          0.03,
        }
    },
    "수육 중": {
        "price": 27000,
        "ingredients": {
            "암퇘지삼겹살":  0.45,
            "된장":          0.04,
            "마늘":          0.015,
            "생강":          0.01,
            "양파":          0.08,
            "대파":          0.02,
        }
    },
    "수육 소": {
        "price": 18000,
        "ingredients": {
            "암퇘지삼겹살":  0.3,
            "된장":          0.03,
            "마늘":          0.01,
            "생강":          0.008,
            "양파":          0.06,
            "대파":          0.015,
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
