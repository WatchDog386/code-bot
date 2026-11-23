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
from .services_invoice_service import *  # noqa: F401,F403


class LabResultServicePart1:
    """Create, change and remove lab results."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.lab_results

    def create(self, data: Dict[str, Any]) -> LabResult:
        """Validate and store a new lab result."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = LabResult.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> LabResult:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("lab result", item_id)
        return item

    def list(self, **filters: Any) -> List[LabResult]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in LAB_RESULT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> LabResult:
        """Change some fields of a lab result."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a lab result nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: LabResult) -> None:
        if self.store.patients.get(item.patient_id) is None:
            raise NotFound("patient", item.patient_id)

    def adjust_value(self, item_id: int, delta: float) -> LabResult:
        item = self.get(item_id)
        return self.update(item_id, {"value": round(item.value + delta, 2)})

    def toggle_flagged(self, item_id: int) -> LabResult:
        item = self.get(item_id)
        return self.update(item_id, {"flagged": not item.flagged})
