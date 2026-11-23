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
from .api_list_guests import *  # noqa: F401,F403


def list_bookings(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Bookings matching the query-string filters."""
    repo = services.store.bookings
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "room_id" in query:
        wanted_id = query_int(query, "room_id")
        items = [item for item in items if item.room_id == wanted_id]
    if "guest_id" in query:
        wanted_id = query_int(query, "guest_id")
        items = [item for item in items if item.guest_id == wanted_id]
    if "check_in_from" in query:
        day = check_date("check_in_from", query["check_in_from"])
        items = [item for item in items if item.check_in >= day]
    if "check_in_to" in query:
        day = check_date("check_in_to", query["check_in_to"])
        items = [item for item in items if item.check_in <= day]
    if "check_out_from" in query:
        day = check_date("check_out_from", query["check_out_from"])
        items = [item for item in items if item.check_out >= day]
    if "check_out_to" in query:
        day = check_date("check_out_to", query["check_out_to"])
        items = [item for item in items if item.check_out <= day]
    if "min_guests" in query:
        limit = query_number(query, "min_guests")
        items = [item for item in items if item.guests >= limit]
    if "max_guests" in query:
        limit = query_number(query, "max_guests")
        items = [item for item in items if item.guests <= limit]
    if "min_total" in query:
        limit = query_number(query, "min_total")
        items = [item for item in items if item.total >= limit]
    if "max_total" in query:
        limit = query_number(query, "max_total")
        items = [item for item in items if item.total <= limit]
    if "status" in query:
        wanted = check_choice("status", query["status"], BookingStatus)
        items = [item for item in items if item.status == wanted]
    if "notes" in query:
        items = [item for item in items if item.notes == query["notes"]]
    items = sort_items(items, query, BOOKING_SORTABLE)
    return paginate(items, query)
