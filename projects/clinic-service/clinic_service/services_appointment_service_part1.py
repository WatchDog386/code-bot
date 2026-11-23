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
from .services_patient_service import *  # noqa: F401,F403


class AppointmentServicePart1:
    """Create, change and remove appointments."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.appointments

    def create(self, data: Dict[str, Any]) -> Appointment:
        """Validate and store a new appointment."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Appointment.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Appointment:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("appointment", item_id)
        return item

    def list(self, **filters: Any) -> List[Appointment]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in APPOINTMENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Appointment:
        """Change some fields of a appointment."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a appointment nobody points at any more."""
        self.get(item_id)
        if self.store.prescriptions.count_for_appointment(item_id):
            raise Conflict(f"appointment {item_id} is still used by prescriptions")
        self.repo.remove(item_id)

    def _check_links(self, item: Appointment) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)
        if self.store.patients.get(item.patient_id) is None:
            raise NotFound("patient", item.patient_id)

    def adjust_slot(self, item_id: int, delta: int) -> Appointment:
        """Add `delta` to the slot (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"slot": item.slot + delta})
