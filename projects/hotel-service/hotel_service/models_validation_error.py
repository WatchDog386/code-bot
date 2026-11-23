"""Domain models for the Hotel Reservations service.

Every model is a dataclass with a
`validate()` that checks and normalises its fields, plus `to_dict()` / `from_dict()`
for the JSON API and `apply()` for partial updates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import date
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Tuple, Type

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_INT = 1_000_000_000


class ValidationError(ValueError):
    """A field holds a value the service can't accept."""

    def __init__(self, field_name: str, message: str) -> None:
        super().__init__(f"{field_name}: {message}")
        self.field_name = field_name
        self.message = message


def check_text(name: str, value: Any, max_length: int = 120, required: bool = True) -> str:
    """Trimmed text, not empty unless optional, and not too long."""
    if not isinstance(value, str):
        raise ValidationError(name, "must be text")
    cleaned = value.strip()
    if required and not cleaned:
        raise ValidationError(name, "is required")
    if len(cleaned) > max_length:
        raise ValidationError(name, f"must be at most {max_length} characters")
    return cleaned
