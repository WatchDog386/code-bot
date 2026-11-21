"""Storage for the Clinic Scheduling service: one thread-safe in-memory repository per
model, with the lookups the services and the API need, and JSON / CSV import-export.
"""

from __future__ import annotations

import csv
import io
import json
import threading
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import (
    Address,
    Appointment,
    AppointmentStatus,
    AuditEntry,
    AuditEntryAction,
    ContactPerson,
    Discount,
    Doctor,
    DoctorSpecialty,
    Document,
    Invoice,
    InvoiceStatus,
    LabResult,
    Note,
    Notification,
    NotificationChannel,
    Patient,
    Prescription,
    Reminder,
    ReminderPriority,
    Review,
    Setting,
    Tag,
)

T = TypeVar("T")


class Repository(Generic[T]):
    """Records kept in memory, keyed by id. Subclasses set `model`."""

    model: Any = None
    entity_name = "record"

    def __init__(self) -> None:
        self._items: Dict[int, T] = {}
        self._next_id = 1
        self._lock = threading.RLock()

    def add(self, item: T) -> T:
        """Store a new record and give it the next id."""
        with self._lock:
            item.id = self._next_id  # type: ignore[attr-defined]
            self._next_id += 1
            self._items[item.id] = item  # type: ignore[attr-defined]
            return item

    def get(self, item_id: int) -> Optional[T]:
        with self._lock:
            return self._items.get(item_id)

    def list(self) -> List[T]:
        """Every record, oldest first."""
        with self._lock:
            return [self._items[key] for key in sorted(self._items)]

    def save(self, item: T) -> T:
        """Replace an existing record."""
        with self._lock:
            key = item.id  # type: ignore[attr-defined]
            if key not in self._items:
                raise KeyError(key)
            self._items[key] = item
            return item

    def remove(self, item_id: int) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None

    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._next_id = 1

    def where(self, keep: Callable[[T], bool]) -> List[T]:
        """Records for which `keep(record)` is true."""
        return [item for item in self.list() if keep(item)]

    def first(self, keep: Callable[[T], bool]) -> Optional[T]:
        for item in self.list():
            if keep(item):
                return item
        return None

    def page(self, number: int = 1, size: int = 20) -> List[T]:
        """One page of records (pages start at 1)."""
        start = max(0, (number - 1) * size)
        return self.list()[start:start + size]

    def sorted_by(self, field_name: str, reverse: bool = False) -> List[T]:
        return sorted(self.list(), key=lambda item: getattr(item, field_name), reverse=reverse)

    def to_json(self) -> str:
        return json.dumps([item.to_dict() for item in self.list()], indent=2)  # type: ignore[attr-defined]

    def load_json(self, text: str) -> int:
        """Load records exported with `to_json()`; returns how many."""
        rows = json.loads(text)
        with self._lock:
            for row in rows:
                item = self.model.from_dict(row).validate()
                self._items[item.id] = item
                self._next_id = max(self._next_id, item.id + 1)
        return len(rows)

    def to_csv(self) -> str:
        """Every record as CSV with a header row."""
        names = ["id"] + [name for name in self.model.__dataclass_fields__ if name != "id"]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=names, lineterminator="\n")
        writer.writeheader()
        for item in self.list():
            writer.writerow(item.to_dict())  # type: ignore[attr-defined]
        return buffer.getvalue()


