"""HTTP API for the School Records service (standard library only).

Run it with   python -m school_service.api   and open http://127.0.0.1:8000/health

Every collection supports GET (list, with filters, ?q= search, ?sort=, ?page=&size=),
POST, GET /<id>, PATCH /<id>, DELETE /<id> and GET /stats.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .config import Settings
from .models import (
    ADDRESS_SORTABLE,
    ASSIGNMENT_SORTABLE,
    ATTENDANCE_SORTABLE,
    AUDIT_ENTRY_SORTABLE,
    AuditEntryAction,
    CONTACT_PERSON_SORTABLE,
    COURSE_SORTABLE,
    CourseTerm,
    DISCOUNT_SORTABLE,
    DOCUMENT_SORTABLE,
    ENROLLMENT_SORTABLE,
    EnrollmentStatus,
    NOTE_SORTABLE,
    NOTIFICATION_SORTABLE,
    NotificationChannel,
    REMINDER_SORTABLE,
    REVIEW_SORTABLE,
    ReminderPriority,
    SETTING_SORTABLE,
    STUDENT_SORTABLE,
    TAG_SORTABLE,
    TEACHER_SORTABLE,
    ValidationError,
    check_choice,
    check_date,
)
from .services import Conflict, NotFound, Services

Response = Tuple[int, Any]
Query = Dict[str, str]


def query_int(query: Query, name: str, default: int = 0) -> int:
    raw = query.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(name, "must be a whole number") from None


def query_number(query: Query, name: str) -> float:
    try:
        return float(query[name])
    except ValueError:
        raise ValidationError(name, "must be a number") from None


def query_flag(query: Query, name: str) -> bool:
    raw = query[name].lower()
    if raw in ("1", "true", "yes"):
        return True
    if raw in ("0", "false", "no"):
        return False
    raise ValidationError(name, "must be true or false")


def paginate(items: List[Any], query: Query) -> List[Dict[str, Any]]:
    page = max(1, query_int(query, "page", 1))
    size = min(200, max(1, query_int(query, "size", 50)))
    start = (page - 1) * size
    return [item.to_dict() for item in items[start:start + size]]


def sort_items(items: List[Any], query: Query, allowed: Tuple[str, ...]) -> List[Any]:
    key = query.get("sort")
    if not key:
        return items
    reverse = key.startswith("-")
    key = key.lstrip("-")
    if key not in allowed:
        raise ValidationError("sort", "can't sort on " + key)
    return sorted(items, key=lambda item: getattr(item, key), reverse=reverse)


class Api:
    """Maps HTTP requests onto the services and returns (status, payload)."""

    def __init__(self, services: Optional[Services] = None) -> None:
        self.services = services or Services()
        self.routes: Dict[str, Callable[[str, Optional[int], Query, Dict[str, Any]], Response]] = {
            "teachers": self.teachers,
            "students": self.students,
            "courses": self.courses,
            "enrollments": self.enrollments,
            "assignments": self.assignments,
            "attendances": self.attendances,
            "documents": self.documents,
            "notifications": self.notifications,
            "addresses": self.addresses,
            "reminders": self.reminders,
            "settings": self.settings,
            "audit-entries": self.audit_entries,
            "notes": self.notes,
            "reviews": self.reviews,
            "contact-persons": self.contact_persons,
            "discounts": self.discounts,
            "tags": self.tags,
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
            return self.routes[parts[0]](method, item_id, query, body or {})
        except ValidationError as exc:
            return 400, {"error": str(exc), "field": exc.field_name}
        except NotFound as exc:
            return 404, {"error": str(exc)}
        except Conflict as exc:
            return 409, {"error": str(exc)}

    def teachers(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.teachers
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_teachers(query)
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

    def list_teachers(self, query: Query) -> List[Dict[str, Any]]:
        """Teachers matching the query-string filters."""
        repo = self.services.store.teachers
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

    def students(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.students
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_students(query)
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

    def list_students(self, query: Query) -> List[Dict[str, Any]]:
        """Students matching the query-string filters."""
        repo = self.services.store.students
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

    def courses(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.courses
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_courses(query)
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

    def list_courses(self, query: Query) -> List[Dict[str, Any]]:
        """Courses matching the query-string filters."""
        repo = self.services.store.courses
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

    def enrollments(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.enrollments
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_enrollments(query)
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

    def list_enrollments(self, query: Query) -> List[Dict[str, Any]]:
        """Enrollments matching the query-string filters."""
        repo = self.services.store.enrollments
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

    def assignments(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.assignments
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_assignments(query)
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

    def list_assignments(self, query: Query) -> List[Dict[str, Any]]:
        """Assignments matching the query-string filters."""
        repo = self.services.store.assignments
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

    def attendances(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.attendances
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_attendances(query)
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

    def list_attendances(self, query: Query) -> List[Dict[str, Any]]:
        """Attendances matching the query-string filters."""
        repo = self.services.store.attendances
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

    def documents(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.documents
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_documents(query)
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

    def list_documents(self, query: Query) -> List[Dict[str, Any]]:
        """Documents matching the query-string filters."""
        repo = self.services.store.documents
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "title" in query:
            items = [item for item in items if item.title == query["title"]]
        if "min_pages" in query:
            limit = query_number(query, "min_pages")
            items = [item for item in items if item.pages >= limit]
        if "max_pages" in query:
            limit = query_number(query, "max_pages")
            items = [item for item in items if item.pages <= limit]
        if "signed" in query:
            flag = query_flag(query, "signed")
            items = [item for item in items if item.signed is flag]
        if "min_version" in query:
            limit = query_number(query, "min_version")
            items = [item for item in items if item.version >= limit]
        if "max_version" in query:
            limit = query_number(query, "max_version")
            items = [item for item in items if item.version <= limit]
        if "issued_from" in query:
            day = check_date("issued_from", query["issued_from"])
            items = [item for item in items if item.issued >= day]
        if "issued_to" in query:
            day = check_date("issued_to", query["issued_to"])
            items = [item for item in items if item.issued <= day]
        items = sort_items(items, query, DOCUMENT_SORTABLE)
        return paginate(items, query)

    def notifications(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.notifications
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_notifications(query)
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

    def list_notifications(self, query: Query) -> List[Dict[str, Any]]:
        """Notifications matching the query-string filters."""
        repo = self.services.store.notifications
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "recipient" in query:
            items = [item for item in items if item.recipient == query["recipient"]]
        if "title" in query:
            items = [item for item in items if item.title == query["title"]]
        if "sent_from" in query:
            day = check_date("sent_from", query["sent_from"])
            items = [item for item in items if item.sent >= day]
        if "sent_to" in query:
            day = check_date("sent_to", query["sent_to"])
            items = [item for item in items if item.sent <= day]
        if "channel" in query:
            wanted = check_choice("channel", query["channel"], NotificationChannel)
            items = [item for item in items if item.channel == wanted]
        if "read" in query:
            flag = query_flag(query, "read")
            items = [item for item in items if item.read is flag]
        items = sort_items(items, query, NOTIFICATION_SORTABLE)
        return paginate(items, query)

    def addresses(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.addresses
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_addresses(query)
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

    def list_addresses(self, query: Query) -> List[Dict[str, Any]]:
        """Addresses matching the query-string filters."""
        repo = self.services.store.addresses
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "street" in query:
            items = [item for item in items if item.street == query["street"]]
        if "city" in query:
            items = [item for item in items if item.city == query["city"]]
        if "postcode" in query:
            items = [item for item in items if item.postcode == query["postcode"]]
        if "country" in query:
            items = [item for item in items if item.country == query["country"]]
        if "billing" in query:
            flag = query_flag(query, "billing")
            items = [item for item in items if item.billing is flag]
        items = sort_items(items, query, ADDRESS_SORTABLE)
        return paginate(items, query)

    def reminders(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.reminders
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_reminders(query)
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

    def list_reminders(self, query: Query) -> List[Dict[str, Any]]:
        """Reminders matching the query-string filters."""
        repo = self.services.store.reminders
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "title" in query:
            items = [item for item in items if item.title == query["title"]]
        if "remind_on_from" in query:
            day = check_date("remind_on_from", query["remind_on_from"])
            items = [item for item in items if item.remind_on >= day]
        if "remind_on_to" in query:
            day = check_date("remind_on_to", query["remind_on_to"])
            items = [item for item in items if item.remind_on <= day]
        if "done" in query:
            flag = query_flag(query, "done")
            items = [item for item in items if item.done is flag]
        if "priority" in query:
            wanted = check_choice("priority", query["priority"], ReminderPriority)
            items = [item for item in items if item.priority == wanted]
        items = sort_items(items, query, REMINDER_SORTABLE)
        return paginate(items, query)

    def settings(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.settings
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_settings(query)
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

    def list_settings(self, query: Query) -> List[Dict[str, Any]]:
        """Settings matching the query-string filters."""
        repo = self.services.store.settings
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "key_name" in query:
            items = [item for item in items if item.key_name == query["key_name"]]
        if "value" in query:
            items = [item for item in items if item.value == query["value"]]
        if "editable" in query:
            flag = query_flag(query, "editable")
            items = [item for item in items if item.editable is flag]
        if "changed_from" in query:
            day = check_date("changed_from", query["changed_from"])
            items = [item for item in items if item.changed >= day]
        if "changed_to" in query:
            day = check_date("changed_to", query["changed_to"])
            items = [item for item in items if item.changed <= day]
        items = sort_items(items, query, SETTING_SORTABLE)
        return paginate(items, query)

    def audit_entries(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.audit_entries
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_audit_entries(query)
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

    def list_audit_entries(self, query: Query) -> List[Dict[str, Any]]:
        """Audit entries matching the query-string filters."""
        repo = self.services.store.audit_entries
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "actor" in query:
            items = [item for item in items if item.actor == query["actor"]]
        if "action" in query:
            wanted = check_choice("action", query["action"], AuditEntryAction)
            items = [item for item in items if item.action == wanted]
        if "at_from" in query:
            day = check_date("at_from", query["at_from"])
            items = [item for item in items if item.at >= day]
        if "at_to" in query:
            day = check_date("at_to", query["at_to"])
            items = [item for item in items if item.at <= day]
        if "details" in query:
            items = [item for item in items if item.details == query["details"]]
        items = sort_items(items, query, AUDIT_ENTRY_SORTABLE)
        return paginate(items, query)

    def notes(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.notes
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_notes(query)
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

    def list_notes(self, query: Query) -> List[Dict[str, Any]]:
        """Notes matching the query-string filters."""
        repo = self.services.store.notes
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "subject" in query:
            items = [item for item in items if item.subject == query["subject"]]
        if "body" in query:
            items = [item for item in items if item.body == query["body"]]
        if "pinned" in query:
            flag = query_flag(query, "pinned")
            items = [item for item in items if item.pinned is flag]
        if "written_from" in query:
            day = check_date("written_from", query["written_from"])
            items = [item for item in items if item.written >= day]
        if "written_to" in query:
            day = check_date("written_to", query["written_to"])
            items = [item for item in items if item.written <= day]
        items = sort_items(items, query, NOTE_SORTABLE)
        return paginate(items, query)

    def reviews(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.reviews
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_reviews(query)
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

    def list_reviews(self, query: Query) -> List[Dict[str, Any]]:
        """Reviews matching the query-string filters."""
        repo = self.services.store.reviews
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "author" in query:
            items = [item for item in items if item.author == query["author"]]
        if "min_stars" in query:
            limit = query_number(query, "min_stars")
            items = [item for item in items if item.stars >= limit]
        if "max_stars" in query:
            limit = query_number(query, "max_stars")
            items = [item for item in items if item.stars <= limit]
        if "comment" in query:
            items = [item for item in items if item.comment == query["comment"]]
        if "verified" in query:
            flag = query_flag(query, "verified")
            items = [item for item in items if item.verified is flag]
        if "posted_from" in query:
            day = check_date("posted_from", query["posted_from"])
            items = [item for item in items if item.posted >= day]
        if "posted_to" in query:
            day = check_date("posted_to", query["posted_to"])
            items = [item for item in items if item.posted <= day]
        items = sort_items(items, query, REVIEW_SORTABLE)
        return paginate(items, query)

    def contact_persons(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.contact_persons
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_contact_persons(query)
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

    def list_contact_persons(self, query: Query) -> List[Dict[str, Any]]:
        """Contact persons matching the query-string filters."""
        repo = self.services.store.contact_persons
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "name" in query:
            items = [item for item in items if item.name == query["name"]]
        if "email" in query:
            items = [item for item in items if item.email == query["email"]]
        if "phone" in query:
            items = [item for item in items if item.phone == query["phone"]]
        if "role" in query:
            items = [item for item in items if item.role == query["role"]]
        if "primary" in query:
            flag = query_flag(query, "primary")
            items = [item for item in items if item.primary is flag]
        items = sort_items(items, query, CONTACT_PERSON_SORTABLE)
        return paginate(items, query)

    def discounts(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.discounts
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_discounts(query)
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

    def list_discounts(self, query: Query) -> List[Dict[str, Any]]:
        """Discounts matching the query-string filters."""
        repo = self.services.store.discounts
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "code" in query:
            items = [item for item in items if item.code == query["code"]]
        if "min_percent" in query:
            limit = query_number(query, "min_percent")
            items = [item for item in items if item.percent >= limit]
        if "max_percent" in query:
            limit = query_number(query, "max_percent")
            items = [item for item in items if item.percent <= limit]
        if "starts_from" in query:
            day = check_date("starts_from", query["starts_from"])
            items = [item for item in items if item.starts >= day]
        if "starts_to" in query:
            day = check_date("starts_to", query["starts_to"])
            items = [item for item in items if item.starts <= day]
        if "ends_from" in query:
            day = check_date("ends_from", query["ends_from"])
            items = [item for item in items if item.ends >= day]
        if "ends_to" in query:
            day = check_date("ends_to", query["ends_to"])
            items = [item for item in items if item.ends <= day]
        if "active" in query:
            flag = query_flag(query, "active")
            items = [item for item in items if item.active is flag]
        items = sort_items(items, query, DISCOUNT_SORTABLE)
        return paginate(items, query)

    def tags(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:
        service = self.services.tags
        if method == "STATS":
            return 200, service.stats()
        if item_id is None:
            if method == "GET":
                return 200, self.list_tags(query)
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

    def list_tags(self, query: Query) -> List[Dict[str, Any]]:
        """Tags matching the query-string filters."""
        repo = self.services.store.tags
        items = repo.list()
        if "q" in query:
            hits = {item.id for item in repo.search(query["q"])}
            items = [item for item in items if item.id in hits]
        if "teacher_id" in query:
            wanted_id = query_int(query, "teacher_id")
            items = [item for item in items if item.teacher_id == wanted_id]
        if "label" in query:
            items = [item for item in items if item.label == query["label"]]
        if "color" in query:
            items = [item for item in items if item.color == query["color"]]
        if "min_usage" in query:
            limit = query_number(query, "min_usage")
            items = [item for item in items if item.usage >= limit]
        if "max_usage" in query:
            limit = query_number(query, "max_usage")
            items = [item for item in items if item.usage <= limit]
        items = sort_items(items, query, TAG_SORTABLE)
        return paginate(items, query)


class Handler(BaseHTTPRequestHandler):
    """Turns HTTP requests into `Api.handle` calls."""

    api = Api()

    def _respond(self, status: int, payload: Any) -> None:
        data = b"" if payload is None else json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self, method: str) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = None
        if length:
            try:
                body = json.loads(self.rfile.read(length))
            except ValueError:
                self._respond(400, {"error": "invalid JSON"})
                return
        status, payload = self.api.handle(method, self.path, body)
        self._respond(status, payload)

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    def do_PATCH(self) -> None:  # noqa: N802
        self._dispatch("PATCH")

    def do_PUT(self) -> None:  # noqa: N802
        self._dispatch("PUT")

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch("DELETE")


def main(port: Optional[int] = None) -> None:
    """Seed some sample data and serve until Ctrl+C."""
    settings = Settings.from_env()
    if port is not None:
        settings = Settings(host=settings.host, port=port, seed_size=settings.seed_size)
    api = Api()
    api.services.seed(settings.seed_size)
    Handler.api = api
    server = ThreadingHTTPServer((settings.host, settings.port), Handler)
    print(f"School Records API on http://{settings.host}:{settings.port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
