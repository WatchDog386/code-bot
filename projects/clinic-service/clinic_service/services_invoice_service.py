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
from .services_invoice_service_part1 import *  # noqa: F401,F403


class InvoiceService(InvoiceServicePart1):
    """Create, change and remove invoices (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every invoice."""
        return {
            "count": self.repo.count(),
            "total_amount": round(self.repo.total_amount(), 2),
            "average_amount": round(self.repo.average_amount(), 2),
            "total_paid": round(self.repo.total_paid(), 2),
            "average_paid": round(self.repo.average_paid(), 2),
            "by_status": self.repo.count_by_status(),
        }
