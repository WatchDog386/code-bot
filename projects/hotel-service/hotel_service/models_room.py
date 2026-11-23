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
from .models_room_fields import *  # noqa: F401,F403


@dataclass
class Room:
    """A room record."""

    id: int = 0
    room_type_id: int = 0
    number: str = ""
    floor: int = 0
    status: RoomStatus = RoomStatus.CLEAN
    sea_view: bool = False

    def validate(self) -> "Room":
        """Check every field and normalise the values in place."""
        self.room_type_id = validate_room_room_type_id(self.room_type_id)
        self.number = validate_room_number(self.number)
        self.floor = validate_room_floor(self.floor)
        self.status = validate_room_status(self.status)
        self.sea_view = validate_room_sea_view(self.sea_view)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "room_type_id": self.room_type_id,
            "number": self.number,
            "floor": self.floor,
            "status": self.status.value,
            "sea_view": self.sea_view,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Room":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ROOM_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "room_type_id" in data:
            item.room_type_id = data["room_type_id"]
        if "number" in data:
            item.number = data["number"]
        if "floor" in data:
            item.floor = data["floor"]
        if "status" in data:
            item.status = data["status"]
        if "sea_view" in data:
            item.sea_view = data["sea_view"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Room":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ROOM_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Room #{self.id}: {self.number}"
