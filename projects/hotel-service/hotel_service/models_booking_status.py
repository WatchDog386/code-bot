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


class BookingStatus(str, Enum):
    """Allowed values of Booking.status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class ChargeCategory(str, Enum):
    """Allowed values of Charge.category."""

    MINIBAR = "minibar"
    RESTAURANT = "restaurant"
    SPA = "spa"
    LAUNDRY = "laundry"
    OTHER = "other"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


# -------------------------------------------------------------------------- RoomType
ROOM_TYPE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "beds",
    "max_guests",
    "nightly_rate",
    "smoking",
})


ROOM_TYPE_SORTABLE: Tuple[str, ...] = ('id', 'name', 'beds', 'max_guests', 'nightly_rate',)


ROOM_TYPE_REQUIRED: Tuple[str, ...] = ('name',)


def validate_room_type_name(value: Any) -> str:
    """Check RoomType.name (str)."""
    return check_text("name", value)


def validate_room_type_beds(value: Any) -> int:
    """Check RoomType.beds (int)."""
    return check_int("beds", value)


def validate_room_type_max_guests(value: Any) -> int:
    """Check RoomType.max_guests (int)."""
    return check_int("max_guests", value)
