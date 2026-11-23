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
from .models_prescription_fields import *  # noqa: F401,F403


@dataclass
class Prescription:
    """A prescription record."""

    id: int = 0
    appointment_id: int = 0
    drug: str = ""
    dose_mg: int = 0
    times_per_day: int = 0
    days: int = 0
    refills: int = 0
    notes: str = ""

    def validate(self) -> "Prescription":
        """Check every field and normalise the values in place."""
        self.appointment_id = validate_prescription_appointment_id(self.appointment_id)
        self.drug = validate_prescription_drug(self.drug)
        self.dose_mg = validate_prescription_dose_mg(self.dose_mg)
        self.times_per_day = validate_prescription_times_per_day(self.times_per_day)
        self.days = validate_prescription_days(self.days)
        self.refills = validate_prescription_refills(self.refills)
        self.notes = validate_prescription_notes(self.notes)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "drug": self.drug,
            "dose_mg": self.dose_mg,
            "times_per_day": self.times_per_day,
            "days": self.days,
            "refills": self.refills,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prescription":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, PRESCRIPTION_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "appointment_id" in data:
            item.appointment_id = data["appointment_id"]
        if "drug" in data:
            item.drug = data["drug"]
        if "dose_mg" in data:
            item.dose_mg = data["dose_mg"]
        if "times_per_day" in data:
            item.times_per_day = data["times_per_day"]
        if "days" in data:
            item.days = data["days"]
        if "refills" in data:
            item.refills = data["refills"]
        if "notes" in data:
            item.notes = data["notes"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Prescription":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, PRESCRIPTION_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Prescription #{self.id}: {self.drug}"
