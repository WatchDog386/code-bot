"""Business rules for the Clinic Scheduling service: validation, links between records
(a record can't point at something that doesn't exist, and can't be deleted while
others still point at it), small domain operations and statistics.
"""

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


class NotFound(LookupError):
    """No record with that id."""

    def __init__(self, entity: str, item_id: int) -> None:
        super().__init__(f"{entity} {item_id} not found")
        self.entity = entity
        self.item_id = item_id


class Conflict(ValueError):
    """The change would break a link between records."""


def plain(value: Any) -> str:
    """A value as the text a query string would carry."""
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
