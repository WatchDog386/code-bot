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
from .models_student import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Course
COURSE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "teacher_id",
    "title",
    "code",
    "credits",
    "room",
    "term",
})


COURSE_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'title', 'code', 'credits', 'room', 'term',)


COURSE_REQUIRED: Tuple[str, ...] = ('teacher_id', 'title', 'code', 'room',)


def validate_course_teacher_id(value: Any) -> int:
    """Check Course.teacher_id (ref)."""
    return check_ref("teacher_id", value)


def validate_course_title(value: Any) -> str:
    """Check Course.title (str)."""
    return check_text("title", value)


def validate_course_code(value: Any) -> str:
    """Check Course.code (str)."""
    return check_text("code", value)


def validate_course_credits(value: Any) -> int:
    """Check Course.credits (int)."""
    return check_int("credits", value)


def validate_course_room(value: Any) -> str:
    """Check Course.room (str)."""
    return check_text("room", value)


def validate_course_term(value: Any) -> CourseTerm:
    """Check Course.term (enum)."""
    return check_choice("term", value, CourseTerm)
