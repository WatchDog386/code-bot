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
from .models_validate_room_type_nightly_rat import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Room
ROOM_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "room_type_id",
    "number",
    "floor",
    "status",
    "sea_view",
})


ROOM_SORTABLE: Tuple[str, ...] = ('id', 'room_type_id', 'number', 'floor', 'status',)


ROOM_REQUIRED: Tuple[str, ...] = ('room_type_id', 'number',)


def validate_room_room_type_id(value: Any) -> int:
    """Check Room.room_type_id (ref)."""
    return check_ref("room_type_id", value)


def validate_room_number(value: Any) -> str:
    """Check Room.number (str)."""
    return check_text("number", value)


def validate_room_floor(value: Any) -> int:
    """Check Room.floor (int)."""
    return check_int("floor", value)


def validate_room_status(value: Any) -> RoomStatus:
    """Check Room.status (enum)."""
    return check_choice("status", value, RoomStatus)


def validate_room_sea_view(value: Any) -> bool:
    """Check Room.sea_view (bool)."""
    return check_flag("sea_view", value)
