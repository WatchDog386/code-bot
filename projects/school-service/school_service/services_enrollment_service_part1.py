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
from .services_course_service import *  # noqa: F401,F403


class EnrollmentServicePart1:
    """Create, change and remove enrollments."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.enrollments

    def create(self, data: Dict[str, Any]) -> Enrollment:
        """Validate and store a new enrollment."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Enrollment.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Enrollment:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("enrollment", item_id)
        return item

    def list(self, **filters: Any) -> List[Enrollment]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ENROLLMENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Enrollment:
        """Change some fields of a enrollment."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a enrollment nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Enrollment) -> None:
        if self.store.courses.get(item.course_id) is None:
            raise NotFound("course", item.course_id)
        if self.store.students.get(item.student_id) is None:
            raise NotFound("student", item.student_id)

    def set_status(self, item_id: int, value: Any) -> Enrollment:
        """Move a enrollment to another status."""
        return self.update(item_id, {"status": value})

    def adjust_final_score(self, item_id: int, delta: float) -> Enrollment:
        item = self.get(item_id)
        return self.update(item_id, {"final_score": round(item.final_score + delta, 2)})
