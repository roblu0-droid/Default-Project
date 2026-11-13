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

        # Sync the menu on every boot instead of only seeding an empty table.
        # catalog.py is the source of truth: existing dishes get their category,
        # copy and price refreshed, new dishes get inserted. Stock and
        # availability are left untouched so live inventory survives a restart.
        for item in MENU_SEED:
            existing = conn.execute(
                "SELECT id FROM menu_items WHERE name = ?", (item["name"],)
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE menu_items
                       SET category = ?, description = ?, price_php = ?,
                           municipality = ?, image_url = ?, ingredients = ?,
                           cooking_notes = ?, allergens = ?, prep_minutes = ?
                     WHERE id = ?
                    """,
                    (
                        item["category"],
                        item["description"],
                        item["price_php"],
                        item["municipality"],
                        item["image_url"],
                        item["ingredients"],
                        item["cooking_notes"],
                        item["allergens"],
                        item["prep_minutes"],
                        existing["id"],
                    ),
                )
                continue
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
