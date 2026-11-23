"""Api (continued)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .models import (
    APPOINTMENT_SORTABLE,
    AppointmentStatus,
    DOCTOR_SORTABLE,
    DoctorSpecialty,
    INVOICE_SORTABLE,
    InvoiceStatus,
    LAB_RESULT_SORTABLE,
    PATIENT_SORTABLE,
    PRESCRIPTION_SORTABLE,
    ValidationError,
    check_choice,
    check_date,
)
from .services import Conflict, NotFound, Services

Response = Tuple[int, Any]
Query = Dict[str, str]
from .api_query_int import *  # noqa: F401,F403


def sort_items(items: List[Any], query: Query, allowed: Tuple[str, ...]) -> List[Any]:
    key = query.get("sort")
    if not key:
        return items
    reverse = key.startswith("-")
    key = key.lstrip("-")
    if key not in allowed:
        raise ValidationError("sort", "can't sort on " + key)
    return sorted(items, key=lambda item: getattr(item, key), reverse=reverse)
