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
from .models_charge_fields import *  # noqa: F401,F403


@dataclass
class Charge:
    """A charge record."""

    id: int = 0
    booking_id: int = 0
    description: str = ""
    amount: float = 0.0
    posted: str = ""
    category: ChargeCategory = ChargeCategory.MINIBAR

    def validate(self) -> "Charge":
        """Check every field and normalise the values in place."""
        self.booking_id = validate_charge_booking_id(self.booking_id)
        self.description = validate_charge_description(self.description)
        self.amount = validate_charge_amount(self.amount)
        self.posted = validate_charge_posted(self.posted)
        self.category = validate_charge_category(self.category)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "description": self.description,
            "amount": self.amount,
            "posted": self.posted,
            "category": self.category.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Charge":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, CHARGE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "booking_id" in data:
            item.booking_id = data["booking_id"]
        if "description" in data:
            item.description = data["description"]
        if "amount" in data:
            item.amount = data["amount"]
        if "posted" in data:
            item.posted = data["posted"]
        if "category" in data:
            item.category = data["category"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Charge":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, CHARGE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Charge #{self.id}: {self.description}"


# -------------------------------------------------------------------------- Housekeeping
HOUSEKEEPING_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "room_id",
    "cleaned",
    "minutes",
    "staff",
    "inspected",
})


HOUSEKEEPING_SORTABLE: Tuple[str, ...] = ('id', 'room_id', 'cleaned', 'minutes', 'staff',)


HOUSEKEEPING_REQUIRED: Tuple[str, ...] = ('room_id', 'cleaned', 'staff',)
