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
from .api_list_invoices import *  # noqa: F401,F403


def handle_invoices(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Invoices: list, create, read, change, delete, stats."""
    service = services.invoices
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_invoices(services, query)
        if method == "POST":
            return 201, service.create(body).to_dict()
        return 405, {"error": "method not allowed"}
    if method == "GET":
        return 200, service.get(item_id).to_dict()
    if method in ("PATCH", "PUT"):
        return 200, service.update(item_id, body).to_dict()
    if method == "DELETE":
        service.delete(item_id)
        return 204, None
    return 405, {"error": "method not allowed"}


def list_lab_results(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Lab results matching the query-string filters."""
    repo = services.store.lab_results
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "patient_id" in query:
        wanted_id = query_int(query, "patient_id")
        items = [item for item in items if item.patient_id == wanted_id]
    if "test_name" in query:
        items = [item for item in items if item.test_name == query["test_name"]]
    if "min_value" in query:
        limit = query_number(query, "min_value")
        items = [item for item in items if item.value >= limit]
    if "max_value" in query:
        limit = query_number(query, "max_value")
        items = [item for item in items if item.value <= limit]
    if "unit" in query:
        items = [item for item in items if item.unit == query["unit"]]
    if "taken_from" in query:
        day = check_date("taken_from", query["taken_from"])
        items = [item for item in items if item.taken >= day]
    if "taken_to" in query:
        day = check_date("taken_to", query["taken_to"])
        items = [item for item in items if item.taken <= day]
    if "flagged" in query:
        flag = query_flag(query, "flagged")
        items = [item for item in items if item.flagged is flag]
    items = sort_items(items, query, LAB_RESULT_SORTABLE)
    return paginate(items, query)
