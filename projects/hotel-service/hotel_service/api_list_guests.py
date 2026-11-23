"""Api (continued)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .models import (
    BOOKING_SORTABLE,
    BookingStatus,
    CHARGE_SORTABLE,
    ChargeCategory,
    GUEST_SORTABLE,
    HOUSEKEEPING_SORTABLE,
    ROOM_SORTABLE,
    ROOM_TYPE_SORTABLE,
    RoomStatus,
    ValidationError,
    check_choice,
    check_date,
)
from .services import Conflict, NotFound, Services

Response = Tuple[int, Any]
Query = Dict[str, str]
from .api_handle_room_types import *  # noqa: F401,F403


def list_guests(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Guests matching the query-string filters."""
    repo = services.store.guests
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "name" in query:
        items = [item for item in items if item.name == query["name"]]
    if "email" in query:
        items = [item for item in items if item.email == query["email"]]
    if "phone" in query:
        items = [item for item in items if item.phone == query["phone"]]
    if "country" in query:
        items = [item for item in items if item.country == query["country"]]
    if "vip" in query:
        flag = query_flag(query, "vip")
        items = [item for item in items if item.vip is flag]
    if "min_loyalty_points" in query:
        limit = query_number(query, "min_loyalty_points")
        items = [item for item in items if item.loyalty_points >= limit]
    if "max_loyalty_points" in query:
        limit = query_number(query, "max_loyalty_points")
        items = [item for item in items if item.loyalty_points <= limit]
    items = sort_items(items, query, GUEST_SORTABLE)
    return paginate(items, query)


def handle_guests(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Guests: list, create, read, change, delete, stats."""
    service = services.guests
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_guests(services, query)
        if method == "POST":
            return 201, service.create(body).to_dict()
        return 405, {"error": "method not allowed"}
    if method == "GET":
        return 200, service.get(item_id).to_dict()
    if method in ("PATCH", "PUT"):
        return 200, service.update(item_id, body).to_dict()
    if method == "DELETE":
        service.delete(item_id)
        return 204, None
    return 405, {"error": "method not allowed"}
