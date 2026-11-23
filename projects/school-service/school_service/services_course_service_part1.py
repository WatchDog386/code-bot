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
from .services_student_service import *  # noqa: F401,F403


class CourseServicePart1:
    """Create, change and remove courses."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.courses

    def create(self, data: Dict[str, Any]) -> Course:
        """Validate and store a new course."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Course.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Course:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("course", item_id)
        return item

    def list(self, **filters: Any) -> List[Course]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in COURSE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Course:
        """Change some fields of a course."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a course nobody points at any more."""
        self.get(item_id)
        if self.store.enrollments.count_for_course(item_id):
            raise Conflict(f"course {item_id} is still used by enrollments")
        if self.store.assignments.count_for_course(item_id):
            raise Conflict(f"course {item_id} is still used by assignments")
        if self.store.attendances.count_for_course(item_id):
            raise Conflict(f"course {item_id} is still used by attendances")
        self.repo.remove(item_id)

    def _check_links(self, item: Course) -> None:
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

    def adjust_credits(self, item_id: int, delta: int) -> Course:
        """Add `delta` to the credits (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"credits": item.credits + delta})
