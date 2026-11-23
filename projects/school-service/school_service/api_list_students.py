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
from .api_list_teachers import *  # noqa: F401,F403


def list_students(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Students matching the query-string filters."""
    repo = services.store.students
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "name" in query:
        items = [item for item in items if item.name == query["name"]]
    if "email" in query:
        items = [item for item in items if item.email == query["email"]]
    if "birth_date_from" in query:
        day = check_date("birth_date_from", query["birth_date_from"])
        items = [item for item in items if item.birth_date >= day]
    if "birth_date_to" in query:
        day = check_date("birth_date_to", query["birth_date_to"])
        items = [item for item in items if item.birth_date <= day]
    if "min_grade_level" in query:
        limit = query_number(query, "min_grade_level")
        items = [item for item in items if item.grade_level >= limit]
    if "max_grade_level" in query:
        limit = query_number(query, "max_grade_level")
        items = [item for item in items if item.grade_level <= limit]
    if "guardian" in query:
        items = [item for item in items if item.guardian == query["guardian"]]
    if "active" in query:
        flag = query_flag(query, "active")
        items = [item for item in items if item.active is flag]
    items = sort_items(items, query, STUDENT_SORTABLE)
    return paginate(items, query)


def handle_students(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Students: list, create, read, change, delete, stats."""
    service = services.students
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_students(services, query)
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
