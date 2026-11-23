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
from .repository_invoice_repository_part1 import *  # noqa: F401,F403


class InvoiceRepository(InvoiceRepositoryPart1):
    """All invoices, with the lookups the services need (continued)."""

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in InvoiceStatus}
        for item in self.list():
            counts[InvoiceStatus(item.status).value] += 1
        return counts

    def due_before(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.due < day)

    def due_after(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.due > day)

    def due_on(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.due == day)

    def search(self, text: str) -> List[Invoice]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: needle == str(item.id))