class DoctorRepository(Repository[Doctor]):
    """All doctors, with the lookups the services need."""

    model = Doctor
    entity_name = "doctor"

    def find_by_name(self, value: str) -> List[Doctor]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Doctor]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Doctor]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Doctor]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def with_specialty(self, value: Any) -> List[Doctor]:
        wanted = DoctorSpecialty(value)
        return self.where(lambda item: item.specialty == wanted)

    def count_by_specialty(self) -> Dict[str, int]:
        """How many records have each specialty."""
        counts = {member.value: 0 for member in DoctorSpecialty}
        for item in self.list():
            counts[DoctorSpecialty(item.specialty).value] += 1
        return counts

    def find_by_room(self, value: str) -> List[Doctor]:
        """Records whose room is exactly `value`."""
        return self.where(lambda item: item.room == value)

    def search_room(self, text: str) -> List[Doctor]:
        """Records whose room contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.room.lower())

    def between_hourly_rate(self, low: float, high: float) -> List[Doctor]:
        """Records whose hourly rate is within [low, high]."""
        return self.where(lambda item: low <= item.hourly_rate <= high)

    def total_hourly_rate(self) -> float:
        return sum(item.hourly_rate for item in self.list())

    def average_hourly_rate(self) -> float:
        items = self.list()
        return sum(item.hourly_rate for item in items) / len(items) if items else 0.0

    def max_hourly_rate(self) -> Optional[Doctor]:
        """The record with the highest hourly rate."""
        items = self.list()
        return max(items, key=lambda item: item.hourly_rate) if items else None

    def where_accepting(self, flag: bool = True) -> List[Doctor]:
        return self.where(lambda item: item.accepting is flag)

    def search(self, text: str) -> List[Doctor]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.room,
        )))


class PatientRepository(Repository[Patient]):
    """All patients, with the lookups the services need."""

    model = Patient
    entity_name = "patient"

    def find_by_name(self, value: str) -> List[Patient]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Patient]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Patient]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Patient]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def find_by_phone(self, value: str) -> List[Patient]:
        """Records whose phone is exactly `value`."""
        return self.where(lambda item: item.phone == value)

    def search_phone(self, text: str) -> List[Patient]:
        """Records whose phone contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.phone.lower())

    def birth_date_before(self, day: str) -> List[Patient]:
        return self.where(lambda item: item.birth_date < day)

    def birth_date_after(self, day: str) -> List[Patient]:
        return self.where(lambda item: item.birth_date > day)

    def birth_date_on(self, day: str) -> List[Patient]:
        return self.where(lambda item: item.birth_date == day)

    def find_by_insurance(self, value: str) -> List[Patient]:
        """Records whose insurance is exactly `value`."""
        return self.where(lambda item: item.insurance == value)

    def search_insurance(self, text: str) -> List[Patient]:
        """Records whose insurance contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.insurance.lower())

    def find_by_allergies(self, value: str) -> List[Patient]:
        """Records whose allergies is exactly `value`."""
        return self.where(lambda item: item.allergies == value)

    def search_allergies(self, text: str) -> List[Patient]:
        """Records whose allergies contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.allergies.lower())

    def where_active(self, flag: bool = True) -> List[Patient]:
        return self.where(lambda item: item.active is flag)

    def search(self, text: str) -> List[Patient]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.phone,
            item.insurance,
            item.allergies,
        )))


