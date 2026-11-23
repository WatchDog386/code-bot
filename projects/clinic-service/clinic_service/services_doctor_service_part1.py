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
from .services_store import *  # noqa: F401,F403


class DoctorServicePart1:
    """Create, change and remove doctors."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.doctors

    def create(self, data: Dict[str, Any]) -> Doctor:
        """Validate and store a new doctor."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Doctor.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Doctor:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("doctor", item_id)
        return item

    def list(self, **filters: Any) -> List[Doctor]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in DOCTOR_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Doctor:
        """Change some fields of a doctor."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a doctor nobody points at any more."""
        self.get(item_id)
        if self.store.appointments.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by appointments")
        self.repo.remove(item_id)

    def _check_links(self, item: Doctor) -> None:
        """Doctor doesn't point at other records."""
        return None

    def set_specialty(self, item_id: int, value: Any) -> Doctor:
        """Move a doctor to another specialty."""
        return self.update(item_id, {"specialty": value})

    def adjust_hourly_rate(self, item_id: int, delta: float) -> Doctor:
        item = self.get(item_id)
        return self.update(item_id, {"hourly_rate": round(item.hourly_rate + delta, 2)})
