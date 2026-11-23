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
from .repository_prescription_repository_part1 import *  # noqa: F401,F403


class PrescriptionRepository(PrescriptionRepositoryPart1):
    """All prescriptions, with the lookups the services need (continued)."""

    def average_days(self) -> float:
        items = self.list()
        return sum(item.days for item in items) / len(items) if items else 0.0

    def max_days(self) -> Optional[Prescription]:
        """The record with the highest days."""
        items = self.list()
        return max(items, key=lambda item: item.days) if items else None

    def between_refills(self, low: float, high: float) -> List[Prescription]:
        """Records whose refills is within [low, high]."""
        return self.where(lambda item: low <= item.refills <= high)

    def total_refills(self) -> float:
        return sum(item.refills for item in self.list())

    def average_refills(self) -> float:
        items = self.list()
        return sum(item.refills for item in items) / len(items) if items else 0.0

    def max_refills(self) -> Optional[Prescription]:
        """The record with the highest refills."""
        items = self.list()
        return max(items, key=lambda item: item.refills) if items else None

    def find_by_notes(self, value: str) -> List[Prescription]:
        """Records whose notes is exactly `value`."""
        return self.where(lambda item: item.notes == value)

    def search_notes(self, text: str) -> List[Prescription]:
        """Records whose notes contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.notes.lower())

    def search(self, text: str) -> List[Prescription]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.drug,
            item.notes,
        )))
