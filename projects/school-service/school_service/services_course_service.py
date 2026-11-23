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
from .services_course_service_part1 import *  # noqa: F401,F403


class CourseService(CourseServicePart1):
    """Create, change and remove courses (continued)."""

    def set_term(self, item_id: int, value: Any) -> Course:
        """Move a course to another term."""
        return self.update(item_id, {"term": value})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every course."""
        return {
            "count": self.repo.count(),
            "total_credits": round(self.repo.total_credits(), 2),
            "average_credits": round(self.repo.average_credits(), 2),
            "by_term": self.repo.count_by_term(),
        }
