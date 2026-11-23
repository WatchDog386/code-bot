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
from .services_patient_service_part1 import *  # noqa: F401,F403


class PatientService(PatientServicePart1):
    """Create, change and remove patients (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every patient."""
        return {
            "count": self.repo.count(),
            "active": len(self.repo.where_active(True)),
        }
