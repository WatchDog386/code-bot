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
from .services_lab_result_service import *  # noqa: F401,F403


def sample_patient(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new patient (refs point at seeded records)."""
    return {
        "name": f"Patient name {index}",
        "email": f"patient{index}@example.com",
        "phone": f"Patient phone {index}",
        "birth_date": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "insurance": f"Patient insurance {index}",
        "allergies": f"Notes about patient {index}.",
        "active": index % 2 == 1,
    }
