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
from .services_attendance_service import *  # noqa: F401,F403


def sample_teacher(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new teacher (refs point at seeded records)."""
    return {
        "name": f"Teacher name {index}",
        "email": f"teacher{index}@example.com",
        "subject": f"Teacher subject {index}",
        "hired": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "salary": round(10.0 * index + 0.99, 2),
        "full_time": index % 2 == 1,
    }


def sample_student(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new student (refs point at seeded records)."""
    return {
        "name": f"Student name {index}",
        "email": f"student{index}@example.com",
        "birth_date": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "grade_level": index + 1,
        "guardian": f"Student guardian {index}",
        "active": index % 2 == 1,
    }
