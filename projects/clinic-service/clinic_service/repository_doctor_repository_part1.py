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
from .repository_repository import *  # noqa: F401,F403


class DoctorRepositoryPart1(Repository[Doctor]):
    """All doctors, with the lookups the services need."""

    model = Doctor
    entity_name = "doctor"

    def find_by_name(self, value: str) -> List[Doctor]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Doctor]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Doctor]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Doctor]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def with_specialty(self, value: Any) -> List[Doctor]:
        wanted = DoctorSpecialty(value)
        return self.where(lambda item: item.specialty == wanted)

    def count_by_specialty(self) -> Dict[str, int]:
        """How many records have each specialty."""
        counts = {member.value: 0 for member in DoctorSpecialty}
        for item in self.list():
            counts[DoctorSpecialty(item.specialty).value] += 1
        return counts

    def find_by_room(self, value: str) -> List[Doctor]:
        """Records whose room is exactly `value`."""
        return self.where(lambda item: item.room == value)

    def search_room(self, text: str) -> List[Doctor]:
        """Records whose room contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.room.lower())

    def between_hourly_rate(self, low: float, high: float) -> List[Doctor]:
        """Records whose hourly rate is within [low, high]."""
        return self.where(lambda item: low <= item.hourly_rate <= high)

    def total_hourly_rate(self) -> float:
        return sum(item.hourly_rate for item in self.list())

    def average_hourly_rate(self) -> float:
        items = self.list()
        return sum(item.hourly_rate for item in items) / len(items) if items else 0.0

    def max_hourly_rate(self) -> Optional[Doctor]:
        """The record with the highest hourly rate."""
        items = self.list()
        return max(items, key=lambda item: item.hourly_rate) if items else None
