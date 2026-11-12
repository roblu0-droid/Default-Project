"""Idempotent database seeding."""

from __future__ import annotations

from .auth import hash_password
from .catalog import MENU_SEED
from .database import get_connection


DEMO_EMAIL = "demo@hatodakean.ph"
DEMO_PASSWORD = "Hatod123!"


def seed_database() -> None:
    with get_connection() as conn:
        if conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"] == 0:
            conn.execute(
                """
                INSERT INTO users (full_name, email, password_hash, municipality)
                VALUES (?, ?, ?, ?)
                """,
                ("Nene Aklanon", DEMO_EMAIL, hash_password(DEMO_PASSWORD), "Kalibo"),
            )

        if conn.execute("SELECT COUNT(*) AS c FROM menu_items").fetchone()["c"] == 0:
            for item in MENU_SEED:
                conn.execute(
                    """
                    INSERT INTO menu_items (
                        name, category, description, price_php, municipality,
                        image_url, ingredients, cooking_notes, allergens,
                        prep_minutes, stock_qty, is_available, is_signature
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        item["name"],
                        item["category"],
                        item["description"],
                        item["price_php"],
                        item["municipality"],
                        item["image_url"],
                        item["ingredients"],
                        item["cooking_notes"],
                        item["allergens"],
                        item["prep_minutes"],
                        item["stock_qty"],
                        item["is_signature"],
                    ),
                )
