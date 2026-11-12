"""Authentication helpers and FastAPI dependencies."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Any

from fastapi import HTTPException, Request, status

from .database import get_connection

PBKDF2_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(expected, actual)
    except (ValueError, TypeError):
        return False


def public_user(row: Any) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "municipality": row["municipality"],
        "created_at": row["created_at"],
    }


def current_user(request: Request) -> dict[str, Any] | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, full_name, email, municipality, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        request.session.clear()
        return None
    return public_user(row)


def require_user(request: Request) -> dict[str, Any]:
    user = current_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to continue.",
        )
    return user


def session_secret() -> str:
    return os.getenv("SESSION_SECRET", "hatod-akean-local-dev-secret-change-me")
