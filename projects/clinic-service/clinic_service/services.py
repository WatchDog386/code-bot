"""Business rules for the Clinic Scheduling service: validation, links between records
(a record can't point at something that doesn't exist, and can't be deleted while
others still point at it), small domain operations and statistics.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from .models import (
    ADDRESS_FIELDS,
    APPOINTMENT_FIELDS,
    AUDIT_ENTRY_FIELDS,
    Address,
    Appointment,
    AuditEntry,
    CONTACT_PERSON_FIELDS,
    ContactPerson,
    DISCOUNT_FIELDS,
    DOCTOR_FIELDS,
    DOCUMENT_FIELDS,
    Discount,
    Doctor,
    Document,
    INVOICE_FIELDS,
    Invoice,
    LAB_RESULT_FIELDS,
    LabResult,
    NOTE_FIELDS,
    NOTIFICATION_FIELDS,
    Note,
    Notification,
    PATIENT_FIELDS,
    PRESCRIPTION_FIELDS,
    Patient,
    Prescription,
    REMINDER_FIELDS,
    REVIEW_FIELDS,
    Reminder,
    Review,
    SETTING_FIELDS,
    Setting,
    TAG_FIELDS,
    Tag,
    ValidationError,
)
from .repository import (
    DoctorRepository,
    PatientRepository,
    AppointmentRepository,
    PrescriptionRepository,
    InvoiceRepository,
    LabResultRepository,
    DocumentRepository,
    NotificationRepository,
    AddressRepository,
    ReminderRepository,
    SettingRepository,
    AuditEntryRepository,
    NoteRepository,
    ReviewRepository,
    ContactPersonRepository,
    DiscountRepository,
    TagRepository,
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


class Store:
    """Every repository of the service."""

    def __init__(self) -> None:
        self.doctors = DoctorRepository()
        self.patients = PatientRepository()
        self.appointments = AppointmentRepository()
        self.prescriptions = PrescriptionRepository()
        self.invoices = InvoiceRepository()
        self.lab_results = LabResultRepository()
        self.documents = DocumentRepository()
        self.notifications = NotificationRepository()
        self.addresses = AddressRepository()
        self.reminders = ReminderRepository()
        self.settings = SettingRepository()
        self.audit_entries = AuditEntryRepository()
        self.notes = NoteRepository()
        self.reviews = ReviewRepository()
        self.contact_persons = ContactPersonRepository()
        self.discounts = DiscountRepository()
        self.tags = TagRepository()

    def counts(self) -> Dict[str, int]:
        return {
            "doctors": self.doctors.count(),
            "patients": self.patients.count(),
            "appointments": self.appointments.count(),
            "prescriptions": self.prescriptions.count(),
            "invoices": self.invoices.count(),
            "lab_results": self.lab_results.count(),
            "documents": self.documents.count(),
            "notifications": self.notifications.count(),
            "addresses": self.addresses.count(),
            "reminders": self.reminders.count(),
            "settings": self.settings.count(),
            "audit_entries": self.audit_entries.count(),
            "notes": self.notes.count(),
            "reviews": self.reviews.count(),
            "contact_persons": self.contact_persons.count(),
            "discounts": self.discounts.count(),
            "tags": self.tags.count(),
        }


class DoctorService:
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
        if self.store.documents.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by documents")
        if self.store.addresses.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by addresses")
        if self.store.reminders.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by reminders")
        if self.store.notes.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by notes")
        if self.store.reviews.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by reviews")
        if self.store.contact_persons.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by contact persons")
        if self.store.tags.count_for_doctor(item_id):
            raise Conflict(f"doctor {item_id} is still used by tags")
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

    def toggle_accepting(self, item_id: int) -> Doctor:
        item = self.get(item_id)
        return self.update(item_id, {"accepting": not item.accepting})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every doctor."""
        return {
            "count": self.repo.count(),
            "by_specialty": self.repo.count_by_specialty(),
            "total_hourly_rate": round(self.repo.total_hourly_rate(), 2),
            "average_hourly_rate": round(self.repo.average_hourly_rate(), 2),
            "accepting": len(self.repo.where_accepting(True)),
        }


