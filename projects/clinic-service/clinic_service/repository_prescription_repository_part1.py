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
from .repository_appointment_repository import *  # noqa: F401,F403


class PrescriptionRepositoryPart1(Repository[Prescription]):
    """All prescriptions, with the lookups the services need."""

    model = Prescription
    entity_name = "prescription"

    def for_appointment(self, appointment_id: int) -> List[Prescription]:
        """Records linked to appointment `appointment_id`."""
        return self.where(lambda item: item.appointment_id == appointment_id)

    def count_for_appointment(self, appointment_id: int) -> int:
        return len(self.for_appointment(appointment_id))

    def find_by_drug(self, value: str) -> List[Prescription]:
        """Records whose drug is exactly `value`."""
        return self.where(lambda item: item.drug == value)

    def search_drug(self, text: str) -> List[Prescription]:
        """Records whose drug contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.drug.lower())

    def between_dose_mg(self, low: float, high: float) -> List[Prescription]:
        """Records whose dose mg is within [low, high]."""
        return self.where(lambda item: low <= item.dose_mg <= high)

    def total_dose_mg(self) -> float:
        return sum(item.dose_mg for item in self.list())

    def average_dose_mg(self) -> float:
        items = self.list()
        return sum(item.dose_mg for item in items) / len(items) if items else 0.0

    def max_dose_mg(self) -> Optional[Prescription]:
        """The record with the highest dose mg."""
        items = self.list()
        return max(items, key=lambda item: item.dose_mg) if items else None

    def between_times_per_day(self, low: float, high: float) -> List[Prescription]:
        """Records whose times per day is within [low, high]."""
        return self.where(lambda item: low <= item.times_per_day <= high)

    def total_times_per_day(self) -> float:
        return sum(item.times_per_day for item in self.list())

    def average_times_per_day(self) -> float:
        items = self.list()
        return sum(item.times_per_day for item in items) / len(items) if items else 0.0

    def max_times_per_day(self) -> Optional[Prescription]:
        """The record with the highest times per day."""
        items = self.list()
        return max(items, key=lambda item: item.times_per_day) if items else None

    def between_days(self, low: float, high: float) -> List[Prescription]:
        """Records whose days is within [low, high]."""
        return self.where(lambda item: low <= item.days <= high)

    def total_days(self) -> float:
        return sum(item.days for item in self.list())