class AppointmentRepository(Repository[Appointment]):
    """All appointments, with the lookups the services need."""

    model = Appointment
    entity_name = "appointment"

    def for_doctor(self, doctor_id: int) -> List[Appointment]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def for_patient(self, patient_id: int) -> List[Appointment]:
        """Records linked to patient `patient_id`."""
        return self.where(lambda item: item.patient_id == patient_id)

    def count_for_patient(self, patient_id: int) -> int:
        return len(self.for_patient(patient_id))

    def day_before(self, day: str) -> List[Appointment]:
        return self.where(lambda item: item.day < day)

    def day_after(self, day: str) -> List[Appointment]:
        return self.where(lambda item: item.day > day)

    def day_on(self, day: str) -> List[Appointment]:
        return self.where(lambda item: item.day == day)

    def between_slot(self, low: float, high: float) -> List[Appointment]:
        """Records whose slot is within [low, high]."""
        return self.where(lambda item: low <= item.slot <= high)

    def total_slot(self) -> float:
        return sum(item.slot for item in self.list())

    def average_slot(self) -> float:
        items = self.list()
        return sum(item.slot for item in items) / len(items) if items else 0.0

    def max_slot(self) -> Optional[Appointment]:
        """The record with the highest slot."""
        items = self.list()
        return max(items, key=lambda item: item.slot) if items else None

    def between_duration(self, low: float, high: float) -> List[Appointment]:
        """Records whose duration is within [low, high]."""
        return self.where(lambda item: low <= item.duration <= high)

    def total_duration(self) -> float:
        return sum(item.duration for item in self.list())

    def average_duration(self) -> float:
        items = self.list()
        return sum(item.duration for item in items) / len(items) if items else 0.0

    def max_duration(self) -> Optional[Appointment]:
        """The record with the highest duration."""
        items = self.list()
        return max(items, key=lambda item: item.duration) if items else None

    def find_by_reason(self, value: str) -> List[Appointment]:
        """Records whose reason is exactly `value`."""
        return self.where(lambda item: item.reason == value)

    def search_reason(self, text: str) -> List[Appointment]:
        """Records whose reason contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.reason.lower())

    def with_status(self, value: Any) -> List[Appointment]:
        wanted = AppointmentStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in AppointmentStatus}
        for item in self.list():
            counts[AppointmentStatus(item.status).value] += 1
        return counts

    def between_fee(self, low: float, high: float) -> List[Appointment]:
        """Records whose fee is within [low, high]."""
        return self.where(lambda item: low <= item.fee <= high)

    def total_fee(self) -> float:
        return sum(item.fee for item in self.list())

    def average_fee(self) -> float:
        items = self.list()
        return sum(item.fee for item in items) / len(items) if items else 0.0

    def max_fee(self) -> Optional[Appointment]:
        """The record with the highest fee."""
        items = self.list()
        return max(items, key=lambda item: item.fee) if items else None

    def search(self, text: str) -> List[Appointment]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.reason,
        )))


class PrescriptionRepository(Repository[Prescription]):
    """All prescriptions, with the lookups the services need."""

    model = Prescription
    entity_name = "prescription"

    def for_appointment(self, appointment_id: int) -> List[Prescription]:
        """Records linked to appointment `appointment_id`."""
        return self.where(lambda item: item.appointment_id == appointment_id)

    def count_for_appointment(self, appointment_id: int) -> int:
        return len(self.for_appointment(appointment_id))

    def find_by_drug(self, value: str) -> List[Prescription]:
        """Records whose drug is exactly `value`."""
        return self.where(lambda item: item.drug == value)

    def search_drug(self, text: str) -> List[Prescription]:
        """Records whose drug contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.drug.lower())

    def between_dose_mg(self, low: float, high: float) -> List[Prescription]:
        """Records whose dose mg is within [low, high]."""
        return self.where(lambda item: low <= item.dose_mg <= high)

    def total_dose_mg(self) -> float:
        return sum(item.dose_mg for item in self.list())

    def average_dose_mg(self) -> float:
        items = self.list()
        return sum(item.dose_mg for item in items) / len(items) if items else 0.0

    def max_dose_mg(self) -> Optional[Prescription]:
        """The record with the highest dose mg."""
        items = self.list()
        return max(items, key=lambda item: item.dose_mg) if items else None

    def between_times_per_day(self, low: float, high: float) -> List[Prescription]:
        """Records whose times per day is within [low, high]."""
        return self.where(lambda item: low <= item.times_per_day <= high)

    def total_times_per_day(self) -> float:
        return sum(item.times_per_day for item in self.list())

    def average_times_per_day(self) -> float:
        items = self.list()
        return sum(item.times_per_day for item in items) / len(items) if items else 0.0

    def max_times_per_day(self) -> Optional[Prescription]:
        """The record with the highest times per day."""
        items = self.list()
        return max(items, key=lambda item: item.times_per_day) if items else None

    def between_days(self, low: float, high: float) -> List[Prescription]:
        """Records whose days is within [low, high]."""
        return self.where(lambda item: low <= item.days <= high)

    def total_days(self) -> float:
        return sum(item.days for item in self.list())

    def average_days(self) -> float:
        items = self.list()
        return sum(item.days for item in items) / len(items) if items else 0.0

    def max_days(self) -> Optional[Prescription]:
        """The record with the highest days."""
        items = self.list()
        return max(items, key=lambda item: item.days) if items else None

    def between_refills(self, low: float, high: float) -> List[Prescription]:
        """Records whose refills is within [low, high]."""
        return self.where(lambda item: low <= item.refills <= high)

    def total_refills(self) -> float:
        return sum(item.refills for item in self.list())

    def average_refills(self) -> float:
        items = self.list()
        return sum(item.refills for item in items) / len(items) if items else 0.0

    def max_refills(self) -> Optional[Prescription]:
        """The record with the highest refills."""
        items = self.list()
        return max(items, key=lambda item: item.refills) if items else None

    def find_by_notes(self, value: str) -> List[Prescription]:
        """Records whose notes is exactly `value`."""
        return self.where(lambda item: item.notes == value)

    def search_notes(self, text: str) -> List[Prescription]:
        """Records whose notes contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.notes.lower())

    def search(self, text: str) -> List[Prescription]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.drug,
            item.notes,
        )))


class InvoiceRepository(Repository[Invoice]):
    """All invoices, with the lookups the services need."""

    model = Invoice
    entity_name = "invoice"

    def for_patient(self, patient_id: int) -> List[Invoice]:
        """Records linked to patient `patient_id`."""
        return self.where(lambda item: item.patient_id == patient_id)

    def count_for_patient(self, patient_id: int) -> int:
        return len(self.for_patient(patient_id))

    def issued_before(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.issued < day)

    def issued_after(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.issued > day)

    def issued_on(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.issued == day)

    def between_amount(self, low: float, high: float) -> List[Invoice]:
        """Records whose amount is within [low, high]."""
        return self.where(lambda item: low <= item.amount <= high)

    def total_amount(self) -> float:
        return sum(item.amount for item in self.list())

    def average_amount(self) -> float:
        items = self.list()
        return sum(item.amount for item in items) / len(items) if items else 0.0

    def max_amount(self) -> Optional[Invoice]:
        """The record with the highest amount."""
        items = self.list()
        return max(items, key=lambda item: item.amount) if items else None

    def between_paid(self, low: float, high: float) -> List[Invoice]:
        """Records whose paid is within [low, high]."""
        return self.where(lambda item: low <= item.paid <= high)

    def total_paid(self) -> float:
        return sum(item.paid for item in self.list())

    def average_paid(self) -> float:
        items = self.list()
        return sum(item.paid for item in items) / len(items) if items else 0.0

    def max_paid(self) -> Optional[Invoice]:
        """The record with the highest paid."""
        items = self.list()
        return max(items, key=lambda item: item.paid) if items else None

    def with_status(self, value: Any) -> List[Invoice]:
        wanted = InvoiceStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in InvoiceStatus}
        for item in self.list():
            counts[InvoiceStatus(item.status).value] += 1
        return counts

    def due_before(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.due < day)

    def due_after(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.due > day)

    def due_on(self, day: str) -> List[Invoice]:
        return self.where(lambda item: item.due == day)

    def search(self, text: str) -> List[Invoice]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: needle == str(item.id))


class LabResultRepository(Repository[LabResult]):
    """All lab results, with the lookups the services need."""

    model = LabResult
    entity_name = "lab_result"

    def for_patient(self, patient_id: int) -> List[LabResult]:
        """Records linked to patient `patient_id`."""
        return self.where(lambda item: item.patient_id == patient_id)

    def count_for_patient(self, patient_id: int) -> int:
        return len(self.for_patient(patient_id))

    def find_by_test_name(self, value: str) -> List[LabResult]:
        """Records whose test name is exactly `value`."""
        return self.where(lambda item: item.test_name == value)

    def search_test_name(self, text: str) -> List[LabResult]:
        """Records whose test name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.test_name.lower())

    def between_value(self, low: float, high: float) -> List[LabResult]:
        """Records whose value is within [low, high]."""
        return self.where(lambda item: low <= item.value <= high)

    def total_value(self) -> float:
        return sum(item.value for item in self.list())

    def average_value(self) -> float:
        items = self.list()
        return sum(item.value for item in items) / len(items) if items else 0.0

    def max_value(self) -> Optional[LabResult]:
        """The record with the highest value."""
        items = self.list()
        return max(items, key=lambda item: item.value) if items else None

    def find_by_unit(self, value: str) -> List[LabResult]:
        """Records whose unit is exactly `value`."""
        return self.where(lambda item: item.unit == value)

    def search_unit(self, text: str) -> List[LabResult]:
        """Records whose unit contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.unit.lower())

    def taken_before(self, day: str) -> List[LabResult]:
        return self.where(lambda item: item.taken < day)

    def taken_after(self, day: str) -> List[LabResult]:
        return self.where(lambda item: item.taken > day)

    def taken_on(self, day: str) -> List[LabResult]:
        return self.where(lambda item: item.taken == day)

    def where_flagged(self, flag: bool = True) -> List[LabResult]:
        return self.where(lambda item: item.flagged is flag)

    def search(self, text: str) -> List[LabResult]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.test_name,
            item.unit,
        )))


class DocumentRepository(Repository[Document]):
    """All documents, with the lookups the services need."""

    model = Document
    entity_name = "document"

    def for_doctor(self, doctor_id: int) -> List[Document]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_title(self, value: str) -> List[Document]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Document]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def between_pages(self, low: float, high: float) -> List[Document]:
        """Records whose pages is within [low, high]."""
        return self.where(lambda item: low <= item.pages <= high)

    def total_pages(self) -> float:
        return sum(item.pages for item in self.list())

    def average_pages(self) -> float:
        items = self.list()
        return sum(item.pages for item in items) / len(items) if items else 0.0

    def max_pages(self) -> Optional[Document]:
        """The record with the highest pages."""
        items = self.list()
        return max(items, key=lambda item: item.pages) if items else None

    def where_signed(self, flag: bool = True) -> List[Document]:
        return self.where(lambda item: item.signed is flag)

    def between_version(self, low: float, high: float) -> List[Document]:
        """Records whose version is within [low, high]."""
        return self.where(lambda item: low <= item.version <= high)

    def total_version(self) -> float:
        return sum(item.version for item in self.list())

    def average_version(self) -> float:
        items = self.list()
        return sum(item.version for item in items) / len(items) if items else 0.0

    def max_version(self) -> Optional[Document]:
        """The record with the highest version."""
        items = self.list()
        return max(items, key=lambda item: item.version) if items else None

    def issued_before(self, day: str) -> List[Document]:
        return self.where(lambda item: item.issued < day)

    def issued_after(self, day: str) -> List[Document]:
        return self.where(lambda item: item.issued > day)

    def issued_on(self, day: str) -> List[Document]:
        return self.where(lambda item: item.issued == day)

    def search(self, text: str) -> List[Document]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.title,
        )))


class NotificationRepository(Repository[Notification]):
    """All notifications, with the lookups the services need."""

    model = Notification
    entity_name = "notification"

    def find_by_recipient(self, value: str) -> List[Notification]:
        """Records whose recipient is exactly `value`."""
        return self.where(lambda item: item.recipient == value)

    def search_recipient(self, text: str) -> List[Notification]:
        """Records whose recipient contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.recipient.lower())

    def find_by_title(self, value: str) -> List[Notification]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Notification]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def sent_before(self, day: str) -> List[Notification]:
        return self.where(lambda item: item.sent < day)

    def sent_after(self, day: str) -> List[Notification]:
        return self.where(lambda item: item.sent > day)

    def sent_on(self, day: str) -> List[Notification]:
        return self.where(lambda item: item.sent == day)

    def with_channel(self, value: Any) -> List[Notification]:
        wanted = NotificationChannel(value)
        return self.where(lambda item: item.channel == wanted)

    def count_by_channel(self) -> Dict[str, int]:
        """How many records have each channel."""
        counts = {member.value: 0 for member in NotificationChannel}
        for item in self.list():
            counts[NotificationChannel(item.channel).value] += 1
        return counts

    def where_read(self, flag: bool = True) -> List[Notification]:
        return self.where(lambda item: item.read is flag)

    def search(self, text: str) -> List[Notification]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.recipient,
            item.title,
        )))


