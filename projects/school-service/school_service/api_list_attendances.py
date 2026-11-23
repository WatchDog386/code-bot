"""Api (continued)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .models import (
    ASSIGNMENT_SORTABLE,
    ATTENDANCE_SORTABLE,
    COURSE_SORTABLE,
    CourseTerm,
    ENROLLMENT_SORTABLE,
    EnrollmentStatus,
    STUDENT_SORTABLE,
    TEACHER_SORTABLE,
    ValidationError,
    check_choice,
    check_date,
)
from .services import Conflict, NotFound, Services

Response = Tuple[int, Any]
Query = Dict[str, str]
from .api_handle_assignments import *  # noqa: F401,F403


def list_attendances(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Attendances matching the query-string filters."""
    repo = services.store.attendances
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "student_id" in query:
        wanted_id = query_int(query, "student_id")
        items = [item for item in items if item.student_id == wanted_id]
    if "course_id" in query:
        wanted_id = query_int(query, "course_id")
        items = [item for item in items if item.course_id == wanted_id]
    if "day_from" in query:
        day = check_date("day_from", query["day_from"])
        items = [item for item in items if item.day >= day]
    if "day_to" in query:
        day = check_date("day_to", query["day_to"])
        items = [item for item in items if item.day <= day]
    if "present" in query:
        flag = query_flag(query, "present")
        items = [item for item in items if item.present is flag]
    if "min_minutes_late" in query:
        limit = query_number(query, "min_minutes_late")
        items = [item for item in items if item.minutes_late >= limit]
    if "max_minutes_late" in query:
        limit = query_number(query, "max_minutes_late")
        items = [item for item in items if item.minutes_late <= limit]
    if "note" in query:
        items = [item for item in items if item.note == query["note"]]
    items = sort_items(items, query, ATTENDANCE_SORTABLE)
    return paginate(items, query)
