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
from .api_handle_patients import *  # noqa: F401,F403


def list_appointments(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Appointments matching the query-string filters."""
    repo = services.store.appointments
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "doctor_id" in query:
        wanted_id = query_int(query, "doctor_id")
        items = [item for item in items if item.doctor_id == wanted_id]
    if "patient_id" in query:
        wanted_id = query_int(query, "patient_id")
        items = [item for item in items if item.patient_id == wanted_id]
    if "day_from" in query:
        day = check_date("day_from", query["day_from"])
        items = [item for item in items if item.day >= day]
    if "day_to" in query:
        day = check_date("day_to", query["day_to"])
        items = [item for item in items if item.day <= day]
    if "min_slot" in query:
        limit = query_number(query, "min_slot")
        items = [item for item in items if item.slot >= limit]
    if "max_slot" in query:
        limit = query_number(query, "max_slot")
        items = [item for item in items if item.slot <= limit]
    if "min_duration" in query:
        limit = query_number(query, "min_duration")
        items = [item for item in items if item.duration >= limit]
    if "max_duration" in query:
        limit = query_number(query, "max_duration")
        items = [item for item in items if item.duration <= limit]
    if "reason" in query:
        items = [item for item in items if item.reason == query["reason"]]
    if "status" in query:
        wanted = check_choice("status", query["status"], AppointmentStatus)
        items = [item for item in items if item.status == wanted]
    if "min_fee" in query:
        limit = query_number(query, "min_fee")
        items = [item for item in items if item.fee >= limit]
    if "max_fee" in query:
        limit = query_number(query, "max_fee")
        items = [item for item in items if item.fee <= limit]
    items = sort_items(items, query, APPOINTMENT_SORTABLE)
    return paginate(items, query)
