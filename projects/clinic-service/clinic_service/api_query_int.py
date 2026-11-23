"""HTTP API for the Clinic Scheduling service (standard library only).

Run it with   python -m clinic_service.api   and open http://127.0.0.1:8000/health

Every collection supports GET (list, with filters, ?q= search, ?sort=, ?page=&size=),
POST, GET /<id>, PATCH /<id>, DELETE /<id> and GET /stats.
"""

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


def query_int(query: Query, name: str, default: int = 0) -> int:
    raw = query.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(name, "must be a whole number") from None


def query_number(query: Query, name: str) -> float:
    try:
        return float(query[name])
    except ValueError:
        raise ValidationError(name, "must be a number") from None


def query_flag(query: Query, name: str) -> bool:
    raw = query[name].lower()
    if raw in ("1", "true", "yes"):
        return True
    if raw in ("0", "false", "no"):
        return False
    raise ValidationError(name, "must be true or false")


def paginate(items: List[Any], query: Query) -> List[Dict[str, Any]]:
    page = max(1, query_int(query, "page", 1))
    size = min(200, max(1, query_int(query, "size", 50)))
    start = (page - 1) * size
    return [item.to_dict() for item in items[start:start + size]]
