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
from .repository_patient_repository import *  # noqa: F401,F403


class AppointmentRepositoryPart1(Repository[Appointment]):
    """All appointments, with the lookups the services need."""

    model = Appointment
    entity_name = "appointment"

    def for_doctor(self, doctor_id: int) -> List[Appointment]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def for_patient(self, patient_id: int) -> List[Appointment]:
        """Records linked to patient `patient_id`."""
        return self.where(lambda item: item.patient_id == patient_id)

    def count_for_patient(self, patient_id: int) -> int:
        return len(self.for_patient(patient_id))

    def day_before(self, day: str) -> List[Appointment]:
        return self.where(lambda item: item.day < day)

    def day_after(self, day: str) -> List[Appointment]:
        return self.where(lambda item: item.day > day)

    def day_on(self, day: str) -> List[Appointment]:
        return self.where(lambda item: item.day == day)

    def between_slot(self, low: float, high: float) -> List[Appointment]:
        """Records whose slot is within [low, high]."""
        return self.where(lambda item: low <= item.slot <= high)

    def total_slot(self) -> float:
        return sum(item.slot for item in self.list())

    def average_slot(self) -> float:
        items = self.list()
        return sum(item.slot for item in items) / len(items) if items else 0.0

    def max_slot(self) -> Optional[Appointment]:
        """The record with the highest slot."""
        items = self.list()
        return max(items, key=lambda item: item.slot) if items else None

    def between_duration(self, low: float, high: float) -> List[Appointment]:
        """Records whose duration is within [low, high]."""
        return self.where(lambda item: low <= item.duration <= high)

    def total_duration(self) -> float:
        return sum(item.duration for item in self.list())

    def average_duration(self) -> float:
        items = self.list()
        return sum(item.duration for item in items) / len(items) if items else 0.0

    def max_duration(self) -> Optional[Appointment]:
        """The record with the highest duration."""
        items = self.list()
        return max(items, key=lambda item: item.duration) if items else None
