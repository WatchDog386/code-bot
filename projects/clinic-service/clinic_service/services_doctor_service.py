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
from .services_doctor_service_part1 import *  # noqa: F401,F403


class DoctorService(DoctorServicePart1):
    """Create, change and remove doctors (continued)."""

    def toggle_accepting(self, item_id: int) -> Doctor:
        item = self.get(item_id)
        return self.update(item_id, {"accepting": not item.accepting})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every doctor."""
        return {
            "count": self.repo.count(),
            "by_specialty": self.repo.count_by_specialty(),
            "total_hourly_rate": round(self.repo.total_hourly_rate(), 2),
            "average_hourly_rate": round(self.repo.average_hourly_rate(), 2),
            "accepting": len(self.repo.where_accepting(True)),
        }