class AddressRepository(Repository[Address]):
    """All addresses, with the lookups the services need."""

    model = Address
    entity_name = "address"

    def for_doctor(self, doctor_id: int) -> List[Address]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_street(self, value: str) -> List[Address]:
        """Records whose street is exactly `value`."""
        return self.where(lambda item: item.street == value)

    def search_street(self, text: str) -> List[Address]:
        """Records whose street contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.street.lower())

    def find_by_city(self, value: str) -> List[Address]:
        """Records whose city is exactly `value`."""
        return self.where(lambda item: item.city == value)

    def search_city(self, text: str) -> List[Address]:
        """Records whose city contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.city.lower())

    def find_by_postcode(self, value: str) -> List[Address]:
        """Records whose postcode is exactly `value`."""
        return self.where(lambda item: item.postcode == value)

    def search_postcode(self, text: str) -> List[Address]:
        """Records whose postcode contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.postcode.lower())

    def find_by_country(self, value: str) -> List[Address]:
        """Records whose country is exactly `value`."""
        return self.where(lambda item: item.country == value)

    def search_country(self, text: str) -> List[Address]:
        """Records whose country contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.country.lower())

    def where_billing(self, flag: bool = True) -> List[Address]:
        return self.where(lambda item: item.billing is flag)

    def search(self, text: str) -> List[Address]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.street,
            item.city,
            item.postcode,
            item.country,
        )))


