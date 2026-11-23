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
from .models_guest_fields import *  # noqa: F401,F403


def validate_guest_country(value: Any) -> str:
    """Check Guest.country (str)."""
    return check_text("country", value)


def validate_guest_vip(value: Any) -> bool:
    """Check Guest.vip (bool)."""
    return check_flag("vip", value)


def validate_guest_loyalty_points(value: Any) -> int:
    """Check Guest.loyalty_points (int)."""
    return check_int("loyalty_points", value)
