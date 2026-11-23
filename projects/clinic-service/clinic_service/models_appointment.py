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
from .models_validate_appointment_fee import *  # noqa: F401,F403


@dataclass
class Appointment:
    """A appointment record."""

    id: int = 0
    doctor_id: int = 0
    patient_id: int = 0
    day: str = ""
    slot: int = 0
    duration: int = 0
    reason: str = ""
    status: AppointmentStatus = AppointmentStatus.BOOKED
    fee: float = 0.0

    def validate(self) -> "Appointment":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_appointment_doctor_id(self.doctor_id)
        self.patient_id = validate_appointment_patient_id(self.patient_id)
        self.day = validate_appointment_day(self.day)
        self.slot = validate_appointment_slot(self.slot)
        self.duration = validate_appointment_duration(self.duration)
        self.reason = validate_appointment_reason(self.reason)
        self.status = validate_appointment_status(self.status)
        self.fee = validate_appointment_fee(self.fee)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
            "day": self.day,
            "slot": self.slot,
            "duration": self.duration,
            "reason": self.reason,
            "status": self.status.value,
            "fee": self.fee,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Appointment":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, APPOINTMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "patient_id" in data:
            item.patient_id = data["patient_id"]
        if "day" in data:
            item.day = data["day"]
        if "slot" in data:
            item.slot = data["slot"]
        if "duration" in data:
            item.duration = data["duration"]
        if "reason" in data:
            item.reason = data["reason"]
        if "status" in data:
            item.status = data["status"]
        if "fee" in data:
            item.fee = data["fee"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Appointment":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, APPOINTMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Appointment #{self.id}"
