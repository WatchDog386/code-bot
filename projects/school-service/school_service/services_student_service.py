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
from .services_student_service_part1 import *  # noqa: F401,F403


class StudentService(StudentServicePart1):
    """Create, change and remove students (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every student."""
        return {
            "count": self.repo.count(),
            "total_grade_level": round(self.repo.total_grade_level(), 2),
            "average_grade_level": round(self.repo.average_grade_level(), 2),
            "active": len(self.repo.where_active(True)),
        }