class PatientService:
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

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every patient."""
        return {
            "count": self.repo.count(),
            "active": len(self.repo.where_active(True)),
        }


class AppointmentService:
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

    def adjust_duration(self, item_id: int, delta: int) -> Appointment:
        """Add `delta` to the duration (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"duration": item.duration + delta})

    def set_status(self, item_id: int, value: Any) -> Appointment:
        """Move a appointment to another status."""
        return self.update(item_id, {"status": value})

    def adjust_fee(self, item_id: int, delta: float) -> Appointment:
        item = self.get(item_id)
        return self.update(item_id, {"fee": round(item.fee + delta, 2)})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every appointment."""
        return {
            "count": self.repo.count(),
            "total_slot": round(self.repo.total_slot(), 2),
            "average_slot": round(self.repo.average_slot(), 2),
            "total_duration": round(self.repo.total_duration(), 2),
            "average_duration": round(self.repo.average_duration(), 2),
            "by_status": self.repo.count_by_status(),
            "total_fee": round(self.repo.total_fee(), 2),
            "average_fee": round(self.repo.average_fee(), 2),
        }


class PrescriptionService:
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

    def adjust_days(self, item_id: int, delta: int) -> Prescription:
        """Add `delta` to the days (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"days": item.days + delta})

    def adjust_refills(self, item_id: int, delta: int) -> Prescription:
        """Add `delta` to the refills (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"refills": item.refills + delta})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every prescription."""
        return {
            "count": self.repo.count(),
            "total_dose_mg": round(self.repo.total_dose_mg(), 2),
            "average_dose_mg": round(self.repo.average_dose_mg(), 2),
            "total_times_per_day": round(self.repo.total_times_per_day(), 2),
            "average_times_per_day": round(self.repo.average_times_per_day(), 2),
            "total_days": round(self.repo.total_days(), 2),
            "average_days": round(self.repo.average_days(), 2),
            "total_refills": round(self.repo.total_refills(), 2),
            "average_refills": round(self.repo.average_refills(), 2),
        }


class InvoiceService:
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


