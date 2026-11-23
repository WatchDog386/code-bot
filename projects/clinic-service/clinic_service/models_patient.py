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
from .models_patient_fields import *  # noqa: F401,F403


@dataclass
class Patient:
    """A patient record."""

    id: int = 0
    name: str = ""
    email: str = ""
    phone: str = ""
    birth_date: str = ""
    insurance: str = ""
    allergies: str = ""
    active: bool = False

    def validate(self) -> "Patient":
        """Check every field and normalise the values in place."""
        self.name = validate_patient_name(self.name)
        self.email = validate_patient_email(self.email)
        self.phone = validate_patient_phone(self.phone)
        self.birth_date = validate_patient_birth_date(self.birth_date)
        self.insurance = validate_patient_insurance(self.insurance)
        self.allergies = validate_patient_allergies(self.allergies)
        self.active = validate_patient_active(self.active)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "birth_date": self.birth_date,
            "insurance": self.insurance,
            "allergies": self.allergies,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Patient":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, PATIENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "phone" in data:
            item.phone = data["phone"]
        if "birth_date" in data:
            item.birth_date = data["birth_date"]
        if "insurance" in data:
            item.insurance = data["insurance"]
        if "allergies" in data:
            item.allergies = data["allergies"]
        if "active" in data:
            item.active = data["active"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Patient":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, PATIENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Patient #{self.id}: {self.name}"
