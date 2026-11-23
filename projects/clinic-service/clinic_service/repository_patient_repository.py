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
from .repository_patient_repository_part1 import *  # noqa: F401,F403


class PatientRepository(PatientRepositoryPart1):
    """All patients, with the lookups the services need (continued)."""

    def where_active(self, flag: bool = True) -> List[Patient]:
        return self.where(lambda item: item.active is flag)

    def search(self, text: str) -> List[Patient]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.phone,
            item.insurance,
            item.allergies,
        )))
