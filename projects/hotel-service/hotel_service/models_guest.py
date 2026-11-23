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
from .models_validate_guest_country import *  # noqa: F401,F403


@dataclass
class Guest:
    """A guest record."""

    id: int = 0
    name: str = ""
    email: str = ""
    phone: str = ""
    country: str = ""
    vip: bool = False
    loyalty_points: int = 0

    def validate(self) -> "Guest":
        """Check every field and normalise the values in place."""
        self.name = validate_guest_name(self.name)
        self.email = validate_guest_email(self.email)
        self.phone = validate_guest_phone(self.phone)
        self.country = validate_guest_country(self.country)
        self.vip = validate_guest_vip(self.vip)
        self.loyalty_points = validate_guest_loyalty_points(self.loyalty_points)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "country": self.country,
            "vip": self.vip,
            "loyalty_points": self.loyalty_points,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Guest":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, GUEST_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "phone" in data:
            item.phone = data["phone"]
        if "country" in data:
            item.country = data["country"]
        if "vip" in data:
            item.vip = data["vip"]
        if "loyalty_points" in data:
            item.loyalty_points = data["loyalty_points"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Guest":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, GUEST_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Guest #{self.id}: {self.name}"
