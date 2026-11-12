"""Hatod Akean — Aklanon's Famous Cuisine.

FastAPI application: landing page, authenticated ordering experience, SQLite
persistence, and a live EIP middleware event bus.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import secrets
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from .auth import (
    current_user,
    hash_password,
    public_user,
    require_user,
    session_secret,
    verify_password,
)
from .catalog import CATEGORIES, DELIVERY_ZONES, MENU_SEED, MUNICIPALITIES, VIDEOS
from .database import get_connection, init_db
from .eip import integration_bus
from .seed import DEMO_EMAIL, DEMO_PASSWORD, seed_database

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    seed_database()
    await integration_bus.start()
    yield
    await integration_bus.stop()


app = FastAPI(
    title="Hatod Akean",
    description="Aklanon's Famous Cuisine — food ordering with an EIP event bus.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret(),
    session_cookie="hatod_session",
    max_age=60 * 60 * 24 * 14,
    same_site="lax",
    https_only=os.getenv("COOKIE_SECURE", "0").lower() in {"1", "true", "yes"},
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    municipality: str = Field(default="Kalibo", max_length=40)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=1, max_length=128)


class ProfileIn(BaseModel):
    municipality: str = Field(max_length=40)


class OrderItemIn(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=20)


class OrderIn(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1, max_length=30)
    municipality: str = Field(min_length=2, max_length=40)
    barangay: str = Field(min_length=2, max_length=80)
    delivery_address: str = Field(min_length=5, max_length=250)
    contact_number: str = Field(min_length=7, max_length=20)
    payment_method: Literal["Cash on Delivery", "GCash", "Maya"] = "Cash on Delivery"
    notes: str = Field(default="", max_length=300)


# ---------------------------------------------------------------------------
# Presentation routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    user = current_user(request)
    if user:
        return RedirectResponse("/app", status_code=302)
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "demo_email": DEMO_EMAIL,
            "demo_password": DEMO_PASSWORD,
            "municipalities": MUNICIPALITIES,
        },
    )


@app.get("/app", response_class=HTMLResponse)
async def application_page(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request,
        "app.html",
        {
            "user": user,
            "user_json": json.dumps(user, ensure_ascii=False),
            "municipalities": MUNICIPALITIES,
            "categories": CATEGORIES,
            "videos": VIDEOS,
            "demo_mode": os.getenv("DEMO_MODE", "1") == "1",
        },
    )


@app.get("/health")
async def health():
    try:
        with get_connection() as conn:
            menu_count = conn.execute("SELECT COUNT(*) AS c FROM menu_items").fetchone()["c"]
        return {
            "status": "ok",
            "service": "hatod-akean",
            "database": "sqlite",
            "menu_items": menu_count,
            "eip_channels": integration_bus.stats(),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "detail": str(exc)},
        )


# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------
@app.post("/api/auth/register", status_code=201)
async def register(payload: RegisterIn, request: Request):
    full_name = " ".join(payload.full_name.split())
    email = payload.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=422, detail="Passwords do not match.")
    if payload.municipality not in MUNICIPALITIES:
        raise HTTPException(status_code=422, detail="Choose an Aklan municipality.")

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (full_name, email, password_hash, municipality)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, email, hash_password(payload.password), payload.municipality),
            )
            user_id = cursor.lastrowid
            row = conn.execute(
                "SELECT id, full_name, email, municipality, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="That email already has a Hatod Akean account. Try signing in.",
        ) from None

    request.session["user_id"] = user_id
    return {"message": "Maayong pag-abot! Your account is ready.", "user": public_user(row)}


@app.post("/api/auth/login")
async def login(payload: LoginIn, request: Request):
    email = payload.email.strip().lower()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    request.session["user_id"] = row["id"]
    return {"message": "Welcome back to Hatod Akean.", "user": public_user(row)}


@app.post("/api/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "You have been signed out."}


@app.get("/api/auth/me")
async def me(user: dict = Depends(require_user)):
    return {"user": user}


@app.patch("/api/auth/me")
async def update_me(payload: ProfileIn, user: dict = Depends(require_user)):
    if payload.municipality not in MUNICIPALITIES:
        raise HTTPException(status_code=422, detail="Choose an Aklan municipality.")
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET municipality = ? WHERE id = ?",
            (payload.municipality, user["id"]),
        )
        row = conn.execute(
            "SELECT id, full_name, email, municipality, created_at FROM users WHERE id = ?",
            (user["id"],),
        ).fetchone()
    return {"message": "Delivery municipality updated.", "user": public_user(row)}


# ---------------------------------------------------------------------------
# Catalog API
# ---------------------------------------------------------------------------
def serialize_menu_row(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "description": row["description"],
        "price_php": round(float(row["price_php"]), 2),
        "municipality": row["municipality"],
        "image_url": row["image_url"],
        "ingredients": row["ingredients"],
        "cooking_notes": row["cooking_notes"],
        "allergens": row["allergens"],
        "prep_minutes": row["prep_minutes"],
        "stock_qty": row["stock_qty"],
        "is_available": bool(row["is_available"]),
        "is_signature": bool(row["is_signature"]),
    }


@app.get("/api/menu")
async def menu(
    category: str | None = Query(default=None),
    municipality: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=80),
):
    clauses = ["is_available = 1"]
    params: list = []
    if category and category != "All":
        clauses.append("category = ?")
        params.append(category)
    if municipality and municipality != "All":
        clauses.append("municipality = ?")
        params.append(municipality)
    if q:
        clauses.append("(name LIKE ? OR description LIKE ? OR ingredients LIKE ?)")
        term = f"%{q.strip()}%"
        params.extend([term, term, term])
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM menu_items WHERE {' AND '.join(clauses)} ORDER BY is_signature DESC, category, name",
            params,
        ).fetchall()
    return {
        "items": [serialize_menu_row(row) for row in rows],
        "categories": CATEGORIES,
        "count": len(rows),
    }


@app.get("/api/zones")
async def zones():
    return {
        "zones": [
            {
                "municipality": name,
                "hub": data["hub"],
                "fee": data["fee"],
                "eta": data["eta"],
                "barangays": data["barangays"],
            }
            for name, data in DELIVERY_ZONES.items()
        ]
    }


@app.get("/api/videos")
async def videos():
    return {"videos": VIDEOS}


# ---------------------------------------------------------------------------
# Orders API
# ---------------------------------------------------------------------------
def _serialize_order(row, items) -> dict:
    return {
        "id": row["id"],
        "reference": row["reference"],
        "customer_name": row["customer_name"],
        "delivery_address": row["delivery_address"],
        "barangay": row["barangay"],
        "municipality": row["municipality"],
        "contact_number": row["contact_number"],
        "payment_method": row["payment_method"],
        "subtotal_php": round(float(row["subtotal_php"]), 2),
        "delivery_fee_php": round(float(row["delivery_fee_php"]), 2),
        "total_php": round(float(row["total_php"]), 2),
        "status": row["status"],
        "hub": row["hub"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "items": [
            {
                "menu_item_id": item["menu_item_id"],
                "name": item["item_name"],
                "unit_price_php": round(float(item["unit_price_php"]), 2),
                "quantity": item["quantity"],
                "line_total_php": round(float(item["line_total_php"]), 2),
            }
            for item in items
        ],
    }


def _fetch_order(conn, customer_id: int, order_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND customer_id = ?",
        (order_id, customer_id),
    ).fetchone()
    if row is None:
        return None
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
        (order_id,),
    ).fetchall()
    return _serialize_order(row, items)


@app.post("/api/orders", status_code=201)
async def create_order(payload: OrderIn, user: dict = Depends(require_user)):
    if payload.municipality not in DELIVERY_ZONES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{payload.municipality} is outside our Aklan delivery network. "
                "Choose Kalibo, Numancia, Banga, Ibajay, or Malay."
            ),
        )
    zone = DELIVERY_ZONES[payload.municipality]
    if payload.barangay not in zone["barangays"]:
        raise HTTPException(status_code=422, detail="That barangay is not in the selected delivery zone.")
    if not PHONE_RE.match(payload.contact_number.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid contact number.")

    quantities: dict[int, int] = {}
    for item in payload.items:
        quantities[item.menu_item_id] = quantities.get(item.menu_item_id, 0) + item.quantity
    ids = list(quantities.keys())
    placeholders = ",".join("?" for _ in ids)

    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM menu_items WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
        by_id = {row["id"]: row for row in rows}
        if len(by_id) != len(ids):
            raise HTTPException(status_code=400, detail="One or more menu items no longer exist.")

        snapshot = []
        stock_errors = []
        subtotal = 0.0
        for menu_id, quantity in quantities.items():
            row = by_id[menu_id]
            if not row["is_available"] or quantity > row["stock_qty"]:
                stock_errors.append(
                    f"{row['name']} has only {row['stock_qty']} portion(s) left."
                )
                continue
            line_total = round(float(row["price_php"]) * quantity, 2)
            subtotal += line_total
            snapshot.append({
                "menu_item_id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "quantity": quantity,
                "stock_qty": row["stock_qty"],
                "is_available": row["is_available"],
                "ingredients": row["ingredients"],
                "cooking_notes": row["cooking_notes"],
                "allergens": row["allergens"],
                "prep_minutes": row["prep_minutes"],
                "unit_price_php": round(float(row["price_php"]), 2),
                "line_total_php": line_total,
            })
        if stock_errors:
            raise HTTPException(status_code=409, detail=" ".join(stock_errors))

        subtotal = round(subtotal, 2)
        delivery_fee = float(zone["fee"])
        total = round(subtotal + delivery_fee, 2)
        reference = f"HATOD-{datetime.now(timezone.utc):%Y%m%d}-{secrets.token_hex(3).upper()}"
        cursor = conn.execute(
            """
            INSERT INTO orders (
                customer_id, reference, customer_name, delivery_address, barangay,
                municipality, contact_number, payment_method, subtotal_php,
                delivery_fee_php, total_php, status, hub, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"], reference, user["full_name"], payload.delivery_address.strip(),
                payload.barangay, payload.municipality, payload.contact_number.strip(),
                payload.payment_method, subtotal, delivery_fee, total, "Preparing",
                zone["hub"], payload.notes.strip(),
            ),
        )
        order_id = cursor.lastrowid
        for item in snapshot:
            conn.execute(
                """
                INSERT INTO order_items (
                    order_id, menu_item_id, item_name, unit_price_php,
                    quantity, line_total_php
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id, item["menu_item_id"], item["name"],
                    item["unit_price_php"], item["quantity"], item["line_total_php"],
                ),
            )
            conn.execute(
                "UPDATE menu_items SET stock_qty = stock_qty - ? WHERE id = ?",
                (item["quantity"], item["menu_item_id"]),
            )
        order_row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        order_items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
            (order_id,),
        ).fetchall()
        order = _serialize_order(order_row, order_items)

    integration_payload = {
        **order,
        "items": snapshot,
    }
    integration = await integration_bus.process_order(integration_payload, user["id"])
    order["status"] = "Preparing" if integration.get("accepted") else "Needs review"
    return {"order": order, "integration": integration}


@app.get("/api/orders")
async def list_orders(user: dict = Depends(require_user)):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY id DESC LIMIT 25",
            (user["id"],),
        ).fetchall()
        orders = []
        for row in rows:
            items = conn.execute(
                "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
                (row["id"],),
            ).fetchall()
            orders.append(_serialize_order(row, items))
    return {"orders": orders}


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, user: dict = Depends(require_user)):
    with get_connection() as conn:
        order = _fetch_order(conn, user["id"], order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    order["integration_logs"] = integration_bus.logs_for_order(user["id"], order_id)
    return {"order": order}


# ---------------------------------------------------------------------------
# Integration API
# ---------------------------------------------------------------------------
@app.get("/api/integration/logs")
async def integration_logs(
    limit: int = Query(default=40, ge=1, le=100),
    user: dict = Depends(require_user),
):
    return {
        "logs": integration_bus.recent_logs(user["id"], limit=limit),
        "channels": integration_bus.stats(),
    }


@app.get("/api/integration/orders/{order_id}/logs")
async def order_integration_logs(order_id: int, user: dict = Depends(require_user)):
    with get_connection() as conn:
        order = _fetch_order(conn, user["id"], order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return {"logs": integration_bus.logs_for_order(user["id"], order_id)}


@app.post("/api/integration/demo")
async def run_filter_demo(user: dict = Depends(require_user)):
    result = await integration_bus.simulate_out_of_zone(user["id"])
    return {
        "message": "A demo order from Manila was pushed into the integration bus.",
        "result": result,
        "channels": integration_bus.stats(),
    }


@app.get("/api/integration/stream")
async def integration_stream(request: Request, user: dict = Depends(require_user)):
    queue = integration_bus.broker.subscribe(user["id"])

    async def event_generator():
        try:
            yield "retry: 3000\n"
            yield 'event: ready\ndata: {"connected": true}\n\n'
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=18)
                    yield f"event: integration\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            integration_bus.broker.unsubscribe(user["id"], queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
