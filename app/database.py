"""SQLite access layer for Hatod Akean."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "hatod_aklan.db"
DB_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH)))


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL,
    municipality TEXT NOT NULL DEFAULT 'Kalibo',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    price_php REAL NOT NULL,
    municipality TEXT NOT NULL,
    image_url TEXT NOT NULL,
    ingredients TEXT NOT NULL DEFAULT '',
    cooking_notes TEXT NOT NULL DEFAULT '',
    allergens TEXT NOT NULL DEFAULT '',
    prep_minutes INTEGER NOT NULL DEFAULT 30,
    stock_qty INTEGER NOT NULL DEFAULT 20,
    is_available INTEGER NOT NULL DEFAULT 1,
    is_signature INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reference TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    barangay TEXT NOT NULL,
    municipality TEXT NOT NULL,
    contact_number TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    subtotal_php REAL NOT NULL,
    delivery_fee_php REAL NOT NULL,
    total_php REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Preparing',
    hub TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER NOT NULL REFERENCES menu_items(id),
    item_name TEXT NOT NULL,
    unit_price_php REAL NOT NULL,
    quantity INTEGER NOT NULL,
    line_total_php REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS integration_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    correlation_id TEXT NOT NULL,
    pattern TEXT NOT NULL,
    channel TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'info',
    title TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    payload TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_user ON integration_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_order ON integration_logs(order_id, id);
CREATE INDEX IF NOT EXISTS idx_menu_category ON menu_items(category);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a connection and always close it."""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
