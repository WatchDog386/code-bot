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
from .api_list_room_types import *  # noqa: F401,F403


def handle_room_types(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Room types: list, create, read, change, delete, stats."""
    service = services.room_types
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_room_types(services, query)
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


def list_rooms(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Rooms matching the query-string filters."""
    repo = services.store.rooms
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "room_type_id" in query:
        wanted_id = query_int(query, "room_type_id")
        items = [item for item in items if item.room_type_id == wanted_id]
    if "number" in query:
        items = [item for item in items if item.number == query["number"]]
    if "min_floor" in query:
        limit = query_number(query, "min_floor")
        items = [item for item in items if item.floor >= limit]
    if "max_floor" in query:
        limit = query_number(query, "max_floor")
        items = [item for item in items if item.floor <= limit]
    if "status" in query:
        wanted = check_choice("status", query["status"], RoomStatus)
        items = [item for item in items if item.status == wanted]
    if "sea_view" in query:
        flag = query_flag(query, "sea_view")
        items = [item for item in items if item.sea_view is flag]
    items = sort_items(items, query, ROOM_SORTABLE)
    return paginate(items, query)


def handle_rooms(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Rooms: list, create, read, change, delete, stats."""
    service = services.rooms
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_rooms(services, query)
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