class LabResultService:
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

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every lab result."""
        return {
            "count": self.repo.count(),
            "total_value": round(self.repo.total_value(), 2),
            "average_value": round(self.repo.average_value(), 2),
            "flagged": len(self.repo.where_flagged(True)),
        }


class DocumentService:
    """Create, change and remove documents."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.documents

    def create(self, data: Dict[str, Any]) -> Document:
        """Validate and store a new document."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Document.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Document:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("document", item_id)
        return item

    def list(self, **filters: Any) -> List[Document]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in DOCUMENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Document:
        """Change some fields of a document."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a document nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Document) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def adjust_pages(self, item_id: int, delta: int) -> Document:
        """Add `delta` to the pages (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"pages": item.pages + delta})

    def toggle_signed(self, item_id: int) -> Document:
        item = self.get(item_id)
        return self.update(item_id, {"signed": not item.signed})

    def adjust_version(self, item_id: int, delta: int) -> Document:
        """Add `delta` to the version (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"version": item.version + delta})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every document."""
        return {
            "count": self.repo.count(),
            "total_pages": round(self.repo.total_pages(), 2),
            "average_pages": round(self.repo.average_pages(), 2),
            "signed": len(self.repo.where_signed(True)),
            "total_version": round(self.repo.total_version(), 2),
            "average_version": round(self.repo.average_version(), 2),
        }


class NotificationService:
    """Create, change and remove notifications."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.notifications

    def create(self, data: Dict[str, Any]) -> Notification:
        """Validate and store a new notification."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Notification.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Notification:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("notification", item_id)
        return item

    def list(self, **filters: Any) -> List[Notification]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in NOTIFICATION_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Notification:
        """Change some fields of a notification."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a notification nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Notification) -> None:
        """Notification doesn't point at other records."""
        return None

    def set_channel(self, item_id: int, value: Any) -> Notification:
        """Move a notification to another channel."""
        return self.update(item_id, {"channel": value})

    def toggle_read(self, item_id: int) -> Notification:
        item = self.get(item_id)
        return self.update(item_id, {"read": not item.read})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every notification."""
        return {
            "count": self.repo.count(),
            "by_channel": self.repo.count_by_channel(),
            "read": len(self.repo.where_read(True)),
        }


class AddressService:
    """Create, change and remove addresses."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.addresses

    def create(self, data: Dict[str, Any]) -> Address:
        """Validate and store a new address."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Address.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Address:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("address", item_id)
        return item

    def list(self, **filters: Any) -> List[Address]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ADDRESS_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Address:
        """Change some fields of a address."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a address nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Address) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def toggle_billing(self, item_id: int) -> Address:
        item = self.get(item_id)
        return self.update(item_id, {"billing": not item.billing})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every address."""
        return {
            "count": self.repo.count(),
            "billing": len(self.repo.where_billing(True)),
        }


class ReminderService:
    """Create, change and remove reminders."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.reminders

    def create(self, data: Dict[str, Any]) -> Reminder:
        """Validate and store a new reminder."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Reminder.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Reminder:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("reminder", item_id)
        return item

    def list(self, **filters: Any) -> List[Reminder]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in REMINDER_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Reminder:
        """Change some fields of a reminder."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a reminder nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Reminder) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def toggle_done(self, item_id: int) -> Reminder:
        item = self.get(item_id)
        return self.update(item_id, {"done": not item.done})

    def set_priority(self, item_id: int, value: Any) -> Reminder:
        """Move a reminder to another priority."""
        return self.update(item_id, {"priority": value})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every reminder."""
        return {
            "count": self.repo.count(),
            "done": len(self.repo.where_done(True)),
            "by_priority": self.repo.count_by_priority(),
        }


class SettingService:
    """Create, change and remove settings."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.settings

    def create(self, data: Dict[str, Any]) -> Setting:
        """Validate and store a new setting."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Setting.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Setting:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("setting", item_id)
        return item

    def list(self, **filters: Any) -> List[Setting]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in SETTING_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Setting:
        """Change some fields of a setting."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a setting nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Setting) -> None:
        """Setting doesn't point at other records."""
        return None

    def toggle_editable(self, item_id: int) -> Setting:
        item = self.get(item_id)
        return self.update(item_id, {"editable": not item.editable})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every setting."""
        return {
            "count": self.repo.count(),
            "editable": len(self.repo.where_editable(True)),
        }


class AuditEntryService:
    """Create, change and remove audit entries."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.audit_entries

    def create(self, data: Dict[str, Any]) -> AuditEntry:
        """Validate and store a new audit entry."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = AuditEntry.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> AuditEntry:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("audit entry", item_id)
        return item

    def list(self, **filters: Any) -> List[AuditEntry]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in AUDIT_ENTRY_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> AuditEntry:
        """Change some fields of a audit entry."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a audit entry nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: AuditEntry) -> None:
        """AuditEntry doesn't point at other records."""
        return None

    def set_action(self, item_id: int, value: Any) -> AuditEntry:
        """Move a audit entry to another action."""
        return self.update(item_id, {"action": value})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every audit entry."""
        return {
            "count": self.repo.count(),
            "by_action": self.repo.count_by_action(),
        }


class NoteService:
    """Create, change and remove notes."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.notes

    def create(self, data: Dict[str, Any]) -> Note:
        """Validate and store a new note."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Note.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Note:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("note", item_id)
        return item

    def list(self, **filters: Any) -> List[Note]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in NOTE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Note:
        """Change some fields of a note."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a note nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Note) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def toggle_pinned(self, item_id: int) -> Note:
        item = self.get(item_id)
        return self.update(item_id, {"pinned": not item.pinned})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every note."""
        return {
            "count": self.repo.count(),
            "pinned": len(self.repo.where_pinned(True)),
        }


class ReviewService:
    """Create, change and remove reviews."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.reviews

    def create(self, data: Dict[str, Any]) -> Review:
        """Validate and store a new review."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Review.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Review:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("review", item_id)
        return item

    def list(self, **filters: Any) -> List[Review]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in REVIEW_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Review:
        """Change some fields of a review."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a review nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Review) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def adjust_stars(self, item_id: int, delta: int) -> Review:
        """Add `delta` to the stars (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"stars": item.stars + delta})

    def toggle_verified(self, item_id: int) -> Review:
        item = self.get(item_id)
        return self.update(item_id, {"verified": not item.verified})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every review."""
        return {
            "count": self.repo.count(),
            "total_stars": round(self.repo.total_stars(), 2),
            "average_stars": round(self.repo.average_stars(), 2),
            "verified": len(self.repo.where_verified(True)),
        }


class ContactPersonService:
    """Create, change and remove contact persons."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.contact_persons

    def create(self, data: Dict[str, Any]) -> ContactPerson:
        """Validate and store a new contact person."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = ContactPerson.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> ContactPerson:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("contact person", item_id)
        return item

    def list(self, **filters: Any) -> List[ContactPerson]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in CONTACT_PERSON_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> ContactPerson:
        """Change some fields of a contact person."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a contact person nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: ContactPerson) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def toggle_primary(self, item_id: int) -> ContactPerson:
        item = self.get(item_id)
        return self.update(item_id, {"primary": not item.primary})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every contact person."""
        return {
            "count": self.repo.count(),
            "primary": len(self.repo.where_primary(True)),
        }


