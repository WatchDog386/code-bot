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
from .models_charge import *  # noqa: F401,F403


def validate_housekeeping_room_id(value: Any) -> int:
    """Check Housekeeping.room_id (ref)."""
    return check_ref("room_id", value)


def validate_housekeeping_cleaned(value: Any) -> str:
    """Check Housekeeping.cleaned (date)."""
    return check_date("cleaned", value)


def validate_housekeeping_minutes(value: Any) -> int:
    """Check Housekeeping.minutes (int)."""
    return check_int("minutes", value)


def validate_housekeeping_staff(value: Any) -> str:
    """Check Housekeeping.staff (str)."""
    return check_text("staff", value)


def validate_housekeeping_inspected(value: Any) -> bool:
    """Check Housekeeping.inspected (bool)."""
    return check_flag("inspected", value)
