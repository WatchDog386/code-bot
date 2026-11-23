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
from .api_handle_doctors import *  # noqa: F401,F403


def list_patients(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Patients matching the query-string filters."""
    repo = services.store.patients
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "name" in query:
        items = [item for item in items if item.name == query["name"]]
    if "email" in query:
        items = [item for item in items if item.email == query["email"]]
    if "phone" in query:
        items = [item for item in items if item.phone == query["phone"]]
    if "birth_date_from" in query:
        day = check_date("birth_date_from", query["birth_date_from"])
        items = [item for item in items if item.birth_date >= day]
    if "birth_date_to" in query:
        day = check_date("birth_date_to", query["birth_date_to"])
        items = [item for item in items if item.birth_date <= day]
    if "insurance" in query:
        items = [item for item in items if item.insurance == query["insurance"]]
    if "allergies" in query:
        items = [item for item in items if item.allergies == query["allergies"]]
    if "active" in query:
        flag = query_flag(query, "active")
        items = [item for item in items if item.active is flag]
    items = sort_items(items, query, PATIENT_SORTABLE)
    return paginate(items, query)
