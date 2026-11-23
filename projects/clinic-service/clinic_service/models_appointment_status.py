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
from .models_unknown_fields import *  # noqa: F401,F403


class AppointmentStatus(str, Enum):
    """Allowed values of Appointment.status."""

    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class InvoiceStatus(str, Enum):
    """Allowed values of Invoice.status."""

    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    VOID = "void"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


# -------------------------------------------------------------------------- Doctor
DOCTOR_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "specialty",
    "room",
    "hourly_rate",
    "accepting",
})


DOCTOR_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'specialty', 'room', 'hourly_rate',)


DOCTOR_REQUIRED: Tuple[str, ...] = ('name', 'email', 'room',)


def validate_doctor_name(value: Any) -> str:
    """Check Doctor.name (str)."""
    return check_text("name", value)


def validate_doctor_email(value: Any) -> str:
    """Check Doctor.email (email)."""
    return check_email("email", value)


def validate_doctor_specialty(value: Any) -> DoctorSpecialty:
    """Check Doctor.specialty (enum)."""
    return check_choice("specialty", value, DoctorSpecialty)
