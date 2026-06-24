"""공급업체 정보 관리"""

import json
import os
from datetime import datetime

SUPPLIERS_FILE = "suppliers.json"
ORDER_LOG_FILE = "order_log.json"


def _load() -> list[dict]:
    if not os.path.exists(SUPPLIERS_FILE):
        return []
    with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[dict]):
    with open(SUPPLIERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_suppliers() -> list[dict]:
    return _load()


def get_supplier(supplier_id: int) -> dict | None:
    for s in _load():
        if s["id"] == supplier_id:
            return s
    return None


def get_suppliers_by_category(category: str) -> list[dict]:
    return [s for s in _load() if s.get("category") == category]


def add_supplier(data: dict) -> dict:
    suppliers = _load()
    new_id = max((s["id"] for s in suppliers), default=0) + 1
    entry = {
        "id": new_id,
        "name": data.get("name", "").strip(),
        "category": data.get("category", "").strip(),
        "phone": data.get("phone", "").strip(),
        "email": data.get("email", "").strip(),
        "kakao": data.get("kakao", "").strip(),
        "bank_name": data.get("bank_name", "").strip(),
        "bank_account": data.get("bank_account", "").strip(),
        "bank_holder": data.get("bank_holder", "").strip(),
        "business_no": data.get("business_no", "").strip(),
        "address": data.get("address", "").strip(),
        "memo": data.get("memo", "").strip(),
        "created_at": datetime.now().isoformat(),
    }
    suppliers.append(entry)
    _save(suppliers)
    return entry


def update_supplier(supplier_id: int, data: dict) -> dict | None:
    suppliers = _load()
    for s in suppliers:
        if s["id"] == supplier_id:
            for key in ("name", "category", "phone", "email", "kakao",
                        "bank_name", "bank_account", "bank_holder",
                        "business_no", "address", "memo"):
                if key in data:
                    s[key] = str(data[key]).strip()
            s["updated_at"] = datetime.now().isoformat()
            _save(suppliers)
            return s
    return None


def delete_supplier(supplier_id: int) -> bool:
    suppliers = _load()
    new_list = [s for s in suppliers if s["id"] != supplier_id]
    if len(new_list) == len(suppliers):
        return False
    _save(new_list)
    return True


# ── 발주 로그 ──────────────────────────────────────────

def save_order_log(items: list[dict], supplier_name: str = "",
                   category: str = "", method: str = "email"):
    logs = []
    if os.path.exists(ORDER_LOG_FILE):
        with open(ORDER_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    entry = {
        "id": max((l["id"] for l in logs), default=0) + 1,
        "timestamp": datetime.now().isoformat(),
        "supplier": supplier_name,
        "category": category,
        "method": method,
        "items": items,
        "status": "발주완료",
    }
    logs.append(entry)
    with open(ORDER_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    return entry


def get_order_logs(limit: int = 50) -> list[dict]:
    if not os.path.exists(ORDER_LOG_FILE):
        return []
    with open(ORDER_LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
    return list(reversed(logs))[:limit]
