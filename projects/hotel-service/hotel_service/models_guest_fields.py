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
from .models_room import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Guest
GUEST_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "phone",
    "country",
    "vip",
    "loyalty_points",
})


GUEST_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'phone', 'country', 'loyalty_points',)


GUEST_REQUIRED: Tuple[str, ...] = ('name', 'email', 'phone', 'country',)


def validate_guest_name(value: Any) -> str:
    """Check Guest.name (str)."""
    return check_text("name", value)


def validate_guest_email(value: Any) -> str:
    """Check Guest.email (email)."""
    return check_email("email", value)


def validate_guest_phone(value: Any) -> str:
    """Check Guest.phone (str)."""
    return check_text("phone", value)
