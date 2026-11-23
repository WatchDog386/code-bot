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
from .models_validation_error import *  # noqa: F401,F403


def check_email(name: str, value: Any) -> str:
    """A plausible e-mail address, stored in lower case."""
    text = check_text(name, value, max_length=254)
    if not EMAIL_RE.match(text):
        raise ValidationError(name, "must be an e-mail address")
    return text.lower()


def check_int(name: str, value: Any, minimum: int = 0, maximum: int = MAX_INT) -> int:
    """A whole number inside [minimum, maximum]."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(name, "must be a whole number")
    if value < minimum:
        raise ValidationError(name, f"must be at least {minimum}")
    if value > maximum:
        raise ValidationError(name, f"must be at most {maximum}")
    return value


def check_number(name: str, value: Any, minimum: float = 0.0) -> float:
    """Any number that isn't negative."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(name, "must be a number")
    if value < minimum:
        raise ValidationError(name, f"must be at least {minimum}")
    return float(value)


def check_money(name: str, value: Any) -> float:
    """An amount of money, rounded to cents."""
    return round(check_number(name, value), 2)


def check_flag(name: str, value: Any) -> bool:
    """A real boolean (no "yes"/"no" strings)."""
    if not isinstance(value, bool):
        raise ValidationError(name, "must be true or false")
    return value


def check_date(name: str, value: Any) -> str:
    """An ISO date (YYYY-MM-DD) that exists in the calendar."""
    text = check_text(name, value, max_length=10)
    if not DATE_RE.match(text):
        raise ValidationError(name, "must look like YYYY-MM-DD")
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValidationError(name, "is not a real date") from None
    return text


def check_ref(name: str, value: Any) -> int:
    """The id of another record (existence is checked by the services)."""
    return check_int(name, value, minimum=1)


def check_choice(name: str, value: Any, choices: Type[Enum]) -> Any:
    """One of the values of an Enum."""
    if isinstance(value, choices):
        return value
    try:
        return choices(value)
    except ValueError:
        allowed = ", ".join(member.value for member in choices)
        raise ValidationError(name, f"must be one of: {allowed}") from None
