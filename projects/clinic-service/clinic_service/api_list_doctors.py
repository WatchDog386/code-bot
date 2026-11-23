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
from .api_sort_items import *  # noqa: F401,F403


def list_doctors(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Doctors matching the query-string filters."""
    repo = services.store.doctors
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "name" in query:
        items = [item for item in items if item.name == query["name"]]
    if "email" in query:
        items = [item for item in items if item.email == query["email"]]
    if "specialty" in query:
        wanted = check_choice("specialty", query["specialty"], DoctorSpecialty)
        items = [item for item in items if item.specialty == wanted]
    if "room" in query:
        items = [item for item in items if item.room == query["room"]]
    if "min_hourly_rate" in query:
        limit = query_number(query, "min_hourly_rate")
        items = [item for item in items if item.hourly_rate >= limit]
    if "max_hourly_rate" in query:
        limit = query_number(query, "max_hourly_rate")
        items = [item for item in items if item.hourly_rate <= limit]
    if "accepting" in query:
        flag = query_flag(query, "accepting")
        items = [item for item in items if item.accepting is flag]
    items = sort_items(items, query, DOCTOR_SORTABLE)
    return paginate(items, query)
