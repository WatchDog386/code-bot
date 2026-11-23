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
from .services_not_found import *  # noqa: F401,F403


class TeacherServicePart1:
    """Create, change and remove teachers."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.teachers

    def create(self, data: Dict[str, Any]) -> Teacher:
        """Validate and store a new teacher."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Teacher.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Teacher:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("teacher", item_id)
        return item

    def list(self, **filters: Any) -> List[Teacher]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in TEACHER_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Teacher:
        """Change some fields of a teacher."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a teacher nobody points at any more."""
        self.get(item_id)
        if self.store.courses.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by courses")
        self.repo.remove(item_id)

    def _check_links(self, item: Teacher) -> None:
        """Teacher doesn't point at other records."""
        return None

    def adjust_salary(self, item_id: int, delta: float) -> Teacher:
        item = self.get(item_id)
        return self.update(item_id, {"salary": round(item.salary + delta, 2)})

    def toggle_full_time(self, item_id: int) -> Teacher:
        item = self.get(item_id)
        return self.update(item_id, {"full_time": not item.full_time})
