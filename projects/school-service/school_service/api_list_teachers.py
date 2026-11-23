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
from .api_paginate import *  # noqa: F401,F403


def list_teachers(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Teachers matching the query-string filters."""
    repo = services.store.teachers
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "name" in query:
        items = [item for item in items if item.name == query["name"]]
    if "email" in query:
        items = [item for item in items if item.email == query["email"]]
    if "subject" in query:
        items = [item for item in items if item.subject == query["subject"]]
    if "hired_from" in query:
        day = check_date("hired_from", query["hired_from"])
        items = [item for item in items if item.hired >= day]
    if "hired_to" in query:
        day = check_date("hired_to", query["hired_to"])
        items = [item for item in items if item.hired <= day]
    if "min_salary" in query:
        limit = query_number(query, "min_salary")
        items = [item for item in items if item.salary >= limit]
    if "max_salary" in query:
        limit = query_number(query, "max_salary")
        items = [item for item in items if item.salary <= limit]
    if "full_time" in query:
        flag = query_flag(query, "full_time")
        items = [item for item in items if item.full_time is flag]
    items = sort_items(items, query, TEACHER_SORTABLE)
    return paginate(items, query)


def handle_teachers(services: Services, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
    """Teachers: list, create, read, change, delete, stats."""
    service = services.teachers
    if method == "STATS":
        return 200, service.stats()
    if item_id is None:
        if method == "GET":
            return 200, list_teachers(services, query)
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
