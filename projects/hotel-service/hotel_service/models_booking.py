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
from .models_booking_fields import *  # noqa: F401,F403


@dataclass
class Booking:
    """A booking record."""

    id: int = 0
    room_id: int = 0
    guest_id: int = 0
    check_in: str = ""
    check_out: str = ""
    guests: int = 0
    total: float = 0.0
    status: BookingStatus = BookingStatus.PENDING
    notes: str = ""

    def validate(self) -> "Booking":
        """Check every field and normalise the values in place."""
        self.room_id = validate_booking_room_id(self.room_id)
        self.guest_id = validate_booking_guest_id(self.guest_id)
        self.check_in = validate_booking_check_in(self.check_in)
        self.check_out = validate_booking_check_out(self.check_out)
        self.guests = validate_booking_guests(self.guests)
        self.total = validate_booking_total(self.total)
        self.status = validate_booking_status(self.status)
        self.notes = validate_booking_notes(self.notes)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "guest_id": self.guest_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "guests": self.guests,
            "total": self.total,
            "status": self.status.value,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Booking":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, BOOKING_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "room_id" in data:
            item.room_id = data["room_id"]
        if "guest_id" in data:
            item.guest_id = data["guest_id"]
        if "check_in" in data:
            item.check_in = data["check_in"]
        if "check_out" in data:
            item.check_out = data["check_out"]
        if "guests" in data:
            item.guests = data["guests"]
        if "total" in data:
            item.total = data["total"]
        if "status" in data:
            item.status = data["status"]
        if "notes" in data:
            item.notes = data["notes"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Booking":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, BOOKING_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Booking #{self.id}"
