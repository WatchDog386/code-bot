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
from .api_handle_attendances import *  # noqa: F401,F403


class Api:
    """Maps HTTP requests onto the services and returns (status, payload)."""

    def __init__(self, services: Optional[Services] = None) -> None:
        self.services = services or Services()
        self.routes: Dict[str, Callable[..., Response]] = {
            "teachers": handle_teachers,
            "students": handle_students,
            "courses": handle_courses,
            "enrollments": handle_enrollments,
            "assignments": handle_assignments,
            "attendances": handle_attendances,
        }

    def handle(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Response:
        """Answer one request."""
        parsed = urlparse(path)
        parts = [part for part in parsed.path.split("/") if part]
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        if parts == ["health"]:
            return 200, {"status": "ok"}
        if parts == ["summary"]:
            return 200, self.services.summary()
        if parts == []:
            return 200, {"collections": sorted(self.routes)}
        if parts[0] not in self.routes or len(parts) > 2:
            return 404, {"error": "unknown resource"}
        item_id: Optional[int] = None
        if len(parts) == 2:
            if parts[1] == "stats":
                method = "STATS"
            elif parts[1].isdigit():
                item_id = int(parts[1])
            else:
                return 404, {"error": "unknown resource"}
        try:
            return self.routes[parts[0]](self.services, method, item_id, query, body or {})
        except ValidationError as exc:
            return 400, {"error": str(exc), "field": exc.field_name}
        except NotFound as exc:
            return 404, {"error": str(exc)}
        except Conflict as exc:
            return 409, {"error": str(exc)}
