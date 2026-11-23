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
from .repository_doctor_repository import *  # noqa: F401,F403


class PatientRepositoryPart1(Repository[Patient]):
    """All patients, with the lookups the services need."""

    model = Patient
    entity_name = "patient"

    def find_by_name(self, value: str) -> List[Patient]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Patient]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Patient]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Patient]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def find_by_phone(self, value: str) -> List[Patient]:
        """Records whose phone is exactly `value`."""
        return self.where(lambda item: item.phone == value)

    def search_phone(self, text: str) -> List[Patient]:
        """Records whose phone contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.phone.lower())

    def birth_date_before(self, day: str) -> List[Patient]:
        return self.where(lambda item: item.birth_date < day)

    def birth_date_after(self, day: str) -> List[Patient]:
        return self.where(lambda item: item.birth_date > day)

    def birth_date_on(self, day: str) -> List[Patient]:
        return self.where(lambda item: item.birth_date == day)

    def find_by_insurance(self, value: str) -> List[Patient]:
        """Records whose insurance is exactly `value`."""
        return self.where(lambda item: item.insurance == value)

    def search_insurance(self, text: str) -> List[Patient]:
        """Records whose insurance contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.insurance.lower())

    def find_by_allergies(self, value: str) -> List[Patient]:
        """Records whose allergies is exactly `value`."""
        return self.where(lambda item: item.allergies == value)

    def search_allergies(self, text: str) -> List[Patient]:
        """Records whose allergies contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.allergies.lower())
