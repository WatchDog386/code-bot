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
from .services_enrollment_service_part1 import *  # noqa: F401,F403


class EnrollmentService(EnrollmentServicePart1):
    """Create, change and remove enrollments (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every enrollment."""
        return {
            "count": self.repo.count(),
            "by_status": self.repo.count_by_status(),
            "total_final_score": round(self.repo.total_final_score(), 2),
            "average_final_score": round(self.repo.average_final_score(), 2),
        }