class ReminderRepository(Repository[Reminder]):
    """All reminders, with the lookups the services need."""

    model = Reminder
    entity_name = "reminder"

    def for_doctor(self, doctor_id: int) -> List[Reminder]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_title(self, value: str) -> List[Reminder]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Reminder]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def remind_on_before(self, day: str) -> List[Reminder]:
        return self.where(lambda item: item.remind_on < day)

    def remind_on_after(self, day: str) -> List[Reminder]:
        return self.where(lambda item: item.remind_on > day)

    def remind_on_on(self, day: str) -> List[Reminder]:
        return self.where(lambda item: item.remind_on == day)

    def where_done(self, flag: bool = True) -> List[Reminder]:
        return self.where(lambda item: item.done is flag)

    def with_priority(self, value: Any) -> List[Reminder]:
        wanted = ReminderPriority(value)
        return self.where(lambda item: item.priority == wanted)

    def count_by_priority(self) -> Dict[str, int]:
        """How many records have each priority."""
        counts = {member.value: 0 for member in ReminderPriority}
        for item in self.list():
            counts[ReminderPriority(item.priority).value] += 1
        return counts

    def search(self, text: str) -> List[Reminder]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.title,
        )))


class SettingRepository(Repository[Setting]):
    """All settings, with the lookups the services need."""

    model = Setting
    entity_name = "setting"

    def find_by_key_name(self, value: str) -> List[Setting]:
        """Records whose key name is exactly `value`."""
        return self.where(lambda item: item.key_name == value)

    def search_key_name(self, text: str) -> List[Setting]:
        """Records whose key name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.key_name.lower())

    def find_by_value(self, value: str) -> List[Setting]:
        """Records whose value is exactly `value`."""
        return self.where(lambda item: item.value == value)

    def search_value(self, text: str) -> List[Setting]:
        """Records whose value contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.value.lower())

    def where_editable(self, flag: bool = True) -> List[Setting]:
        return self.where(lambda item: item.editable is flag)

    def changed_before(self, day: str) -> List[Setting]:
        return self.where(lambda item: item.changed < day)

    def changed_after(self, day: str) -> List[Setting]:
        return self.where(lambda item: item.changed > day)

    def changed_on(self, day: str) -> List[Setting]:
        return self.where(lambda item: item.changed == day)

    def search(self, text: str) -> List[Setting]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.key_name,
            item.value,
        )))


