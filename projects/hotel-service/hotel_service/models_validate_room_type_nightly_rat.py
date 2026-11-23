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
from .models_booking_status import *  # noqa: F401,F403


def validate_room_type_nightly_rate(value: Any) -> float:
    """Check RoomType.nightly_rate (money)."""
    return check_money("nightly_rate", value)


def validate_room_type_smoking(value: Any) -> bool:
    """Check RoomType.smoking (bool)."""
    return check_flag("smoking", value)


@dataclass
class RoomType:
    """A room type record."""

    id: int = 0
    name: str = ""
    beds: int = 0
    max_guests: int = 0
    nightly_rate: float = 0.0
    smoking: bool = False

    def validate(self) -> "RoomType":
        """Check every field and normalise the values in place."""
        self.name = validate_room_type_name(self.name)
        self.beds = validate_room_type_beds(self.beds)
        self.max_guests = validate_room_type_max_guests(self.max_guests)
        self.nightly_rate = validate_room_type_nightly_rate(self.nightly_rate)
        self.smoking = validate_room_type_smoking(self.smoking)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "beds": self.beds,
            "max_guests": self.max_guests,
            "nightly_rate": self.nightly_rate,
            "smoking": self.smoking,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoomType":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ROOM_TYPE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "beds" in data:
            item.beds = data["beds"]
        if "max_guests" in data:
            item.max_guests = data["max_guests"]
        if "nightly_rate" in data:
            item.nightly_rate = data["nightly_rate"]
        if "smoking" in data:
            item.smoking = data["smoking"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "RoomType":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ROOM_TYPE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"RoomType #{self.id}: {self.name}"
