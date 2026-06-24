"""사용자 인증 및 회원 관리 모듈"""

import json
import os
import hashlib
import secrets
from datetime import datetime

USERS_FILE = "users.json"


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def load_users() -> list[dict]:
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users: list[dict]):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def init_admin():
    """최초 실행 시 관리자 계정 생성 (admin / admin1234)"""
    users = load_users()
    if any(u["role"] == "admin" for u in users):
        return
    salt = secrets.token_hex(16)
    users.append({
        "id": 1,
        "username": "admin",
        "password_hash": _hash_password("admin1234", salt),
        "salt": salt,
        "name": "관리자",
        "role": "admin",
        "status": "approved",
        "created_at": datetime.now().isoformat(),
        "approved_at": datetime.now().isoformat(),
    })
    save_users(users)
    print("✓ 관리자 계정 생성 완료 (admin / admin1234)")


def login(username: str, password: str) -> dict | None:
    """로그인 — 성공 시 사용자 dict 반환, 실패 시 None"""
    users = load_users()
    for user in users:
        if user["username"] == username:
            hashed = _hash_password(password, user["salt"])
            if hashed == user["password_hash"]:
                if user["status"] == "pending":
                    return {"error": "pending"}
                if user["status"] == "rejected":
                    return {"error": "rejected"}
                return user
    return None


def register(username: str, password: str, name: str) -> dict:
    """직원 회원가입 신청"""
    users = load_users()
    if any(u["username"] == username for u in users):
        return {"error": "이미 사용 중인 아이디입니다."}
    salt = secrets.token_hex(16)
    new_id = max((u["id"] for u in users), default=0) + 1
    users.append({
        "id": new_id,
        "username": username,
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "name": name,
        "role": "staff",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_at": None,
    })
    save_users(users)
    return {"ok": True}


def approve_user(user_id: int) -> bool:
    users = load_users()
    for u in users:
        if u["id"] == user_id:
            u["status"] = "approved"
            u["approved_at"] = datetime.now().isoformat()
            save_users(users)
            return True
    return False


def reject_user(user_id: int) -> bool:
    users = load_users()
    for u in users:
        if u["id"] == user_id:
            u["status"] = "rejected"
            save_users(users)
            return True
    return False


def delete_user(user_id: int) -> bool:
    users = load_users()
    original = len(users)
    users = [u for u in users if u["id"] != user_id or u["role"] == "admin"]
    if len(users) < original:
        save_users(users)
        return True
    return False


def get_pending_users() -> list[dict]:
    return [u for u in load_users() if u["status"] == "pending"]


def get_all_staff() -> list[dict]:
    return [u for u in load_users() if u["role"] != "admin"]


def change_password(user_id: int, current_password: str, new_password: str) -> dict:
    """비밀번호 변경 — 현재 비번 확인 후 변경"""
    users = load_users()
    for u in users:
        if u["id"] == user_id:
            if _hash_password(current_password, u["salt"]) != u["password_hash"]:
                return {"error": "현재 비밀번호가 올바르지 않습니다."}
            if len(new_password) < 6:
                return {"error": "새 비밀번호는 6자 이상이어야 합니다."}
            new_salt = secrets.token_hex(16)
            u["salt"] = new_salt
            u["password_hash"] = _hash_password(new_password, new_salt)
            save_users(users)
            return {"ok": True}
    return {"error": "사용자를 찾을 수 없습니다."}