class DiscountService:
    """Create, change and remove discounts."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.discounts

    def create(self, data: Dict[str, Any]) -> Discount:
        """Validate and store a new discount."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Discount.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Discount:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("discount", item_id)
        return item

    def list(self, **filters: Any) -> List[Discount]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in DISCOUNT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Discount:
        """Change some fields of a discount."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a discount nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Discount) -> None:
        """Discount doesn't point at other records."""
        return None

    def adjust_percent(self, item_id: int, delta: float) -> Discount:
        item = self.get(item_id)
        return self.update(item_id, {"percent": round(item.percent + delta, 2)})

    def toggle_active(self, item_id: int) -> Discount:
        item = self.get(item_id)
        return self.update(item_id, {"active": not item.active})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every discount."""
        return {
            "count": self.repo.count(),
            "total_percent": round(self.repo.total_percent(), 2),
            "average_percent": round(self.repo.average_percent(), 2),
            "active": len(self.repo.where_active(True)),
        }


class TagService:
    """Create, change and remove tags."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.tags

    def create(self, data: Dict[str, Any]) -> Tag:
        """Validate and store a new tag."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Tag.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Tag:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("tag", item_id)
        return item

    def list(self, **filters: Any) -> List[Tag]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in TAG_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Tag:
        """Change some fields of a tag."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a tag nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Tag) -> None:
        if self.store.doctors.get(item.doctor_id) is None:
            raise NotFound("doctor", item.doctor_id)

    def adjust_usage(self, item_id: int, delta: int) -> Tag:
        """Add `delta` to the usage (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"usage": item.usage + delta})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every tag."""
        return {
            "count": self.repo.count(),
            "total_usage": round(self.repo.total_usage(), 2),
            "average_usage": round(self.repo.average_usage(), 2),
        }


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
        self.documents = DocumentService(self.store)
        self.notifications = NotificationService(self.store)
        self.addresses = AddressService(self.store)
        self.reminders = ReminderService(self.store)
        self.settings = SettingService(self.store)
        self.audit_entries = AuditEntryService(self.store)
        self.notes = NoteService(self.store)
        self.reviews = ReviewService(self.store)
        self.contact_persons = ContactPersonService(self.store)
        self.discounts = DiscountService(self.store)
        self.tags = TagService(self.store)

    def seed(self, count: int = 3) -> None:
        """Fill every repository with `count` sample records."""
        for index in range(1, count + 1):
            self.doctors.create(sample_doctor(index))
            self.patients.create(sample_patient(index))
            self.appointments.create(sample_appointment(index))
            self.prescriptions.create(sample_prescription(index))
            self.invoices.create(sample_invoice(index))
            self.lab_results.create(sample_lab_result(index))
            self.documents.create(sample_document(index))
            self.notifications.create(sample_notification(index))
            self.addresses.create(sample_address(index))
            self.reminders.create(sample_reminder(index))
            self.settings.create(sample_setting(index))
            self.audit_entries.create(sample_audit_entry(index))
            self.notes.create(sample_note(index))
            self.reviews.create(sample_review(index))
            self.contact_persons.create(sample_contact_person(index))
            self.discounts.create(sample_discount(index))
            self.tags.create(sample_tag(index))

    def summary(self) -> Dict[str, Any]:
        return {
            "doctors": self.doctors.stats(),
            "patients": self.patients.stats(),
            "appointments": self.appointments.stats(),
            "prescriptions": self.prescriptions.stats(),
            "invoices": self.invoices.stats(),
            "lab_results": self.lab_results.stats(),
            "documents": self.documents.stats(),
            "notifications": self.notifications.stats(),
            "addresses": self.addresses.stats(),
            "reminders": self.reminders.stats(),
            "settings": self.settings.stats(),
            "audit_entries": self.audit_entries.stats(),
            "notes": self.notes.stats(),
            "reviews": self.reviews.stats(),
            "contact_persons": self.contact_persons.stats(),
            "discounts": self.discounts.stats(),
            "tags": self.tags.stats(),
        }


