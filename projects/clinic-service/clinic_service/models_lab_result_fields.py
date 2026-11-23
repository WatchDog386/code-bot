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
from .models_invoice import *  # noqa: F401,F403


# -------------------------------------------------------------------------- LabResult
LAB_RESULT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "patient_id",
    "test_name",
    "value",
    "unit",
    "taken",
    "flagged",
})


LAB_RESULT_SORTABLE: Tuple[str, ...] = ('id', 'patient_id', 'test_name', 'value', 'unit', 'taken',)


LAB_RESULT_REQUIRED: Tuple[str, ...] = ('patient_id', 'test_name', 'unit', 'taken',)


def validate_lab_result_patient_id(value: Any) -> int:
    """Check LabResult.patient_id (ref)."""
    return check_ref("patient_id", value)


def validate_lab_result_test_name(value: Any) -> str:
    """Check LabResult.test_name (str)."""
    return check_text("test_name", value)


def validate_lab_result_value(value: Any) -> float:
    """Check LabResult.value (float)."""
    return check_number("value", value)


def validate_lab_result_unit(value: Any) -> str:
    """Check LabResult.unit (str)."""
    return check_text("unit", value)
