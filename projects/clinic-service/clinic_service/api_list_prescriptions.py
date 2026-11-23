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
from .api_handle_appointments import *  # noqa: F401,F403


def list_prescriptions(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Prescriptions matching the query-string filters."""
    repo = services.store.prescriptions
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "appointment_id" in query:
        wanted_id = query_int(query, "appointment_id")
        items = [item for item in items if item.appointment_id == wanted_id]
    if "drug" in query:
        items = [item for item in items if item.drug == query["drug"]]
    if "min_dose_mg" in query:
        limit = query_number(query, "min_dose_mg")
        items = [item for item in items if item.dose_mg >= limit]
    if "max_dose_mg" in query:
        limit = query_number(query, "max_dose_mg")
        items = [item for item in items if item.dose_mg <= limit]
    if "min_times_per_day" in query:
        limit = query_number(query, "min_times_per_day")
        items = [item for item in items if item.times_per_day >= limit]
    if "max_times_per_day" in query:
        limit = query_number(query, "max_times_per_day")
        items = [item for item in items if item.times_per_day <= limit]
    if "min_days" in query:
        limit = query_number(query, "min_days")
        items = [item for item in items if item.days >= limit]
    if "max_days" in query:
        limit = query_number(query, "max_days")
        items = [item for item in items if item.days <= limit]
    if "min_refills" in query:
        limit = query_number(query, "min_refills")
        items = [item for item in items if item.refills >= limit]
    if "max_refills" in query:
        limit = query_number(query, "max_refills")
        items = [item for item in items if item.refills <= limit]
    if "notes" in query:
        items = [item for item in items if item.notes == query["notes"]]
    items = sort_items(items, query, PRESCRIPTION_SORTABLE)
    return paginate(items, query)
