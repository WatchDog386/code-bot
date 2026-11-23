"""Business rules for the School Records service: validation, links between records
(a record can't point at something that doesn't exist, and can't be deleted while
others still point at it), small domain operations and statistics.
"""

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


class NotFound(LookupError):
    """No record with that id."""

    def __init__(self, entity: str, item_id: int) -> None:
        super().__init__(f"{entity} {item_id} not found")
        self.entity = entity
        self.item_id = item_id


class Conflict(ValueError):
    """The change would break a link between records."""


def plain(value: Any) -> str:
    """A value as the text a query string would carry."""
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class Store:
    """Every repository of the service."""

    def __init__(self) -> None:
        self.teachers = TeacherRepository()
        self.students = StudentRepository()
        self.courses = CourseRepository()
        self.enrollments = EnrollmentRepository()
        self.assignments = AssignmentRepository()
        self.attendances = AttendanceRepository()

    def counts(self) -> Dict[str, int]:
        return {
            "teachers": self.teachers.count(),
            "students": self.students.count(),
            "courses": self.courses.count(),
            "enrollments": self.enrollments.count(),
            "assignments": self.assignments.count(),
            "attendances": self.attendances.count(),
        }
