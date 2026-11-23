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
from .models_enrollment import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Assignment
ASSIGNMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "course_id",
    "title",
    "due",
    "max_points",
    "weight",
    "published",
})


ASSIGNMENT_SORTABLE: Tuple[str, ...] = ('id', 'course_id', 'title', 'due', 'max_points', 'weight',)


ASSIGNMENT_REQUIRED: Tuple[str, ...] = ('course_id', 'title', 'due',)


def validate_assignment_course_id(value: Any) -> int:
    """Check Assignment.course_id (ref)."""
    return check_ref("course_id", value)


def validate_assignment_title(value: Any) -> str:
    """Check Assignment.title (str)."""
    return check_text("title", value)


def validate_assignment_due(value: Any) -> str:
    """Check Assignment.due (date)."""
    return check_date("due", value)


def validate_assignment_max_points(value: Any) -> int:
    """Check Assignment.max_points (int)."""
    return check_int("max_points", value)


def validate_assignment_weight(value: Any) -> float:
    """Check Assignment.weight (float)."""
    return check_number("weight", value)


def validate_assignment_published(value: Any) -> bool:
    """Check Assignment.published (bool)."""
    return check_flag("published", value)
