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
from .api_handle_bookings import *  # noqa: F401,F403


def list_charges(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Charges matching the query-string filters."""
    repo = services.store.charges
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "booking_id" in query:
        wanted_id = query_int(query, "booking_id")
        items = [item for item in items if item.booking_id == wanted_id]
    if "description" in query:
        items = [item for item in items if item.description == query["description"]]
    if "min_amount" in query:
        limit = query_number(query, "min_amount")
        items = [item for item in items if item.amount >= limit]
    if "max_amount" in query:
        limit = query_number(query, "max_amount")
        items = [item for item in items if item.amount <= limit]
    if "posted_from" in query:
        day = check_date("posted_from", query["posted_from"])
        items = [item for item in items if item.posted >= day]
    if "posted_to" in query:
        day = check_date("posted_to", query["posted_to"])
        items = [item for item in items if item.posted <= day]
    if "category" in query:
        wanted = check_choice("category", query["category"], ChargeCategory)
        items = [item for item in items if item.category == wanted]
    items = sort_items(items, query, CHARGE_SORTABLE)
    return paginate(items, query)
