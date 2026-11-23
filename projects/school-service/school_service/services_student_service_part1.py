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
from .services_teacher_service import *  # noqa: F401,F403


class StudentServicePart1:
    """Create, change and remove students."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.students

    def create(self, data: Dict[str, Any]) -> Student:
        """Validate and store a new student."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Student.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Student:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("student", item_id)
        return item

    def list(self, **filters: Any) -> List[Student]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in STUDENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Student:
        """Change some fields of a student."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a student nobody points at any more."""
        self.get(item_id)
        if self.store.enrollments.count_for_student(item_id):
            raise Conflict(f"student {item_id} is still used by enrollments")
        if self.store.attendances.count_for_student(item_id):
            raise Conflict(f"student {item_id} is still used by attendances")
        self.repo.remove(item_id)

    def _check_links(self, item: Student) -> None:
        """Student doesn't point at other records."""
        return None

    def adjust_grade_level(self, item_id: int, delta: int) -> Student:
        """Add `delta` to the grade level (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"grade_level": item.grade_level + delta})

    def toggle_active(self, item_id: int) -> Student:
        item = self.get(item_id)
        return self.update(item_id, {"active": not item.active})
