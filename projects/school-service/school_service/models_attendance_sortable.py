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
from .models_assignment import *  # noqa: F401,F403


ATTENDANCE_SORTABLE: Tuple[str, ...] = ('id', 'student_id', 'course_id', 'day', 'minutes_late',)


ATTENDANCE_REQUIRED: Tuple[str, ...] = ('student_id', 'course_id', 'day',)


def validate_attendance_student_id(value: Any) -> int:
    """Check Attendance.student_id (ref)."""
    return check_ref("student_id", value)


def validate_attendance_course_id(value: Any) -> int:
    """Check Attendance.course_id (ref)."""
    return check_ref("course_id", value)


def validate_attendance_day(value: Any) -> str:
    """Check Attendance.day (date)."""
    return check_date("day", value)


def validate_attendance_present(value: Any) -> bool:
    """Check Attendance.present (bool)."""
    return check_flag("present", value)


def validate_attendance_minutes_late(value: Any) -> int:
    """Check Attendance.minutes_late (int)."""
    return check_int("minutes_late", value)


def validate_attendance_note(value: Any) -> str:
    """Check Attendance.note (text)."""
    return check_text("note", value, max_length=2000, required=False)
