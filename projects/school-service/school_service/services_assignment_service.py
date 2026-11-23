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
from .services_assignment_service_part1 import *  # noqa: F401,F403


class AssignmentService(AssignmentServicePart1):
    """Create, change and remove assignments (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every assignment."""
        return {
            "count": self.repo.count(),
            "total_max_points": round(self.repo.total_max_points(), 2),
            "average_max_points": round(self.repo.average_max_points(), 2),
            "total_weight": round(self.repo.total_weight(), 2),
            "average_weight": round(self.repo.average_weight(), 2),
            "published": len(self.repo.where_published(True)),
        }
