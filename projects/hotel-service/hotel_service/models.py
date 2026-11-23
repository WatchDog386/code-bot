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
from .models_validate_housekeeping_room_id import *  # noqa: F401,F403


@dataclass
class Housekeeping:
    """A housekeeping record."""

    id: int = 0
    room_id: int = 0
    cleaned: str = ""
    minutes: int = 0
    staff: str = ""
    inspected: bool = False

    def validate(self) -> "Housekeeping":
        """Check every field and normalise the values in place."""
        self.room_id = validate_housekeeping_room_id(self.room_id)
        self.cleaned = validate_housekeeping_cleaned(self.cleaned)
        self.minutes = validate_housekeeping_minutes(self.minutes)
        self.staff = validate_housekeeping_staff(self.staff)
        self.inspected = validate_housekeeping_inspected(self.inspected)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "cleaned": self.cleaned,
            "minutes": self.minutes,
            "staff": self.staff,
            "inspected": self.inspected,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Housekeeping":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, HOUSEKEEPING_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "room_id" in data:
            item.room_id = data["room_id"]
        if "cleaned" in data:
            item.cleaned = data["cleaned"]
        if "minutes" in data:
            item.minutes = data["minutes"]
        if "staff" in data:
            item.staff = data["staff"]
        if "inspected" in data:
            item.inspected = data["inspected"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Housekeeping":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, HOUSEKEEPING_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Housekeeping #{self.id}: {self.staff}"
