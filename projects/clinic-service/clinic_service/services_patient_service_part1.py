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
from .services_doctor_service import *  # noqa: F401,F403


class PatientServicePart1:
    """Create, change and remove patients."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.patients

    def create(self, data: Dict[str, Any]) -> Patient:
        """Validate and store a new patient."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Patient.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Patient:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("patient", item_id)
        return item

    def list(self, **filters: Any) -> List[Patient]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in PATIENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Patient:
        """Change some fields of a patient."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a patient nobody points at any more."""
        self.get(item_id)
        if self.store.appointments.count_for_patient(item_id):
            raise Conflict(f"patient {item_id} is still used by appointments")
        if self.store.invoices.count_for_patient(item_id):
            raise Conflict(f"patient {item_id} is still used by invoices")
        if self.store.lab_results.count_for_patient(item_id):
            raise Conflict(f"patient {item_id} is still used by lab results")
        self.repo.remove(item_id)

    def _check_links(self, item: Patient) -> None:
        """Patient doesn't point at other records."""
        return None

    def toggle_active(self, item_id: int) -> Patient:
        item = self.get(item_id)
        return self.update(item_id, {"active": not item.active})