class AuditEntryRepository(Repository[AuditEntry]):
    """All audit entries, with the lookups the services need."""

    model = AuditEntry
    entity_name = "audit_entry"

    def find_by_actor(self, value: str) -> List[AuditEntry]:
        """Records whose actor is exactly `value`."""
        return self.where(lambda item: item.actor == value)

    def search_actor(self, text: str) -> List[AuditEntry]:
        """Records whose actor contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.actor.lower())

    def with_action(self, value: Any) -> List[AuditEntry]:
        wanted = AuditEntryAction(value)
        return self.where(lambda item: item.action == wanted)

    def count_by_action(self) -> Dict[str, int]:
        """How many records have each action."""
        counts = {member.value: 0 for member in AuditEntryAction}
        for item in self.list():
            counts[AuditEntryAction(item.action).value] += 1
        return counts

    def at_before(self, day: str) -> List[AuditEntry]:
        return self.where(lambda item: item.at < day)

    def at_after(self, day: str) -> List[AuditEntry]:
        return self.where(lambda item: item.at > day)

    def at_on(self, day: str) -> List[AuditEntry]:
        return self.where(lambda item: item.at == day)

    def find_by_details(self, value: str) -> List[AuditEntry]:
        """Records whose details is exactly `value`."""
        return self.where(lambda item: item.details == value)

    def search_details(self, text: str) -> List[AuditEntry]:
        """Records whose details contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.details.lower())

    def search(self, text: str) -> List[AuditEntry]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.actor,
            item.details,
        )))


