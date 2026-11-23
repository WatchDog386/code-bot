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
from .repository_invoice_repository import *  # noqa: F401,F403


class LabResultRepositoryPart1(Repository[LabResult]):
    """All lab results, with the lookups the services need."""

    model = LabResult
    entity_name = "lab_result"

    def for_patient(self, patient_id: int) -> List[LabResult]:
        """Records linked to patient `patient_id`."""
        return self.where(lambda item: item.patient_id == patient_id)

    def count_for_patient(self, patient_id: int) -> int:
        return len(self.for_patient(patient_id))

    def find_by_test_name(self, value: str) -> List[LabResult]:
        """Records whose test name is exactly `value`."""
        return self.where(lambda item: item.test_name == value)

    def search_test_name(self, text: str) -> List[LabResult]:
        """Records whose test name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.test_name.lower())

    def between_value(self, low: float, high: float) -> List[LabResult]:
        """Records whose value is within [low, high]."""
        return self.where(lambda item: low <= item.value <= high)

    def total_value(self) -> float:
        return sum(item.value for item in self.list())

    def average_value(self) -> float:
        items = self.list()
        return sum(item.value for item in items) / len(items) if items else 0.0

    def max_value(self) -> Optional[LabResult]:
        """The record with the highest value."""
        items = self.list()
        return max(items, key=lambda item: item.value) if items else None

    def find_by_unit(self, value: str) -> List[LabResult]:
        """Records whose unit is exactly `value`."""
        return self.where(lambda item: item.unit == value)

    def search_unit(self, text: str) -> List[LabResult]:
        """Records whose unit contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.unit.lower())

    def taken_before(self, day: str) -> List[LabResult]:
        return self.where(lambda item: item.taken < day)

    def taken_after(self, day: str) -> List[LabResult]:
        return self.where(lambda item: item.taken > day)

    def taken_on(self, day: str) -> List[LabResult]:
        return self.where(lambda item: item.taken == day)

    def where_flagged(self, flag: bool = True) -> List[LabResult]:
        return self.where(lambda item: item.flagged is flag)
