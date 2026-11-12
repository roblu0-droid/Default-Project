"""A small, live Enterprise Integration Pattern (EIP) message bus.

The implementation intentionally mirrors the four integration patterns shown in
the UI:

1. Message Channel       -> asyncio queues with named channels and workers
2. Content-Based Router  -> route by delivery municipality + item category
3. Message Translator    -> checkout JSON -> kitchen / rider ticket formats
4. Message Filter        -> zone + stock validation -> dead-letter channel
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .catalog import CATEGORY_LANES, DELIVERY_ZONES
from .database import get_connection


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def pretty_php(value: float) -> str:
    return f"₱{value:,.2f}"


class EventBroker:
    """Fan-out broker used by the Server-Sent Events endpoint."""

    def __init__(self) -> None:
        self._subscribers: dict[int, set[asyncio.Queue]] = {}

    def subscribe(self, user_id: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._subscribers.setdefault(user_id, set()).add(queue)
        return queue

    def unsubscribe(self, user_id: int, queue: asyncio.Queue) -> None:
        subscribers = self._subscribers.get(user_id)
        if not subscribers:
            return
        subscribers.discard(queue)
        if not subscribers:
            self._subscribers.pop(user_id, None)

    async def publish(self, user_id: int, event: dict[str, Any]) -> None:
        for queue in list(self._subscribers.get(user_id, set())):
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass


class MessageChannel:
    """Named async channel backed by a queue and a single consumer worker."""

    def __init__(self, name: str, handler) -> None:
        self.name = name
        self.handler = handler
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._worker: asyncio.Task | None = None

    async def start(self) -> None:
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._run(), name=self.name)

    async def _run(self) -> None:
        while True:
            message = await self.queue.get()
            try:
                await self.handler(message)
            except Exception as exc:  # keep the channel alive in a demo environment
                print(f"[EIP] channel {self.name} failed: {exc!r}")
            finally:
                self.queue.task_done()

    async def publish(self, message: dict[str, Any]) -> None:
        await self.queue.put(message)

    async def join(self) -> None:
        await self.queue.join()

    async def stop(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            try:
                await self._worker
            except asyncio.CancelledError:
                pass
            self._worker = None

    @property
    def depth(self) -> int:
        return self.queue.qsize()


class EnterpriseIntegrationBus:
    """Coordinates the order pipeline and persists every integration event."""

    def __init__(self) -> None:
        self.broker = EventBroker()
        self.channels: dict[str, MessageChannel] = {
            "inbound": MessageChannel("channel.orders.inbound", self._handle_inbound),
            "kitchen": MessageChannel("channel.kitchen.dispatch", self._handle_kitchen),
            "rider": MessageChannel("channel.rider.delivery", self._handle_rider),
            "deadletter": MessageChannel("channel.deadletter", self._handle_deadletter),
        }
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        for channel in self.channels.values():
            await channel.start()
        self._started = True

    async def stop(self) -> None:
        for channel in self.channels.values():
            await channel.stop()
        self._started = False

    def stats(self) -> dict[str, int]:
        return {channel.name: channel.depth for channel in self.channels.values()}

    def _log(
        self,
        *,
        user_id: int | None,
        order_id: int | None,
        correlation_id: str,
        pattern: str,
        channel: str,
        event_type: str,
        title: str,
        detail: str = "",
        status: str = "info",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        created_at = utc_now()
        payload_json = json.dumps(payload or {}, ensure_ascii=False, default=str)
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO integration_logs (
                    user_id, order_id, correlation_id, pattern, channel,
                    event_type, status, title, detail, payload, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, order_id, correlation_id, pattern, channel,
                    event_type, status, title, detail, payload_json, created_at,
                ),
            )
            log_id = cursor.lastrowid
        event = {
            "id": log_id,
            "user_id": user_id,
            "order_id": order_id,
            "correlation_id": correlation_id,
            "pattern": pattern,
            "channel": channel,
            "event_type": event_type,
            "status": status,
            "title": title,
            "detail": detail,
            "payload": payload or {},
            "created_at": created_at,
        }
        if user_id is not None:
            # This is intentionally fire-and-forget from the channel worker.
            asyncio.create_task(self.broker.publish(user_id, event))
        return event

    async def process_order(self, order: dict[str, Any], user_id: int) -> dict[str, Any]:
        """Publish a validated checkout payload and await the channel cascade."""
        correlation_id = f"corr_{uuid.uuid4().hex[:14]}"
        envelope = {
            "correlation_id": correlation_id,
            "user_id": user_id,
            "order": order,
            "done": asyncio.Event(),
            "result": None,
            "logs": [],
        }
        await self.channels["inbound"].publish(envelope)
        await self.channels["inbound"].join()
        await self.channels["kitchen"].join()
        await self.channels["rider"].join()
        await self.channels["deadletter"].join()
        return envelope["result"] or {
            "accepted": False,
            "correlation_id": correlation_id,
            "errors": ["The integration pipeline did not return a result."],
            "logs": envelope["logs"],
        }

    async def simulate_out_of_zone(self, user_id: int) -> dict[str, Any]:
        """Drive a deliberately invalid order through the filter for the UI demo."""
        correlation_id = f"corr_{uuid.uuid4().hex[:14]}"
        demo_order = {
            "reference": f"DEMO-{uuid.uuid4().hex[:6].upper()}",
            "customer_name": "Demo Customer",
            "municipality": "Manila",
            "barangay": "Ermita",
            "delivery_address": "2nd Floor, Demo Building, Roxas Boulevard",
            "contact_number": "09170000000",
            "payment_method": "Cash on Delivery",
            "notes": "This is a filter demonstration.",
            "subtotal_php": 285.0,
            "delivery_fee_php": 39.0,
            "total_php": 324.0,
            "items": [
                {
                    "menu_item_id": 1,
                    "name": "Inubaran nga Manok",
                    "category": "Main Dishes",
                    "quantity": 1,
                    "stock_qty": 18,
                    "is_available": 1,
                    "ingredients": "Native chicken, ubad, coconut milk",
                    "cooking_notes": "Simmer slowly.",
                    "allergens": "Fish (patis); coconut",
                    "unit_price_php": 285.0,
                    "line_total_php": 285.0,
                }
            ],
        }
        envelope = {
            "correlation_id": correlation_id,
            "user_id": user_id,
            "order": demo_order,
            "done": asyncio.Event(),
            "result": None,
            "logs": [],
            "is_demo": True,
        }
        await self.channels["inbound"].publish(envelope)
        await self.channels["inbound"].join()
        await self.channels["deadletter"].join()
        return envelope["result"] or {
            "accepted": False,
            "correlation_id": correlation_id,
            "errors": ["Demo request was filtered."],
            "logs": envelope["logs"],
        }

    async def _handle_inbound(self, envelope: dict[str, Any]) -> None:
        order = envelope["order"]
        correlation_id = envelope["correlation_id"]
        user_id = envelope["user_id"]
        order_id = order.get("id")
        reference = order.get("reference", "DEMO")
        logs = envelope["logs"]

        # ---- Pattern 4: Message Filter ------------------------------------
        errors = self._filter_order(order)
        if errors:
            logs.append(self._log(
                user_id=user_id,
                order_id=order_id,
                correlation_id=correlation_id,
                pattern="Message Filter",
                channel="channel.orders.inbound",
                event_type="FILTER_REJECTED",
                status="error",
                title="Order blocked by delivery/stock filter",
                detail=errors[0],
                payload={
                    "order_reference": reference,
                    "municipality": order.get("municipality"),
                    "checks": {
                        "delivery_zone": order.get("municipality") in DELIVERY_ZONES,
                        "stock": not any("stock" in error.lower() for error in errors),
                        "delivery_address": bool(order.get("delivery_address")),
                    },
                    "errors": errors,
                },
            ))
            await self.channels["deadletter"].publish({
                "envelope": envelope,
                "reason": errors[0],
                "errors": errors,
            })
            envelope["result"] = {
                "accepted": False,
                "correlation_id": correlation_id,
                "errors": errors,
                "logs": logs,
            }
            envelope["done"].set()
            return

        logs.append(self._log(
            user_id=user_id,
            order_id=order_id,
            correlation_id=correlation_id,
            pattern="Message Filter",
            channel="channel.orders.inbound",
            event_type="FILTER_PASSED",
            status="success",
            title="Stock + delivery-zone validation passed",
            detail=(
                f"{order['municipality']} is inside the Aklan delivery network; "
                f"{sum(item['quantity'] for item in order['items'])} item(s) reserved."
            ),
            payload={
                "order_reference": reference,
                "municipality": order["municipality"],
                "barangay": order.get("barangay"),
                "reserved_stock": [
                    {
                        "item": item["name"],
                        "quantity": item["quantity"],
                        "stock_before": item.get("stock_qty"),
                    }
                    for item in order["items"]
                ],
            },
        ))

        # ---- Pattern 1: Message Channel -----------------------------------
        logs.append(self._log(
            user_id=user_id,
            order_id=order_id,
            correlation_id=correlation_id,
            pattern="Message Channel",
            channel="channel.orders.inbound",
            event_type="MESSAGE_ENQUEUED",
            status="info",
            title=f"Checkout payload enqueued for {reference}",
            detail="Raw customer JSON is now on the asynchronous inbound channel.",
            payload={
                "message_key": reference,
                "channel_depth": self.channels["inbound"].depth,
                "content_type": "application/json",
                "pattern_role": "producer → queue → consumer",
            },
        ))

        # ---- Pattern 2: Content-Based Router ------------------------------
        route = self._route_order(order)
        logs.append(self._log(
            user_id=user_id,
            order_id=order_id,
            correlation_id=correlation_id,
            pattern="Content-Based Router",
            channel="channel.orders.inbound",
            event_type="ROUTE_SELECTED",
            status="success",
            title=f"Routed to {route['destination']}",
            detail=route["rule"],
            payload=route,
        ))

        # ---- Pattern 3: Message Translator --------------------------------
        kitchen_ticket, rider_ticket = self._translate_order(order, route, correlation_id)
        logs.append(self._log(
            user_id=user_id,
            order_id=order_id,
            correlation_id=correlation_id,
            pattern="Message Translator",
            channel="channel.orders.inbound",
            event_type="MESSAGE_TRANSFORMED",
            status="success",
            title="Translated into kitchen + rider tickets",
            detail=(
                f"{kitchen_ticket['ticket_id']} · {rider_ticket['ticket_id']} "
                f"· {rider_ticket['payment']['collect_php']}"
            ),
            payload={
                "source_format": "customer_checkout_json",
                "target_formats": ["KITCHEN_PREP_TICKET", "RIDER_LOGISTICS_TICKET"],
                "kitchen_ticket": kitchen_ticket,
                "rider_ticket": rider_ticket,
            },
        ))

        # Publish translated messages onto downstream channels.
        await self.channels["kitchen"].publish({
            "envelope": envelope,
            "ticket": kitchen_ticket,
            "route": route,
        })
        await self.channels["rider"].publish({
            "envelope": envelope,
            "ticket": rider_ticket,
            "route": route,
        })

        envelope["result"] = {
            "accepted": True,
            "correlation_id": correlation_id,
            "route": route,
            "kitchen_ticket": kitchen_ticket,
            "rider_ticket": rider_ticket,
            "errors": [],
            "logs": logs,
        }
        envelope["done"].set()

    async def _handle_kitchen(self, message: dict[str, Any]) -> None:
        envelope = message["envelope"]
        order = envelope["order"]
        ticket = message["ticket"]
        log = self._log(
            user_id=envelope["user_id"],
            order_id=order.get("id"),
            correlation_id=envelope["correlation_id"],
            pattern="Message Channel",
            channel="channel.kitchen.dispatch",
            event_type="KITCHEN_TICKET_CONSUMED",
            status="success",
            title=f"{ticket['hub']} accepted the prep ticket",
            detail=(
                f"{ticket['station']} · {ticket['item_count']} item(s) · "
                f"ready in ~{ticket['promised_ready_mins']} min"
            ),
            payload=ticket,
        )
        envelope["logs"].append(log)

    async def _handle_rider(self, message: dict[str, Any]) -> None:
        envelope = message["envelope"]
        order = envelope["order"]
        ticket = message["ticket"]
        log = self._log(
            user_id=envelope["user_id"],
            order_id=order.get("id"),
            correlation_id=envelope["correlation_id"],
            pattern="Message Channel",
            channel="channel.rider.delivery",
            event_type="RIDER_TICKET_CONSUMED",
            status="success",
            title="Rider dispatch queue accepted the logistics ticket",
            detail=(
                f"{ticket['dropoff']['barangay']} · {ticket['eta']} · "
                f"collect {ticket['payment']['collect_php']}"
            ),
            payload=ticket,
        )
        envelope["logs"].append(log)

    async def _handle_deadletter(self, message: dict[str, Any]) -> None:
        envelope = message["envelope"]
        order = envelope["order"]
        log = self._log(
            user_id=envelope["user_id"],
            order_id=order.get("id"),
            correlation_id=envelope["correlation_id"],
            pattern="Message Filter",
            channel="channel.deadletter",
            event_type="MESSAGE_DEAD_LETTERED",
            status="error",
            title="Dead-letter queue captured a rejected order",
            detail=message["reason"],
            payload={
                "order_reference": order.get("reference"),
                "municipality": order.get("municipality"),
                "barangay": order.get("barangay"),
                "errors": message["errors"],
                "recovery": "Ops will review the payload; no kitchen or rider receives it.",
            },
        )
        envelope["logs"].append(log)

    # ---------------------------------------------------------------------
    # Pattern helpers
    # ---------------------------------------------------------------------
    def _filter_order(self, order: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        municipality = order.get("municipality", "")
        zone = DELIVERY_ZONES.get(municipality)
        if zone is None:
            errors.append(
                f"Delivery rejected: {municipality or 'Unknown municipality'} is outside the Aklan delivery network."
            )
        elif order.get("barangay") and order["barangay"] not in zone["barangays"]:
            errors.append(
                f"Delivery rejected: {order['barangay']} is not a serviceable barangay in {municipality}."
            )
        if not order.get("delivery_address"):
            errors.append("Delivery rejected: a complete delivery address is required.")
        if not order.get("contact_number"):
            errors.append("Delivery rejected: a contact number is required.")
        for item in order.get("items", []):
            if not item.get("is_available", 1):
                errors.append(f"Stock filter: {item.get('name')} is currently unavailable.")
            elif int(item.get("quantity", 0)) > int(item.get("stock_qty", 0)):
                errors.append(
                    f"Stock filter: only {item.get('stock_qty', 0)} portion(s) of "
                    f"{item.get('name')} remain."
                )
        return errors

    def _route_order(self, order: dict[str, Any]) -> dict[str, Any]:
        municipality = order["municipality"]
        zone = DELIVERY_ZONES[municipality]
        categories = Counter(item["category"] for item in order["items"])
        primary_category = categories.most_common(1)[0][0]
        lane = CATEGORY_LANES[primary_category]
        hub = zone["hub"]
        return {
            "municipality": municipality,
            "hub": hub,
            "primary_category": primary_category,
            "category_mix": dict(categories),
            "lane": lane,
            "destination": f"{hub} / {lane}",
            "delivery_fee_php": zone["fee"],
            "eta": zone["eta"],
            "rule": (
                f"WHEN municipality = '{municipality}' "
                f"AND dominant_category = '{primary_category}' "
                f"THEN route -> '{hub} / {lane}'"
            ),
        }

    def _translate_order(
        self, order: dict[str, Any], route: dict[str, Any], correlation_id: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        reference = order["reference"]
        kitchen_ticket_id = f"KIT-{reference}-{correlation_id[-5:].upper()}"
        rider_ticket_id = f"RDR-{reference}-{correlation_id[-5:].upper()}"
        allergens = sorted({
            allergen.strip()
            for item in order["items"]
            for allergen in str(item.get("allergens", "")).replace(";", ",").split(",")
            if allergen.strip()
        })
        kitchen_ticket = {
            "ticket_type": "KITCHEN_PREP",
            "ticket_id": kitchen_ticket_id,
            "correlation_id": correlation_id,
            "order_reference": reference,
            "hub": route["hub"],
            "station": route["lane"],
            "priority": "express" if order.get("total_php", 0) >= 1000 else "standard",
            "item_count": sum(item["quantity"] for item in order["items"]),
            "promised_ready_mins": max(
                (int(item.get("prep_minutes", 25)) for item in order["items"]),
                default=25,
            ),
            "allergy_alert": allergens or ["No allergies declared"],
            "customer_notes": order.get("notes") or "No special kitchen notes.",
            "items": [
                {
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "station": route["lane"],
                    "ingredients": item.get("ingredients", ""),
                    "cooking_instructions": item.get("cooking_notes", ""),
                    "allergy_notes": item.get("allergens", ""),
                }
                for item in order["items"]
            ],
            "created_at": utc_now(),
        }
        rider_ticket = {
            "ticket_type": "RIDER_LOGISTICS",
            "ticket_id": rider_ticket_id,
            "correlation_id": correlation_id,
            "order_reference": reference,
            "hub": route["hub"],
            "dropoff": {
                "customer": order.get("customer_name", ""),
                "contact": order.get("contact_number", ""),
                "municipality": order["municipality"],
                "barangay": order.get("barangay", ""),
                "address": order.get("delivery_address", ""),
            },
            "route_zone": f"{order['municipality']} · {order.get('barangay', '')}",
            "eta": route["eta"],
            "payment": {
                "method": order.get("payment_method", "Cash on Delivery"),
                "collect_php": pretty_php(order.get("total_php", 0)),
                "delivery_fee_php": pretty_php(route["delivery_fee_php"]),
                "currency": "PHP",
            },
            "package": {
                "item_count": sum(item["quantity"] for item in order["items"]),
                "handling": "Insulated bag · keep upright · hot food",
            },
            "created_at": utc_now(),
        }
        return kitchen_ticket, rider_ticket

    # ---------------------------------------------------------------------
    # Read helpers for HTTP endpoints
    # ---------------------------------------------------------------------
    def recent_logs(self, user_id: int, limit: int = 40) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM integration_logs
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [self._serialize_log(row) for row in reversed(rows)]

    def logs_for_order(self, user_id: int, order_id: int) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM integration_logs
                WHERE user_id = ? AND order_id = ?
                ORDER BY id ASC
                """,
                (user_id, order_id),
            ).fetchall()
        return [self._serialize_log(row) for row in rows]

    @staticmethod
    def _serialize_log(row) -> dict[str, Any]:
        try:
            payload = json.loads(row["payload"])
        except (TypeError, json.JSONDecodeError):
            payload = {"raw": row["payload"]}
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "order_id": row["order_id"],
            "correlation_id": row["correlation_id"],
            "pattern": row["pattern"],
            "channel": row["channel"],
            "event_type": row["event_type"],
            "status": row["status"],
            "title": row["title"],
            "detail": row["detail"],
            "payload": payload,
            "created_at": row["created_at"],
        }


integration_bus = EnterpriseIntegrationBus()
