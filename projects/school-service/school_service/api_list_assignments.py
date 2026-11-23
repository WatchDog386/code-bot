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
from .api_handle_enrollments import *  # noqa: F401,F403


def list_assignments(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Assignments matching the query-string filters."""
    repo = services.store.assignments
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "course_id" in query:
        wanted_id = query_int(query, "course_id")
        items = [item for item in items if item.course_id == wanted_id]
    if "title" in query:
        items = [item for item in items if item.title == query["title"]]
    if "due_from" in query:
        day = check_date("due_from", query["due_from"])
        items = [item for item in items if item.due >= day]
    if "due_to" in query:
        day = check_date("due_to", query["due_to"])
        items = [item for item in items if item.due <= day]
    if "min_max_points" in query:
        limit = query_number(query, "min_max_points")
        items = [item for item in items if item.max_points >= limit]
    if "max_max_points" in query:
        limit = query_number(query, "max_max_points")
        items = [item for item in items if item.max_points <= limit]
    if "min_weight" in query:
        limit = query_number(query, "min_weight")
        items = [item for item in items if item.weight >= limit]
    if "max_weight" in query:
        limit = query_number(query, "max_weight")
        items = [item for item in items if item.weight <= limit]
    if "published" in query:
        flag = query_flag(query, "published")
        items = [item for item in items if item.published is flag]
    items = sort_items(items, query, ASSIGNMENT_SORTABLE)
    return paginate(items, query)
