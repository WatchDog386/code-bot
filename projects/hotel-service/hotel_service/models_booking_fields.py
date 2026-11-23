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
from .models_guest import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Booking
BOOKING_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "room_id",
    "guest_id",
    "check_in",
    "check_out",
    "guests",
    "total",
    "status",
    "notes",
})


BOOKING_SORTABLE: Tuple[str, ...] = ('id', 'room_id', 'guest_id', 'check_in', 'check_out', 'guests', 'total', 'status',)


BOOKING_REQUIRED: Tuple[str, ...] = ('room_id', 'guest_id', 'check_in', 'check_out',)


def validate_booking_room_id(value: Any) -> int:
    """Check Booking.room_id (ref)."""
    return check_ref("room_id", value)


def validate_booking_guest_id(value: Any) -> int:
    """Check Booking.guest_id (ref)."""
    return check_ref("guest_id", value)


def validate_booking_check_in(value: Any) -> str:
    """Check Booking.check_in (date)."""
    return check_date("check_in", value)


def validate_booking_check_out(value: Any) -> str:
    """Check Booking.check_out (date)."""
    return check_date("check_out", value)


def validate_booking_guests(value: Any) -> int:
    """Check Booking.guests (int)."""
    return check_int("guests", value)


def validate_booking_total(value: Any) -> float:
    """Check Booking.total (money)."""
    return check_money("total", value)


def validate_booking_status(value: Any) -> BookingStatus:
    """Check Booking.status (enum)."""
    return check_choice("status", value, BookingStatus)


def validate_booking_notes(value: Any) -> str:
    """Check Booking.notes (text)."""
    return check_text("notes", value, max_length=2000, required=False)
