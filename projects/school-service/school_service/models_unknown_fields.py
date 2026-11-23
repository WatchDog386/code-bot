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
from .models_check_email import *  # noqa: F401,F403


def unknown_fields(data: Dict[str, Any], known: FrozenSet[str]) -> Optional[str]:
    """The first key in `data` that isn't a field, if any."""
    extra = sorted(set(data) - known)
    return extra[0] if extra else None


class CourseTerm(str, Enum):
    """Allowed values of Course.term."""

    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)
