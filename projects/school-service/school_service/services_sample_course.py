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
from .services_sample_teacher import *  # noqa: F401,F403


def sample_course(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new course (refs point at seeded records)."""
    return {
        "teacher_id": (index - 1) % 3 + 1,
        "title": f"Course title {index}",
        "code": f"Course code {index}",
        "credits": index + 1,
        "room": f"Course room {index}",
        "term": ['fall', 'spring', 'summer'][index % 3],
    }


def sample_enrollment(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new enrollment (refs point at seeded records)."""
    return {
        "course_id": (index - 1) % 3 + 1,
        "student_id": (index - 1) % 3 + 1,
        "enrolled": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "status": ['active', 'dropped', 'completed'][index % 3],
        "final_score": round(1.5 * index + 0.25, 2),
    }


def sample_assignment(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new assignment (refs point at seeded records)."""
    return {
        "course_id": (index - 1) % 3 + 1,
        "title": f"Assignment title {index}",
        "due": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "max_points": index + 1,
        "weight": round(1.5 * index + 0.25, 2),
        "published": index % 2 == 1,
    }


def sample_attendance(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new attendance (refs point at seeded records)."""
    return {
        "student_id": (index - 1) % 3 + 1,
        "course_id": (index - 1) % 3 + 1,
        "day": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "present": index % 2 == 1,
        "minutes_late": index + 1,
        "note": f"Notes about attendance {index}.",
    }
