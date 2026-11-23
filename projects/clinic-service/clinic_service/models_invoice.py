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
from .models_invoice_fields import *  # noqa: F401,F403


@dataclass
class Invoice:
    """A invoice record."""

    id: int = 0
    patient_id: int = 0
    issued: str = ""
    amount: float = 0.0
    paid: float = 0.0
    status: InvoiceStatus = InvoiceStatus.DRAFT
    due: str = ""

    def validate(self) -> "Invoice":
        """Check every field and normalise the values in place."""
        self.patient_id = validate_invoice_patient_id(self.patient_id)
        self.issued = validate_invoice_issued(self.issued)
        self.amount = validate_invoice_amount(self.amount)
        self.paid = validate_invoice_paid(self.paid)
        self.status = validate_invoice_status(self.status)
        self.due = validate_invoice_due(self.due)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "issued": self.issued,
            "amount": self.amount,
            "paid": self.paid,
            "status": self.status.value,
            "due": self.due,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Invoice":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, INVOICE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "patient_id" in data:
            item.patient_id = data["patient_id"]
        if "issued" in data:
            item.issued = data["issued"]
        if "amount" in data:
            item.amount = data["amount"]
        if "paid" in data:
            item.paid = data["paid"]
        if "status" in data:
            item.status = data["status"]
        if "due" in data:
            item.due = data["due"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Invoice":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, INVOICE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Invoice #{self.id}"
