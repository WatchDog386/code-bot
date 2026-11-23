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
from .models_lab_result_fields import *  # noqa: F401,F403


def validate_lab_result_taken(value: Any) -> str:
    """Check LabResult.taken (date)."""
    return check_date("taken", value)


def validate_lab_result_flagged(value: Any) -> bool:
    """Check LabResult.flagged (bool)."""
    return check_flag("flagged", value)
