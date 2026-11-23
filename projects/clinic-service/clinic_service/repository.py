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
from .repository_lab_result_repository_part1 import *  # noqa: F401,F403


class LabResultRepository(LabResultRepositoryPart1):
    """All lab results, with the lookups the services need (continued)."""

    def search(self, text: str) -> List[LabResult]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.test_name,
            item.unit,
        )))
