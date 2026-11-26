"""Idempotent database seeding."""

from __future__ import annotations

from .auth import hash_password
from .catalog import MENU_SEED
from .database import get_connection


DEMO_EMAIL = "demo@hatodakean.ph"
DEMO_PASSWORD = "Hatod123!"

ADMIN_EMAIL = "admin@hatodakean.ph"
ADMIN_PASSWORD = "Admin123!"


def _ensure_account(
    conn, *, full_name: str, email: str, password: str, municipality: str, is_admin: bool
) -> None:
    """Create (or repair) a demo account without touching any other user."""
    row = conn.execute(
        "SELECT id, is_admin FROM users WHERE email = ?", (email,)
    ).fetchone()
    if row is None:
        conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, municipality, is_admin)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, hash_password(password), municipality, int(is_admin)),
        )
        return
    if is_admin and not row["is_admin"]:
        # An older database may already have this email as a customer. Promote
        # it and reset the password so the documented admin login always works.
        conn.execute(
            "UPDATE users SET is_admin = 1, password_hash = ? WHERE id = ?",
            (hash_password(password), row["id"]),
        )


def seed_database() -> None:
    with get_connection() as conn:
        _ensure_account(
            conn,
            full_name="Nene Aklanon",
            email=DEMO_EMAIL,
            password=DEMO_PASSWORD,
            municipality="Kalibo",
            is_admin=False,
        )
        _ensure_account(
            conn,
            full_name="Hatod Admin",
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            municipality="Kalibo",
            is_admin=True,
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
