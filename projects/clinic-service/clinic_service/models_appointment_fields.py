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
from .models_patient import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Appointment
APPOINTMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "patient_id",
    "day",
    "slot",
    "duration",
    "reason",
    "status",
    "fee",
})


APPOINTMENT_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'patient_id', 'day', 'slot', 'duration', 'status', 'fee',)


APPOINTMENT_REQUIRED: Tuple[str, ...] = ('doctor_id', 'patient_id', 'day',)


def validate_appointment_doctor_id(value: Any) -> int:
    """Check Appointment.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_appointment_patient_id(value: Any) -> int:
    """Check Appointment.patient_id (ref)."""
    return check_ref("patient_id", value)


def validate_appointment_day(value: Any) -> str:
    """Check Appointment.day (date)."""
    return check_date("day", value)


def validate_appointment_slot(value: Any) -> int:
    """Check Appointment.slot (int)."""
    return check_int("slot", value)


def validate_appointment_duration(value: Any) -> int:
    """Check Appointment.duration (int)."""
    return check_int("duration", value)


def validate_appointment_reason(value: Any) -> str:
    """Check Appointment.reason (text)."""
    return check_text("reason", value, max_length=2000, required=False)


def validate_appointment_status(value: Any) -> AppointmentStatus:
    """Check Appointment.status (enum)."""
    return check_choice("status", value, AppointmentStatus)
