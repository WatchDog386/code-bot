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
from .repository_appointment_repository_part1 import *  # noqa: F401,F403


class AppointmentRepository(AppointmentRepositoryPart1):
    """All appointments, with the lookups the services need (continued)."""

    def find_by_reason(self, value: str) -> List[Appointment]:
        """Records whose reason is exactly `value`."""
        return self.where(lambda item: item.reason == value)

    def search_reason(self, text: str) -> List[Appointment]:
        """Records whose reason contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.reason.lower())

    def with_status(self, value: Any) -> List[Appointment]:
        wanted = AppointmentStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in AppointmentStatus}
        for item in self.list():
            counts[AppointmentStatus(item.status).value] += 1
        return counts

    def between_fee(self, low: float, high: float) -> List[Appointment]:
        """Records whose fee is within [low, high]."""
        return self.where(lambda item: low <= item.fee <= high)

    def total_fee(self) -> float:
        return sum(item.fee for item in self.list())

    def average_fee(self) -> float:
        items = self.list()
        return sum(item.fee for item in items) / len(items) if items else 0.0

    def max_fee(self) -> Optional[Appointment]:
        """The record with the highest fee."""
        items = self.list()
        return max(items, key=lambda item: item.fee) if items else None

    def search(self, text: str) -> List[Appointment]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.reason,
        )))
