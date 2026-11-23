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
from .services_attendance_service_part1 import *  # noqa: F401,F403


class AttendanceService(AttendanceServicePart1):
    """Create, change and remove attendances (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every attendance."""
        return {
            "count": self.repo.count(),
            "present": len(self.repo.where_present(True)),
            "total_minutes_late": round(self.repo.total_minutes_late(), 2),
            "average_minutes_late": round(self.repo.average_minutes_late(), 2),
        }
