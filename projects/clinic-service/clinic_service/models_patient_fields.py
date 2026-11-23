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
from .models_doctor import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Patient
PATIENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "phone",
    "birth_date",
    "insurance",
    "allergies",
    "active",
})


PATIENT_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'phone', 'birth_date', 'insurance',)


PATIENT_REQUIRED: Tuple[str, ...] = ('name', 'email', 'phone', 'birth_date', 'insurance',)


def validate_patient_name(value: Any) -> str:
    """Check Patient.name (str)."""
    return check_text("name", value)


def validate_patient_email(value: Any) -> str:
    """Check Patient.email (email)."""
    return check_email("email", value)


def validate_patient_phone(value: Any) -> str:
    """Check Patient.phone (str)."""
    return check_text("phone", value)


def validate_patient_birth_date(value: Any) -> str:
    """Check Patient.birth_date (date)."""
    return check_date("birth_date", value)


def validate_patient_insurance(value: Any) -> str:
    """Check Patient.insurance (str)."""
    return check_text("insurance", value)


def validate_patient_allergies(value: Any) -> str:
    """Check Patient.allergies (text)."""
    return check_text("allergies", value, max_length=2000, required=False)


def validate_patient_active(value: Any) -> bool:
    """Check Patient.active (bool)."""
    return check_flag("active", value)