class NoteRepository(Repository[Note]):
    """All notes, with the lookups the services need."""

    model = Note
    entity_name = "note"

    def for_doctor(self, doctor_id: int) -> List[Note]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_subject(self, value: str) -> List[Note]:
        """Records whose subject is exactly `value`."""
        return self.where(lambda item: item.subject == value)

    def search_subject(self, text: str) -> List[Note]:
        """Records whose subject contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.subject.lower())

    def find_by_body(self, value: str) -> List[Note]:
        """Records whose body is exactly `value`."""
        return self.where(lambda item: item.body == value)

    def search_body(self, text: str) -> List[Note]:
        """Records whose body contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.body.lower())

    def where_pinned(self, flag: bool = True) -> List[Note]:
        return self.where(lambda item: item.pinned is flag)

    def written_before(self, day: str) -> List[Note]:
        return self.where(lambda item: item.written < day)

    def written_after(self, day: str) -> List[Note]:
        return self.where(lambda item: item.written > day)

    def written_on(self, day: str) -> List[Note]:
        return self.where(lambda item: item.written == day)

    def search(self, text: str) -> List[Note]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.subject,
            item.body,
        )))


class ReviewRepository(Repository[Review]):
    """All reviews, with the lookups the services need."""

    model = Review
    entity_name = "review"

    def for_doctor(self, doctor_id: int) -> List[Review]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_author(self, value: str) -> List[Review]:
        """Records whose author is exactly `value`."""
        return self.where(lambda item: item.author == value)

    def search_author(self, text: str) -> List[Review]:
        """Records whose author contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.author.lower())

    def between_stars(self, low: float, high: float) -> List[Review]:
        """Records whose stars is within [low, high]."""
        return self.where(lambda item: low <= item.stars <= high)

    def total_stars(self) -> float:
        return sum(item.stars for item in self.list())

    def average_stars(self) -> float:
        items = self.list()
        return sum(item.stars for item in items) / len(items) if items else 0.0

    def max_stars(self) -> Optional[Review]:
        """The record with the highest stars."""
        items = self.list()
        return max(items, key=lambda item: item.stars) if items else None

    def find_by_comment(self, value: str) -> List[Review]:
        """Records whose comment is exactly `value`."""
        return self.where(lambda item: item.comment == value)

    def search_comment(self, text: str) -> List[Review]:
        """Records whose comment contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.comment.lower())

    def where_verified(self, flag: bool = True) -> List[Review]:
        return self.where(lambda item: item.verified is flag)

    def posted_before(self, day: str) -> List[Review]:
        return self.where(lambda item: item.posted < day)

    def posted_after(self, day: str) -> List[Review]:
        return self.where(lambda item: item.posted > day)

    def posted_on(self, day: str) -> List[Review]:
        return self.where(lambda item: item.posted == day)

    def search(self, text: str) -> List[Review]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.author,
            item.comment,
        )))


