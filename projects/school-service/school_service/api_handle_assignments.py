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
from .api_list_assignments import *  # noqa: F401,F403


def handle_assignments(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Assignments: list, create, read, change, delete, stats."""
    service = services.assignments
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_assignments(services, query)
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
