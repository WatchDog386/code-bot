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
from .services_sample_appointment import *  # noqa: F401,F403


class Services:
    """The whole service: storage plus one service object per model."""

    def __init__(self, store: Optional[Store] = None) -> None:
        self.store = store or Store()
        self.doctors = DoctorService(self.store)
        self.patients = PatientService(self.store)
        self.appointments = AppointmentService(self.store)
        self.prescriptions = PrescriptionService(self.store)
        self.invoices = InvoiceService(self.store)
        self.lab_results = LabResultService(self.store)

    def seed(self, count: int = 3) -> None:
        """Fill every repository with `count` sample records."""
        for index in range(1, count + 1):
            self.doctors.create(sample_doctor(index))
            self.patients.create(sample_patient(index))
            self.appointments.create(sample_appointment(index))
            self.prescriptions.create(sample_prescription(index))
            self.invoices.create(sample_invoice(index))
            self.lab_results.create(sample_lab_result(index))

    def summary(self) -> Dict[str, Any]:
        return {
            "doctors": self.doctors.stats(),
            "patients": self.patients.stats(),
            "appointments": self.appointments.stats(),
            "prescriptions": self.prescriptions.stats(),
            "invoices": self.invoices.stats(),
            "lab_results": self.lab_results.stats(),
        }
