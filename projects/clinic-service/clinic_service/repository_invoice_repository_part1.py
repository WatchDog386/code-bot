"""Repository (continued)."""

from __future__ import annotations

import csv
import io
import json
import threading
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import (
    Appointment,
    AppointmentStatus,
    Doctor,
    DoctorSpecialty,
    Invoice,
    InvoiceStatus,
    LabResult,
    Patient,
    Prescription,
)

T = TypeVar("T")
from .repository_prescription_repository import *  # noqa: F401,F403


class InvoiceRepositoryPart1(Repository[Invoice]):
    """All invoices, with the lookups the services need."""

    model = Invoice
    entity_name = "invoice"

    def for_patient(self, patient_id: int) -> List[Invoice]:
        """Records linked to patient `patient_id`."""
        return self.where(lambda item: item.patient_id == patient_id)

    def count_for_patient(self, patient_id: int) -> int:
        return len(self.for_patient(patient_id))

    def issued_before(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.issued < day)

    def issued_after(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.issued > day)

    def issued_on(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.issued == day)

    def between_amount(self, low: float, high: float) -> List[Invoice]:
        """Records whose amount is within [low, high]."""
        return self.where(lambda item: low <= item.amount <= high)

    def total_amount(self) -> float:
        return sum(item.amount for item in self.list())

    def average_amount(self) -> float:
        items = self.list()
        return sum(item.amount for item in items) / len(items) if items else 0.0

    def max_amount(self) -> Optional[Invoice]:
        """The record with the highest amount."""
        items = self.list()
        return max(items, key=lambda item: item.amount) if items else None

    def between_paid(self, low: float, high: float) -> List[Invoice]:
        """Records whose paid is within [low, high]."""
        return self.where(lambda item: low <= item.paid <= high)

    def total_paid(self) -> float:
        return sum(item.paid for item in self.list())

    def average_paid(self) -> float:
        items = self.list()
        return sum(item.paid for item in items) / len(items) if items else 0.0

    def max_paid(self) -> Optional[Invoice]:
        """The record with the highest paid."""
        items = self.list()
        return max(items, key=lambda item: item.paid) if items else None

    def with_status(self, value: Any) -> List[Invoice]:
        wanted = InvoiceStatus(value)
        return self.where(lambda item: item.status == wanted)
