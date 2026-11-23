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
from .api_handle_charges import *  # noqa: F401,F403


def list_housekeepings(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Housekeepings matching the query-string filters."""
    repo = services.store.housekeepings
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "room_id" in query:
        wanted_id = query_int(query, "room_id")
        items = [item for item in items if item.room_id == wanted_id]
    if "cleaned_from" in query:
        day = check_date("cleaned_from", query["cleaned_from"])
        items = [item for item in items if item.cleaned >= day]
    if "cleaned_to" in query:
        day = check_date("cleaned_to", query["cleaned_to"])
        items = [item for item in items if item.cleaned <= day]
    if "min_minutes" in query:
        limit = query_number(query, "min_minutes")
        items = [item for item in items if item.minutes >= limit]
    if "max_minutes" in query:
        limit = query_number(query, "max_minutes")
        items = [item for item in items if item.minutes <= limit]
    if "staff" in query:
        items = [item for item in items if item.staff == query["staff"]]
    if "inspected" in query:
        flag = query_flag(query, "inspected")
        items = [item for item in items if item.inspected is flag]
    items = sort_items(items, query, HOUSEKEEPING_SORTABLE)
    return paginate(items, query)
