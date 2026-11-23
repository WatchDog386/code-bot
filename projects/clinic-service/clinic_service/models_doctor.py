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
from .models_validate_doctor_room import *  # noqa: F401,F403


@dataclass
class Doctor:
    """A doctor record."""

    id: int = 0
    name: str = ""
    email: str = ""
    specialty: DoctorSpecialty = DoctorSpecialty.GENERAL
    room: str = ""
    hourly_rate: float = 0.0
    accepting: bool = False

    def validate(self) -> "Doctor":
        """Check every field and normalise the values in place."""
        self.name = validate_doctor_name(self.name)
        self.email = validate_doctor_email(self.email)
        self.specialty = validate_doctor_specialty(self.specialty)
        self.room = validate_doctor_room(self.room)
        self.hourly_rate = validate_doctor_hourly_rate(self.hourly_rate)
        self.accepting = validate_doctor_accepting(self.accepting)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "specialty": self.specialty.value,
            "room": self.room,
            "hourly_rate": self.hourly_rate,
            "accepting": self.accepting,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Doctor":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, DOCTOR_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "specialty" in data:
            item.specialty = data["specialty"]
        if "room" in data:
            item.room = data["room"]
        if "hourly_rate" in data:
            item.hourly_rate = data["hourly_rate"]
        if "accepting" in data:
            item.accepting = data["accepting"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Doctor":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, DOCTOR_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Doctor #{self.id}: {self.name}"
