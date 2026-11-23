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
from .api_handle_prescriptions import *  # noqa: F401,F403


def list_invoices(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Invoices matching the query-string filters."""
    repo = services.store.invoices
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "patient_id" in query:
        wanted_id = query_int(query, "patient_id")
        items = [item for item in items if item.patient_id == wanted_id]
    if "issued_from" in query:
        day = check_date("issued_from", query["issued_from"])
        items = [item for item in items if item.issued >= day]
    if "issued_to" in query:
        day = check_date("issued_to", query["issued_to"])
        items = [item for item in items if item.issued <= day]
    if "min_amount" in query:
        limit = query_number(query, "min_amount")
        items = [item for item in items if item.amount >= limit]
    if "max_amount" in query:
        limit = query_number(query, "max_amount")
        items = [item for item in items if item.amount <= limit]
    if "min_paid" in query:
        limit = query_number(query, "min_paid")
        items = [item for item in items if item.paid >= limit]
    if "max_paid" in query:
        limit = query_number(query, "max_paid")
        items = [item for item in items if item.paid <= limit]
    if "status" in query:
        wanted = check_choice("status", query["status"], InvoiceStatus)
        items = [item for item in items if item.status == wanted]
    if "due_from" in query:
        day = check_date("due_from", query["due_from"])
        items = [item for item in items if item.due >= day]
    if "due_to" in query:
        day = check_date("due_to", query["due_to"])
        items = [item for item in items if item.due <= day]
    items = sort_items(items, query, INVOICE_SORTABLE)
    return paginate(items, query)
