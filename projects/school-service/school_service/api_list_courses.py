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
from .api_list_students import *  # noqa: F401,F403


def list_courses(services: Services, query: Query) -> List[Dict[str, Any]]:
    """Courses matching the query-string filters."""
    repo = services.store.courses
    items = repo.list()
    if "q" in query:
        hits = {item.id for item in repo.search(query["q"])}
        items = [item for item in items if item.id in hits]
    if "teacher_id" in query:
        wanted_id = query_int(query, "teacher_id")
        items = [item for item in items if item.teacher_id == wanted_id]
    if "title" in query:
        items = [item for item in items if item.title == query["title"]]
    if "code" in query:
        items = [item for item in items if item.code == query["code"]]
    if "min_credits" in query:
        limit = query_number(query, "min_credits")
        items = [item for item in items if item.credits >= limit]
    if "max_credits" in query:
        limit = query_number(query, "max_credits")
        items = [item for item in items if item.credits <= limit]
    if "room" in query:
        items = [item for item in items if item.room == query["room"]]
    if "term" in query:
        wanted = check_choice("term", query["term"], CourseTerm)
        items = [item for item in items if item.term == wanted]
    items = sort_items(items, query, COURSE_SORTABLE)
    return paginate(items, query)
