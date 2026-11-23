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
from .services_prescription_service import *  # noqa: F401,F403


class InvoiceServicePart1:
    """Create, change and remove invoices."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.invoices

    def create(self, data: Dict[str, Any]) -> Invoice:
        """Validate and store a new invoice."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Invoice.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Invoice:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("invoice", item_id)
        return item

    def list(self, **filters: Any) -> List[Invoice]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in INVOICE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Invoice:
        """Change some fields of a invoice."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a invoice nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Invoice) -> None:
        if self.store.patients.get(item.patient_id) is None:
            raise NotFound("patient", item.patient_id)

    def adjust_amount(self, item_id: int, delta: float) -> Invoice:
        item = self.get(item_id)
        return self.update(item_id, {"amount": round(item.amount + delta, 2)})

    def adjust_paid(self, item_id: int, delta: float) -> Invoice:
        item = self.get(item_id)
        return self.update(item_id, {"paid": round(item.paid + delta, 2)})

    def set_status(self, item_id: int, value: Any) -> Invoice:
        """Move a invoice to another status."""
        return self.update(item_id, {"status": value})
