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
from .services_not_found import *  # noqa: F401,F403


class Store:
    """Every repository of the service."""

    def __init__(self) -> None:
        self.doctors = DoctorRepository()
        self.patients = PatientRepository()
        self.appointments = AppointmentRepository()
        self.prescriptions = PrescriptionRepository()
        self.invoices = InvoiceRepository()
        self.lab_results = LabResultRepository()

    def counts(self) -> Dict[str, int]:
        return {
            "doctors": self.doctors.count(),
            "patients": self.patients.count(),
            "appointments": self.appointments.count(),
            "prescriptions": self.prescriptions.count(),
            "invoices": self.invoices.count(),
            "lab_results": self.lab_results.count(),
        }
