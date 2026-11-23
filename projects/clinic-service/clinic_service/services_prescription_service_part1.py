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
from .services_appointment_service import *  # noqa: F401,F403


class PrescriptionServicePart1:
    """Create, change and remove prescriptions."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.prescriptions

    def create(self, data: Dict[str, Any]) -> Prescription:
        """Validate and store a new prescription."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Prescription.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Prescription:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("prescription", item_id)
        return item

    def list(self, **filters: Any) -> List[Prescription]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in PRESCRIPTION_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Prescription:
        """Change some fields of a prescription."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a prescription nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Prescription) -> None:
        if self.store.appointments.get(item.appointment_id) is None:
            raise NotFound("appointment", item.appointment_id)

    def adjust_dose_mg(self, item_id: int, delta: int) -> Prescription:
        """Add `delta` to the dose mg (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"dose_mg": item.dose_mg + delta})

    def adjust_times_per_day(self, item_id: int, delta: int) -> Prescription:
        """Add `delta` to the times per day (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"times_per_day": item.times_per_day + delta})
