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
from .services_sample_patient import *  # noqa: F401,F403


def sample_appointment(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new appointment (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "patient_id": (index - 1) % 3 + 1,
        "day": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "slot": index + 1,
        "duration": index + 1,
        "reason": f"Notes about appointment {index}.",
        "status": ['booked', 'checked_in', 'completed', 'cancelled', 'no_show'][index % 5],
        "fee": round(10.0 * index + 0.99, 2),
    }


def sample_prescription(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new prescription (refs point at seeded records)."""
    return {
        "appointment_id": (index - 1) % 3 + 1,
        "drug": f"Prescription drug {index}",
        "dose_mg": index + 1,
        "times_per_day": index + 1,
        "days": index + 1,
        "refills": index + 1,
        "notes": f"Notes about prescription {index}.",
    }


def sample_invoice(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new invoice (refs point at seeded records)."""
    return {
        "patient_id": (index - 1) % 3 + 1,
        "issued": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "amount": round(10.0 * index + 0.99, 2),
        "paid": round(10.0 * index + 0.99, 2),
        "status": ['draft', 'sent', 'paid', 'void'][index % 4],
        "due": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_lab_result(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new lab result (refs point at seeded records)."""
    return {
        "patient_id": (index - 1) % 3 + 1,
        "test_name": f"Lab result test name {index}",
        "value": round(1.5 * index + 0.25, 2),
        "unit": f"Lab result unit {index}",
        "taken": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "flagged": index % 2 == 1,
    }
