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
from .models_appointment_status import *  # noqa: F401,F403


def validate_doctor_room(value: Any) -> str:
    """Check Doctor.room (str)."""
    return check_text("room", value)


def validate_doctor_hourly_rate(value: Any) -> float:
    """Check Doctor.hourly_rate (money)."""
    return check_money("hourly_rate", value)


def validate_doctor_accepting(value: Any) -> bool:
    """Check Doctor.accepting (bool)."""
    return check_flag("accepting", value)
