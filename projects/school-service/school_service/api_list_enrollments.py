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
from .api_handle_courses import *  # noqa: F401,F403


def list_enrollments(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Enrollments matching the query-string filters."""
    repo = services.store.enrollments
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "course_id" in query:
        wanted_id = query_int(query, "course_id")
        items = [item for item in items if item.course_id == wanted_id]
    if "student_id" in query:
        wanted_id = query_int(query, "student_id")
        items = [item for item in items if item.student_id == wanted_id]
    if "enrolled_from" in query:
        day = check_date("enrolled_from", query["enrolled_from"])
        items = [item for item in items if item.enrolled >= day]
    if "enrolled_to" in query:
        day = check_date("enrolled_to", query["enrolled_to"])
        items = [item for item in items if item.enrolled <= day]
    if "status" in query:
        wanted = check_choice("status", query["status"], EnrollmentStatus)
        items = [item for item in items if item.status == wanted]
    if "min_final_score" in query:
        limit = query_number(query, "min_final_score")
        items = [item for item in items if item.final_score >= limit]
    if "max_final_score" in query:
        limit = query_number(query, "max_final_score")
        items = [item for item in items if item.final_score <= limit]
    items = sort_items(items, query, ENROLLMENT_SORTABLE)
    return paginate(items, query)
