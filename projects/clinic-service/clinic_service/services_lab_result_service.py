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
from .services_lab_result_service_part1 import *  # noqa: F401,F403


class LabResultService(LabResultServicePart1):
    """Create, change and remove lab results (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every lab result."""
        return {
            "count": self.repo.count(),
            "total_value": round(self.repo.total_value(), 2),
            "average_value": round(self.repo.average_value(), 2),
            "flagged": len(self.repo.where_flagged(True)),
        }


def sample_doctor(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new doctor (refs point at seeded records)."""
    return {
        "name": f"Doctor name {index}",
        "email": f"doctor{index}@example.com",
        "specialty": ['general', 'pediatrics', 'cardiology', 'dermatology', 'orthopedics'][index % 5],
        "room": f"Doctor room {index}",
        "hourly_rate": round(10.0 * index + 0.99, 2),
        "accepting": index % 2 == 1,
    }