class ContactPersonRepository(Repository[ContactPerson]):
    """All contact persons, with the lookups the services need."""

    model = ContactPerson
    entity_name = "contact_person"

    def for_doctor(self, doctor_id: int) -> List[ContactPerson]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_name(self, value: str) -> List[ContactPerson]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[ContactPerson]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[ContactPerson]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[ContactPerson]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def find_by_phone(self, value: str) -> List[ContactPerson]:
        """Records whose phone is exactly `value`."""
        return self.where(lambda item: item.phone == value)

    def search_phone(self, text: str) -> List[ContactPerson]:
        """Records whose phone contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.phone.lower())

    def find_by_role(self, value: str) -> List[ContactPerson]:
        """Records whose role is exactly `value`."""
        return self.where(lambda item: item.role == value)

    def search_role(self, text: str) -> List[ContactPerson]:
        """Records whose role contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.role.lower())

    def where_primary(self, flag: bool = True) -> List[ContactPerson]:
        return self.where(lambda item: item.primary is flag)

    def search(self, text: str) -> List[ContactPerson]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.phone,
            item.role,
        )))


class DiscountRepository(Repository[Discount]):
    """All discounts, with the lookups the services need."""

    model = Discount
    entity_name = "discount"

    def find_by_code(self, value: str) -> List[Discount]:
        """Records whose code is exactly `value`."""
        return self.where(lambda item: item.code == value)

    def search_code(self, text: str) -> List[Discount]:
        """Records whose code contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.code.lower())

    def between_percent(self, low: float, high: float) -> List[Discount]:
        """Records whose percent is within [low, high]."""
        return self.where(lambda item: low <= item.percent <= high)

    def total_percent(self) -> float:
        return sum(item.percent for item in self.list())

    def average_percent(self) -> float:
        items = self.list()
        return sum(item.percent for item in items) / len(items) if items else 0.0

    def max_percent(self) -> Optional[Discount]:
        """The record with the highest percent."""
        items = self.list()
        return max(items, key=lambda item: item.percent) if items else None

    def starts_before(self, day: str) -> List[Discount]:
        return self.where(lambda item: item.starts < day)

    def starts_after(self, day: str) -> List[Discount]:
        return self.where(lambda item: item.starts > day)

    def starts_on(self, day: str) -> List[Discount]:
        return self.where(lambda item: item.starts == day)

    def ends_before(self, day: str) -> List[Discount]:
        return self.where(lambda item: item.ends < day)

    def ends_after(self, day: str) -> List[Discount]:
        return self.where(lambda item: item.ends > day)

    def ends_on(self, day: str) -> List[Discount]:
        return self.where(lambda item: item.ends == day)

    def where_active(self, flag: bool = True) -> List[Discount]:
        return self.where(lambda item: item.active is flag)

    def search(self, text: str) -> List[Discount]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.code,
        )))


class TagRepository(Repository[Tag]):
    """All tags, with the lookups the services need."""

    model = Tag
    entity_name = "tag"

    def for_doctor(self, doctor_id: int) -> List[Tag]:
        """Records linked to doctor `doctor_id`."""
        return self.where(lambda item: item.doctor_id == doctor_id)

    def count_for_doctor(self, doctor_id: int) -> int:
        return len(self.for_doctor(doctor_id))

    def find_by_label(self, value: str) -> List[Tag]:
        """Records whose label is exactly `value`."""
        return self.where(lambda item: item.label == value)

    def search_label(self, text: str) -> List[Tag]:
        """Records whose label contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.label.lower())

    def find_by_color(self, value: str) -> List[Tag]:
        """Records whose color is exactly `value`."""
        return self.where(lambda item: item.color == value)

    def search_color(self, text: str) -> List[Tag]:
        """Records whose color contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.color.lower())

    def between_usage(self, low: float, high: float) -> List[Tag]:
        """Records whose usage is within [low, high]."""
        return self.where(lambda item: low <= item.usage <= high)

    def total_usage(self) -> float:
        return sum(item.usage for item in self.list())

    def average_usage(self) -> float:
        items = self.list()
        return sum(item.usage for item in items) / len(items) if items else 0.0

    def max_usage(self) -> Optional[Tag]:
        """The record with the highest usage."""
        items = self.list()
        return max(items, key=lambda item: item.usage) if items else None

    def search(self, text: str) -> List[Tag]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.label,
            item.color,
        )))
