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
from .models_appointment import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Prescription
PRESCRIPTION_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "appointment_id",
    "drug",
    "dose_mg",
    "times_per_day",
    "days",
    "refills",
    "notes",
})


PRESCRIPTION_SORTABLE: Tuple[str, ...] = ('id', 'appointment_id', 'drug', 'dose_mg', 'times_per_day', 'days', 'refills',)


PRESCRIPTION_REQUIRED: Tuple[str, ...] = ('appointment_id', 'drug',)


def validate_prescription_appointment_id(value: Any) -> int:
    """Check Prescription.appointment_id (ref)."""
    return check_ref("appointment_id", value)


def validate_prescription_drug(value: Any) -> str:
    """Check Prescription.drug (str)."""
    return check_text("drug", value)


def validate_prescription_dose_mg(value: Any) -> int:
    """Check Prescription.dose_mg (int)."""
    return check_int("dose_mg", value)


def validate_prescription_times_per_day(value: Any) -> int:
    """Check Prescription.times_per_day (int)."""
    return check_int("times_per_day", value)


def validate_prescription_days(value: Any) -> int:
    """Check Prescription.days (int)."""
    return check_int("days", value)


def validate_prescription_refills(value: Any) -> int:
    """Check Prescription.refills (int)."""
    return check_int("refills", value)


def validate_prescription_notes(value: Any) -> str:
    """Check Prescription.notes (text)."""
    return check_text("notes", value, max_length=2000, required=False)
