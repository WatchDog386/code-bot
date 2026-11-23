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
from .models_booking import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Charge
CHARGE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "booking_id",
    "description",
    "amount",
    "posted",
    "category",
})


CHARGE_SORTABLE: Tuple[str, ...] = ('id', 'booking_id', 'description', 'amount', 'posted', 'category',)


CHARGE_REQUIRED: Tuple[str, ...] = ('booking_id', 'description', 'posted',)


def validate_charge_booking_id(value: Any) -> int:
    """Check Charge.booking_id (ref)."""
    return check_ref("booking_id", value)


def validate_charge_description(value: Any) -> str:
    """Check Charge.description (str)."""
    return check_text("description", value)


def validate_charge_amount(value: Any) -> float:
    """Check Charge.amount (money)."""
    return check_money("amount", value)


def validate_charge_posted(value: Any) -> str:
    """Check Charge.posted (date)."""
    return check_date("posted", value)


def validate_charge_category(value: Any) -> ChargeCategory:
    """Check Charge.category (enum)."""
    return check_choice("category", value, ChargeCategory)
