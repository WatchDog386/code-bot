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
from .services_prescription_service_part1 import *  # noqa: F401,F403


class PrescriptionService(PrescriptionServicePart1):
    """Create, change and remove prescriptions (continued)."""

    def adjust_days(self, item_id: int, delta: int) -> Prescription:
        """Add `delta` to the days (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"days": item.days + delta})

    def adjust_refills(self, item_id: int, delta: int) -> Prescription:
        """Add `delta` to the refills (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"refills": item.refills + delta})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every prescription."""
        return {
            "count": self.repo.count(),
            "total_dose_mg": round(self.repo.total_dose_mg(), 2),
            "average_dose_mg": round(self.repo.average_dose_mg(), 2),
            "total_times_per_day": round(self.repo.total_times_per_day(), 2),
            "average_times_per_day": round(self.repo.average_times_per_day(), 2),
            "total_days": round(self.repo.total_days(), 2),
            "average_days": round(self.repo.average_days(), 2),
            "total_refills": round(self.repo.total_refills(), 2),
            "average_refills": round(self.repo.average_refills(), 2),
        }
