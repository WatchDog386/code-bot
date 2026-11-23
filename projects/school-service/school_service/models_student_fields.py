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
from .models_teacher import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Student
STUDENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "birth_date",
    "grade_level",
    "guardian",
    "active",
})


STUDENT_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'birth_date', 'grade_level', 'guardian',)


STUDENT_REQUIRED: Tuple[str, ...] = ('name', 'email', 'birth_date', 'guardian',)


def validate_student_name(value: Any) -> str:
    """Check Student.name (str)."""
    return check_text("name", value)


def validate_student_email(value: Any) -> str:
    """Check Student.email (email)."""
    return check_email("email", value)


def validate_student_birth_date(value: Any) -> str:
    """Check Student.birth_date (date)."""
    return check_date("birth_date", value)


def validate_student_grade_level(value: Any) -> int:
    """Check Student.grade_level (int)."""
    return check_int("grade_level", value)


def validate_student_guardian(value: Any) -> str:
    """Check Student.guardian (str)."""
    return check_text("guardian", value)
