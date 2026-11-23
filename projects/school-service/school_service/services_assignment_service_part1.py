"""Services (continued)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from .models import (
    ASSIGNMENT_FIELDS,
    ATTENDANCE_FIELDS,
    Assignment,
    Attendance,
    COURSE_FIELDS,
    Course,
    ENROLLMENT_FIELDS,
    Enrollment,
    STUDENT_FIELDS,
    Student,
    TEACHER_FIELDS,
    Teacher,
    ValidationError,
)
from .repository import (
    TeacherRepository,
    StudentRepository,
    CourseRepository,
    EnrollmentRepository,
    AssignmentRepository,
    AttendanceRepository,
)
from .services_enrollment_service import *  # noqa: F401,F403


class AssignmentServicePart1:
    """Create, change and remove assignments."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.assignments

    def create(self, data: Dict[str, Any]) -> Assignment:
        """Validate and store a new assignment."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Assignment.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Assignment:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("assignment", item_id)
        return item

    def list(self, **filters: Any) -> List[Assignment]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ASSIGNMENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Assignment:
        """Change some fields of a assignment."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a assignment nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Assignment) -> None:
        if self.store.courses.get(item.course_id) is None:
            raise NotFound("course", item.course_id)

    def adjust_max_points(self, item_id: int, delta: int) -> Assignment:
        """Add `delta` to the max points (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"max_points": item.max_points + delta})

    def adjust_weight(self, item_id: int, delta: float) -> Assignment:
        item = self.get(item_id)
        return self.update(item_id, {"weight": round(item.weight + delta, 2)})

    def toggle_published(self, item_id: int) -> Assignment:
        item = self.get(item_id)
        return self.update(item_id, {"published": not item.published})
