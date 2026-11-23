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
from .models_validate_lab_result_taken import *  # noqa: F401,F403


@dataclass
class LabResult:
    """A lab result record."""

    id: int = 0
    patient_id: int = 0
    test_name: str = ""
    value: float = 0.0
    unit: str = ""
    taken: str = ""
    flagged: bool = False

    def validate(self) -> "LabResult":
        """Check every field and normalise the values in place."""
        self.patient_id = validate_lab_result_patient_id(self.patient_id)
        self.test_name = validate_lab_result_test_name(self.test_name)
        self.value = validate_lab_result_value(self.value)
        self.unit = validate_lab_result_unit(self.unit)
        self.taken = validate_lab_result_taken(self.taken)
        self.flagged = validate_lab_result_flagged(self.flagged)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "test_name": self.test_name,
            "value": self.value,
            "unit": self.unit,
            "taken": self.taken,
            "flagged": self.flagged,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabResult":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, LAB_RESULT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "patient_id" in data:
            item.patient_id = data["patient_id"]
        if "test_name" in data:
            item.test_name = data["test_name"]
        if "value" in data:
            item.value = data["value"]
        if "unit" in data:
            item.unit = data["unit"]
        if "taken" in data:
            item.taken = data["taken"]
        if "flagged" in data:
            item.flagged = data["flagged"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "LabResult":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, LAB_RESULT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"LabResult #{self.id}: {self.test_name}"
