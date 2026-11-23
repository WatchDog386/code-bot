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
from .services_teacher_service_part1 import *  # noqa: F401,F403


class TeacherService(TeacherServicePart1):
    """Create, change and remove teachers (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every teacher."""
        return {
            "count": self.repo.count(),
            "total_salary": round(self.repo.total_salary(), 2),
            "average_salary": round(self.repo.average_salary(), 2),
            "full_time": len(self.repo.where_full_time(True)),
        }