def sample_doctor(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new doctor (refs point at seeded records)."""
    return {
        "name": f"Doctor name {index}",
        "email": f"doctor{index}@example.com",
        "specialty": ['general', 'pediatrics', 'cardiology', 'dermatology', 'orthopedics'][index % 5],
        "room": f"Doctor room {index}",
        "hourly_rate": round(10.0 * index + 0.99, 2),
        "accepting": index % 2 == 1,
    }


def sample_patient(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new patient (refs point at seeded records)."""
    return {
        "name": f"Patient name {index}",
        "email": f"patient{index}@example.com",
        "phone": f"Patient phone {index}",
        "birth_date": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "insurance": f"Patient insurance {index}",
        "allergies": f"Notes about patient {index}.",
        "active": index % 2 == 1,
    }


def sample_appointment(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new appointment (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "patient_id": (index - 1) % 3 + 1,
        "day": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "slot": index + 1,
        "duration": index + 1,
        "reason": f"Notes about appointment {index}.",
        "status": ['booked', 'checked_in', 'completed', 'cancelled', 'no_show'][index % 5],
        "fee": round(10.0 * index + 0.99, 2),
    }


def sample_prescription(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new prescription (refs point at seeded records)."""
    return {
        "appointment_id": (index - 1) % 3 + 1,
        "drug": f"Prescription drug {index}",
        "dose_mg": index + 1,
        "times_per_day": index + 1,
        "days": index + 1,
        "refills": index + 1,
        "notes": f"Notes about prescription {index}.",
    }


def sample_invoice(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new invoice (refs point at seeded records)."""
    return {
        "patient_id": (index - 1) % 3 + 1,
        "issued": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "amount": round(10.0 * index + 0.99, 2),
        "paid": round(10.0 * index + 0.99, 2),
        "status": ['draft', 'sent', 'paid', 'void'][index % 4],
        "due": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_lab_result(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new lab result (refs point at seeded records)."""
    return {
        "patient_id": (index - 1) % 3 + 1,
        "test_name": f"Lab result test name {index}",
        "value": round(1.5 * index + 0.25, 2),
        "unit": f"Lab result unit {index}",
        "taken": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "flagged": index % 2 == 1,
    }


def sample_document(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new document (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "title": f"Document title {index}",
        "pages": index + 1,
        "signed": index % 2 == 1,
        "version": index + 1,
        "issued": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_notification(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new notification (refs point at seeded records)."""
    return {
        "recipient": f"notification{index}@example.com",
        "title": f"Notification title {index}",
        "sent": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "channel": ['email', 'sms', 'push'][index % 3],
        "read": index % 2 == 1,
    }


def sample_address(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new address (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "street": f"Address street {index}",
        "city": f"Address city {index}",
        "postcode": f"Address postcode {index}",
        "country": f"Address country {index}",
        "billing": index % 2 == 1,
    }


def sample_reminder(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new reminder (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "title": f"Reminder title {index}",
        "remind_on": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "done": index % 2 == 1,
        "priority": ['low', 'normal', 'high'][index % 3],
    }


def sample_setting(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new setting (refs point at seeded records)."""
    return {
        "key_name": f"Setting key name {index}",
        "value": f"Setting value {index}",
        "editable": index % 2 == 1,
        "changed": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_audit_entry(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new audit entry (refs point at seeded records)."""
    return {
        "actor": f"Audit entry actor {index}",
        "action": ['create', 'update', 'delete', 'login', 'export'][index % 5],
        "at": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "details": f"Notes about audit entry {index}.",
    }


def sample_note(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new note (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "subject": f"Note subject {index}",
        "body": f"Notes about note {index}.",
        "pinned": index % 2 == 1,
        "written": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_review(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new review (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "author": f"Review author {index}",
        "stars": index + 1,
        "comment": f"Notes about review {index}.",
        "verified": index % 2 == 1,
        "posted": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_contact_person(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new contact person (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "name": f"Contact person name {index}",
        "email": f"contact_person{index}@example.com",
        "phone": f"Contact person phone {index}",
        "role": f"Contact person role {index}",
        "primary": index % 2 == 1,
    }


def sample_discount(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new discount (refs point at seeded records)."""
    return {
        "code": f"Discount code {index}",
        "percent": round(1.5 * index + 0.25, 2),
        "starts": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "ends": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "active": index % 2 == 1,
    }


def sample_tag(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new tag (refs point at seeded records)."""
    return {
        "doctor_id": (index - 1) % 3 + 1,
        "label": f"Tag label {index}",
        "color": f"Tag color {index}",
        "usage": index + 1,
    }
