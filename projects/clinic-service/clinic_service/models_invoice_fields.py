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
from .models_prescription import *  # noqa: F401,F403


# -------------------------------------------------------------------------- Invoice
INVOICE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "patient_id",
    "issued",
    "amount",
    "paid",
    "status",
    "due",
})


INVOICE_SORTABLE: Tuple[str, ...] = ('id', 'patient_id', 'issued', 'amount', 'paid', 'status', 'due',)


INVOICE_REQUIRED: Tuple[str, ...] = ('patient_id', 'issued', 'due',)


def validate_invoice_patient_id(value: Any) -> int:
    """Check Invoice.patient_id (ref)."""
    return check_ref("patient_id", value)


def validate_invoice_issued(value: Any) -> str:
    """Check Invoice.issued (date)."""
    return check_date("issued", value)


def validate_invoice_amount(value: Any) -> float:
    """Check Invoice.amount (money)."""
    return check_money("amount", value)


def validate_invoice_paid(value: Any) -> float:
    """Check Invoice.paid (money)."""
    return check_money("paid", value)


def validate_invoice_status(value: Any) -> InvoiceStatus:
    """Check Invoice.status (enum)."""
    return check_choice("status", value, InvoiceStatus)


def validate_invoice_due(value: Any) -> str:
    """Check Invoice.due (date)."""
    return check_date("due", value)
