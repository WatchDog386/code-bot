"""Models (continued)."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import date
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Tuple, Type

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_INT = 1_000_000_000
from .models_course import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Enrollment
ENROLLMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "course_id",
    "student_id",
    "enrolled",
    "status",
    "final_score",
})


ENROLLMENT_SORTABLE: Tuple[str, ...] = ('id', 'course_id', 'student_id', 'enrolled', 'status', 'final_score',)


ENROLLMENT_REQUIRED: Tuple[str, ...] = ('course_id', 'student_id', 'enrolled',)


def validate_enrollment_course_id(value: Any) -> int:
    """Check Enrollment.course_id (ref)."""
    return check_ref("course_id", value)


def validate_enrollment_student_id(value: Any) -> int:
    """Check Enrollment.student_id (ref)."""
    return check_ref("student_id", value)


def validate_enrollment_enrolled(value: Any) -> str:
    """Check Enrollment.enrolled (date)."""
    return check_date("enrolled", value)


def validate_enrollment_status(value: Any) -> EnrollmentStatus:
    """Check Enrollment.status (enum)."""
    return check_choice("status", value, EnrollmentStatus)


def validate_enrollment_final_score(value: Any) -> float:
    """Check Enrollment.final_score (float)."""
    return check_number("final_score", value)
