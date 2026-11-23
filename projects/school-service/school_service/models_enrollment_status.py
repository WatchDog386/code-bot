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
from .models_unknown_fields import *  # noqa: F401,F403


class EnrollmentStatus(str, Enum):
    """Allowed values of Enrollment.status."""

    ACTIVE = "active"
    DROPPED = "dropped"
    COMPLETED = "completed"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


# -------------------------------------------------------------------------- Teacher
TEACHER_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "subject",
    "hired",
    "salary",
    "full_time",
})


TEACHER_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'subject', 'hired', 'salary',)


TEACHER_REQUIRED: Tuple[str, ...] = ('name', 'email', 'subject', 'hired',)


def validate_teacher_name(value: Any) -> str:
    """Check Teacher.name (str)."""
    return check_text("name", value)


def validate_teacher_email(value: Any) -> str:
    """Check Teacher.email (email)."""
    return check_email("email", value)


def validate_teacher_subject(value: Any) -> str:
    """Check Teacher.subject (str)."""
    return check_text("subject", value)


def validate_teacher_hired(value: Any) -> str:
    """Check Teacher.hired (date)."""
    return check_date("hired", value)


def validate_teacher_salary(value: Any) -> float:
    """Check Teacher.salary (money)."""
    return check_money("salary", value)


def validate_teacher_full_time(value: Any) -> bool:
    """Check Teacher.full_time (bool)."""
    return check_flag("full_time", value)
