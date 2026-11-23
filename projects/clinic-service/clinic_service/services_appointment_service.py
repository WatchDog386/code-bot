"""Services (continued)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from .models import (
    APPOINTMENT_FIELDS,
    Appointment,
    DOCTOR_FIELDS,
    Doctor,
    INVOICE_FIELDS,
    Invoice,
    LAB_RESULT_FIELDS,
    LabResult,
    PATIENT_FIELDS,
    PRESCRIPTION_FIELDS,
    Patient,
    Prescription,
    ValidationError,
)
from .repository import (
    DoctorRepository,
    PatientRepository,
    AppointmentRepository,
    PrescriptionRepository,
    InvoiceRepository,
    LabResultRepository,
)
from .services_appointment_service_part1 import *  # noqa: F401,F403


class AppointmentService(AppointmentServicePart1):
    """Create, change and remove appointments (continued)."""

    def adjust_duration(self, item_id: int, delta: int) -> Appointment:
        """Add `delta` to the duration (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"duration": item.duration + delta})

    def set_status(self, item_id: int, value: Any) -> Appointment:
        """Move a appointment to another status."""
        return self.update(item_id, {"status": value})

    def adjust_fee(self, item_id: int, delta: float) -> Appointment:
        item = self.get(item_id)
        return self.update(item_id, {"fee": round(item.fee + delta, 2)})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every appointment."""
        return {
            "count": self.repo.count(),
            "total_slot": round(self.repo.total_slot(), 2),
            "average_slot": round(self.repo.average_slot(), 2),
            "total_duration": round(self.repo.total_duration(), 2),
            "average_duration": round(self.repo.average_duration(), 2),
            "by_status": self.repo.count_by_status(),
            "total_fee": round(self.repo.total_fee(), 2),
            "average_fee": round(self.repo.average_fee(), 2),
        }
