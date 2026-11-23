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
from .api_paginate import *  # noqa: F401,F403


def list_room_types(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Room types matching the query-string filters."""
    repo = services.store.room_types
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "name" in query:
        items = [item for item in items if item.name == query["name"]]
    if "min_beds" in query:
        limit = query_number(query, "min_beds")
        items = [item for item in items if item.beds >= limit]
    if "max_beds" in query:
        limit = query_number(query, "max_beds")
        items = [item for item in items if item.beds <= limit]
    if "min_max_guests" in query:
        limit = query_number(query, "min_max_guests")
        items = [item for item in items if item.max_guests >= limit]
    if "max_max_guests" in query:
        limit = query_number(query, "max_max_guests")
        items = [item for item in items if item.max_guests <= limit]
    if "min_nightly_rate" in query:
        limit = query_number(query, "min_nightly_rate")
        items = [item for item in items if item.nightly_rate >= limit]
    if "max_nightly_rate" in query:
        limit = query_number(query, "max_nightly_rate")
        items = [item for item in items if item.nightly_rate <= limit]
    if "smoking" in query:
        flag = query_flag(query, "smoking")
        items = [item for item in items if item.smoking is flag]
    items = sort_items(items, query, ROOM_TYPE_SORTABLE)
    return paginate(items, query)
