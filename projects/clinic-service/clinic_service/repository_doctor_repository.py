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
from .repository_doctor_repository_part1 import *  # noqa: F401,F403


class DoctorRepository(DoctorRepositoryPart1):
    """All doctors, with the lookups the services need (continued)."""

    def where_accepting(self, flag: bool = True) -> List[Doctor]:
        return self.where(lambda item: item.accepting is flag)

    def search(self, text: str) -> List[Doctor]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.room,
        )))
