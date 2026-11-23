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
from .api_query_int import *  # noqa: F401,F403


def paginate(items: List[Any], query: Query) -> List[Dict[str, Any]]:
    page = max(1, query_int(query, "page", 1))
    size = min(200, max(1, query_int(query, "size", 50)))
    start = (page - 1) * size
    return [item.to_dict() for item in items[start:start + size]]


def sort_items(items: List[Any], query: Query, allowed: Tuple[str, ...]) -> List[Any]:
    key = query.get("sort")
    if not key:
        return items
    reverse = key.startswith("-")
    key = key.lstrip("-")
    if key not in allowed:
        raise ValidationError("sort", "can't sort on " + key)
    return sorted(items, key=lambda item: getattr(item, key), reverse=reverse)
