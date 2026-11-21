"""Domain models for the Clinic Scheduling service.

Every model is a dataclass with a
`validate()` that checks and normalises its fields, plus `to_dict()` / `from_dict()`
for the JSON API and `apply()` for partial updates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import date
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Tuple, Type

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_INT = 1_000_000_000


class ValidationError(ValueError):
    """A field holds a value the service can't accept."""

    def __init__(self, field_name: str, message: str) -> None:
        super().__init__(f"{field_name}: {message}")
        self.field_name = field_name
        self.message = message


def check_text(name: str, value: Any, max_length: int = 120, required: bool = True) -> str:
    """Trimmed text, not empty unless optional, and not too long."""
    if not isinstance(value, str):
        raise ValidationError(name, "must be text")
    cleaned = value.strip()
    if required and not cleaned:
        raise ValidationError(name, "is required")
    if len(cleaned) > max_length:
        raise ValidationError(name, f"must be at most {max_length} characters")
    return cleaned


def check_email(name: str, value: Any) -> str:
    """A plausible e-mail address, stored in lower case."""
    text = check_text(name, value, max_length=254)
    if not EMAIL_RE.match(text):
        raise ValidationError(name, "must be an e-mail address")
    return text.lower()


def check_int(name: str, value: Any, minimum: int = 0, maximum: int = MAX_INT) -> int:
    """A whole number inside [minimum, maximum]."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(name, "must be a whole number")
    if value < minimum:
        raise ValidationError(name, f"must be at least {minimum}")
    if value > maximum:
        raise ValidationError(name, f"must be at most {maximum}")
    return value


def check_number(name: str, value: Any, minimum: float = 0.0) -> float:
    """Any number that isn't negative."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(name, "must be a number")
    if value < minimum:
        raise ValidationError(name, f"must be at least {minimum}")
    return float(value)


def check_money(name: str, value: Any) -> float:
    """An amount of money, rounded to cents."""
    return round(check_number(name, value), 2)


def check_flag(name: str, value: Any) -> bool:
    """A real boolean (no "yes"/"no" strings)."""
    if not isinstance(value, bool):
        raise ValidationError(name, "must be true or false")
    return value


def check_date(name: str, value: Any) -> str:
    """An ISO date (YYYY-MM-DD) that exists in the calendar."""
    text = check_text(name, value, max_length=10)
    if not DATE_RE.match(text):
        raise ValidationError(name, "must look like YYYY-MM-DD")
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValidationError(name, "is not a real date") from None
    return text


def check_ref(name: str, value: Any) -> int:
    """The id of another record (existence is checked by the services)."""
    return check_int(name, value, minimum=1)


def check_choice(name: str, value: Any, choices: Type[Enum]) -> Any:
    """One of the values of an Enum."""
    if isinstance(value, choices):
        return value
    try:
        return choices(value)
    except ValueError:
        allowed = ", ".join(member.value for member in choices)
        raise ValidationError(name, f"must be one of: {allowed}") from None


def unknown_fields(data: Dict[str, Any], known: FrozenSet[str]) -> Optional[str]:
    """The first key in `data` that isn't a field, if any."""
    extra = sorted(set(data) - known)
    return extra[0] if extra else None


class DoctorSpecialty(str, Enum):
    """Allowed values of Doctor.specialty."""

    GENERAL = "general"
    PEDIATRICS = "pediatrics"
    CARDIOLOGY = "cardiology"
    DERMATOLOGY = "dermatology"
    ORTHOPEDICS = "orthopedics"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class AppointmentStatus(str, Enum):
    """Allowed values of Appointment.status."""

    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class InvoiceStatus(str, Enum):
    """Allowed values of Invoice.status."""

    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    VOID = "void"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class NotificationChannel(str, Enum):
    """Allowed values of Notification.channel."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class ReminderPriority(str, Enum):
    """Allowed values of Reminder.priority."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class AuditEntryAction(str, Enum):
    """Allowed values of AuditEntry.action."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    EXPORT = "export"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


# -------------------------------------------------------------------------- Doctor
DOCTOR_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "specialty",
    "room",
    "hourly_rate",
    "accepting",
})
DOCTOR_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'specialty', 'room', 'hourly_rate',)
DOCTOR_REQUIRED: Tuple[str, ...] = ('name', 'email', 'room',)


def validate_doctor_name(value: Any) -> str:
    """Check Doctor.name (str)."""
    return check_text("name", value)


def validate_doctor_email(value: Any) -> str:
    """Check Doctor.email (email)."""
    return check_email("email", value)


def validate_doctor_specialty(value: Any) -> DoctorSpecialty:
    """Check Doctor.specialty (enum)."""
    return check_choice("specialty", value, DoctorSpecialty)


def validate_doctor_room(value: Any) -> str:
    """Check Doctor.room (str)."""
    return check_text("room", value)


def validate_doctor_hourly_rate(value: Any) -> float:
    """Check Doctor.hourly_rate (money)."""
    return check_money("hourly_rate", value)


def validate_doctor_accepting(value: Any) -> bool:
    """Check Doctor.accepting (bool)."""
    return check_flag("accepting", value)


@dataclass
class Doctor:
    """A doctor record."""

    id: int = 0
    name: str = ""
    email: str = ""
    specialty: DoctorSpecialty = DoctorSpecialty.GENERAL
    room: str = ""
    hourly_rate: float = 0.0
    accepting: bool = False

    def validate(self) -> "Doctor":
        """Check every field and normalise the values in place."""
        self.name = validate_doctor_name(self.name)
        self.email = validate_doctor_email(self.email)
        self.specialty = validate_doctor_specialty(self.specialty)
        self.room = validate_doctor_room(self.room)
        self.hourly_rate = validate_doctor_hourly_rate(self.hourly_rate)
        self.accepting = validate_doctor_accepting(self.accepting)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "specialty": self.specialty.value,
            "room": self.room,
            "hourly_rate": self.hourly_rate,
            "accepting": self.accepting,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Doctor":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, DOCTOR_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "specialty" in data:
            item.specialty = data["specialty"]
        if "room" in data:
            item.room = data["room"]
        if "hourly_rate" in data:
            item.hourly_rate = data["hourly_rate"]
        if "accepting" in data:
            item.accepting = data["accepting"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Doctor":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, DOCTOR_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Doctor #{self.id}: {self.name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in DOCTOR_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Patient
PATIENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "phone",
    "birth_date",
    "insurance",
    "allergies",
    "active",
})
PATIENT_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'phone', 'birth_date', 'insurance',)
PATIENT_REQUIRED: Tuple[str, ...] = ('name', 'email', 'phone', 'birth_date', 'insurance',)


def validate_patient_name(value: Any) -> str:
    """Check Patient.name (str)."""
    return check_text("name", value)


def validate_patient_email(value: Any) -> str:
    """Check Patient.email (email)."""
    return check_email("email", value)


def validate_patient_phone(value: Any) -> str:
    """Check Patient.phone (str)."""
    return check_text("phone", value)


def validate_patient_birth_date(value: Any) -> str:
    """Check Patient.birth_date (date)."""
    return check_date("birth_date", value)


def validate_patient_insurance(value: Any) -> str:
    """Check Patient.insurance (str)."""
    return check_text("insurance", value)


def validate_patient_allergies(value: Any) -> str:
    """Check Patient.allergies (text)."""
    return check_text("allergies", value, max_length=2000, required=False)


def validate_patient_active(value: Any) -> bool:
    """Check Patient.active (bool)."""
    return check_flag("active", value)


@dataclass
class Patient:
    """A patient record."""

    id: int = 0
    name: str = ""
    email: str = ""
    phone: str = ""
    birth_date: str = ""
    insurance: str = ""
    allergies: str = ""
    active: bool = False

    def validate(self) -> "Patient":
        """Check every field and normalise the values in place."""
        self.name = validate_patient_name(self.name)
        self.email = validate_patient_email(self.email)
        self.phone = validate_patient_phone(self.phone)
        self.birth_date = validate_patient_birth_date(self.birth_date)
        self.insurance = validate_patient_insurance(self.insurance)
        self.allergies = validate_patient_allergies(self.allergies)
        self.active = validate_patient_active(self.active)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "birth_date": self.birth_date,
            "insurance": self.insurance,
            "allergies": self.allergies,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Patient":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, PATIENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "phone" in data:
            item.phone = data["phone"]
        if "birth_date" in data:
            item.birth_date = data["birth_date"]
        if "insurance" in data:
            item.insurance = data["insurance"]
        if "allergies" in data:
            item.allergies = data["allergies"]
        if "active" in data:
            item.active = data["active"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Patient":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, PATIENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Patient #{self.id}: {self.name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in PATIENT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Appointment
APPOINTMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "patient_id",
    "day",
    "slot",
    "duration",
    "reason",
    "status",
    "fee",
})
APPOINTMENT_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'patient_id', 'day', 'slot', 'duration', 'status', 'fee',)
APPOINTMENT_REQUIRED: Tuple[str, ...] = ('doctor_id', 'patient_id', 'day',)


def validate_appointment_doctor_id(value: Any) -> int:
    """Check Appointment.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_appointment_patient_id(value: Any) -> int:
    """Check Appointment.patient_id (ref)."""
    return check_ref("patient_id", value)


def validate_appointment_day(value: Any) -> str:
    """Check Appointment.day (date)."""
    return check_date("day", value)


def validate_appointment_slot(value: Any) -> int:
    """Check Appointment.slot (int)."""
    return check_int("slot", value)


def validate_appointment_duration(value: Any) -> int:
    """Check Appointment.duration (int)."""
    return check_int("duration", value)


def validate_appointment_reason(value: Any) -> str:
    """Check Appointment.reason (text)."""
    return check_text("reason", value, max_length=2000, required=False)


def validate_appointment_status(value: Any) -> AppointmentStatus:
    """Check Appointment.status (enum)."""
    return check_choice("status", value, AppointmentStatus)


def validate_appointment_fee(value: Any) -> float:
    """Check Appointment.fee (money)."""
    return check_money("fee", value)


@dataclass
class Appointment:
    """A appointment record."""

    id: int = 0
    doctor_id: int = 0
    patient_id: int = 0
    day: str = ""
    slot: int = 0
    duration: int = 0
    reason: str = ""
    status: AppointmentStatus = AppointmentStatus.BOOKED
    fee: float = 0.0

    def validate(self) -> "Appointment":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_appointment_doctor_id(self.doctor_id)
        self.patient_id = validate_appointment_patient_id(self.patient_id)
        self.day = validate_appointment_day(self.day)
        self.slot = validate_appointment_slot(self.slot)
        self.duration = validate_appointment_duration(self.duration)
        self.reason = validate_appointment_reason(self.reason)
        self.status = validate_appointment_status(self.status)
        self.fee = validate_appointment_fee(self.fee)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "patient_id": self.patient_id,
            "day": self.day,
            "slot": self.slot,
            "duration": self.duration,
            "reason": self.reason,
            "status": self.status.value,
            "fee": self.fee,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Appointment":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, APPOINTMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "patient_id" in data:
            item.patient_id = data["patient_id"]
        if "day" in data:
            item.day = data["day"]
        if "slot" in data:
            item.slot = data["slot"]
        if "duration" in data:
            item.duration = data["duration"]
        if "reason" in data:
            item.reason = data["reason"]
        if "status" in data:
            item.status = data["status"]
        if "fee" in data:
            item.fee = data["fee"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Appointment":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, APPOINTMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Appointment #{self.id}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in APPOINTMENT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Prescription
PRESCRIPTION_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "appointment_id",
    "drug",
    "dose_mg",
    "times_per_day",
    "days",
    "refills",
    "notes",
})
PRESCRIPTION_SORTABLE: Tuple[str, ...] = ('id', 'appointment_id', 'drug', 'dose_mg', 'times_per_day', 'days', 'refills',)
PRESCRIPTION_REQUIRED: Tuple[str, ...] = ('appointment_id', 'drug',)


def validate_prescription_appointment_id(value: Any) -> int:
    """Check Prescription.appointment_id (ref)."""
    return check_ref("appointment_id", value)


def validate_prescription_drug(value: Any) -> str:
    """Check Prescription.drug (str)."""
    return check_text("drug", value)


def validate_prescription_dose_mg(value: Any) -> int:
    """Check Prescription.dose_mg (int)."""
    return check_int("dose_mg", value)


def validate_prescription_times_per_day(value: Any) -> int:
    """Check Prescription.times_per_day (int)."""
    return check_int("times_per_day", value)


def validate_prescription_days(value: Any) -> int:
    """Check Prescription.days (int)."""
    return check_int("days", value)


def validate_prescription_refills(value: Any) -> int:
    """Check Prescription.refills (int)."""
    return check_int("refills", value)


def validate_prescription_notes(value: Any) -> str:
    """Check Prescription.notes (text)."""
    return check_text("notes", value, max_length=2000, required=False)


@dataclass
class Prescription:
    """A prescription record."""

    id: int = 0
    appointment_id: int = 0
    drug: str = ""
    dose_mg: int = 0
    times_per_day: int = 0
    days: int = 0
    refills: int = 0
    notes: str = ""

    def validate(self) -> "Prescription":
        """Check every field and normalise the values in place."""
        self.appointment_id = validate_prescription_appointment_id(self.appointment_id)
        self.drug = validate_prescription_drug(self.drug)
        self.dose_mg = validate_prescription_dose_mg(self.dose_mg)
        self.times_per_day = validate_prescription_times_per_day(self.times_per_day)
        self.days = validate_prescription_days(self.days)
        self.refills = validate_prescription_refills(self.refills)
        self.notes = validate_prescription_notes(self.notes)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "drug": self.drug,
            "dose_mg": self.dose_mg,
            "times_per_day": self.times_per_day,
            "days": self.days,
            "refills": self.refills,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prescription":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, PRESCRIPTION_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "appointment_id" in data:
            item.appointment_id = data["appointment_id"]
        if "drug" in data:
            item.drug = data["drug"]
        if "dose_mg" in data:
            item.dose_mg = data["dose_mg"]
        if "times_per_day" in data:
            item.times_per_day = data["times_per_day"]
        if "days" in data:
            item.days = data["days"]
        if "refills" in data:
            item.refills = data["refills"]
        if "notes" in data:
            item.notes = data["notes"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Prescription":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, PRESCRIPTION_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Prescription #{self.id}: {self.drug}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in PRESCRIPTION_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Invoice
INVOICE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "patient_id",
    "issued",
    "amount",
    "paid",
    "status",
    "due",
})
INVOICE_SORTABLE: Tuple[str, ...] = ('id', 'patient_id', 'issued', 'amount', 'paid', 'status', 'due',)
INVOICE_REQUIRED: Tuple[str, ...] = ('patient_id', 'issued', 'due',)


def validate_invoice_patient_id(value: Any) -> int:
    """Check Invoice.patient_id (ref)."""
    return check_ref("patient_id", value)


def validate_invoice_issued(value: Any) -> str:
    """Check Invoice.issued (date)."""
    return check_date("issued", value)


def validate_invoice_amount(value: Any) -> float:
    """Check Invoice.amount (money)."""
    return check_money("amount", value)


def validate_invoice_paid(value: Any) -> float:
    """Check Invoice.paid (money)."""
    return check_money("paid", value)


def validate_invoice_status(value: Any) -> InvoiceStatus:
    """Check Invoice.status (enum)."""
    return check_choice("status", value, InvoiceStatus)


def validate_invoice_due(value: Any) -> str:
    """Check Invoice.due (date)."""
    return check_date("due", value)


@dataclass
class Invoice:
    """A invoice record."""

    id: int = 0
    patient_id: int = 0
    issued: str = ""
    amount: float = 0.0
    paid: float = 0.0
    status: InvoiceStatus = InvoiceStatus.DRAFT
    due: str = ""

    def validate(self) -> "Invoice":
        """Check every field and normalise the values in place."""
        self.patient_id = validate_invoice_patient_id(self.patient_id)
        self.issued = validate_invoice_issued(self.issued)
        self.amount = validate_invoice_amount(self.amount)
        self.paid = validate_invoice_paid(self.paid)
        self.status = validate_invoice_status(self.status)
        self.due = validate_invoice_due(self.due)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "issued": self.issued,
            "amount": self.amount,
            "paid": self.paid,
            "status": self.status.value,
            "due": self.due,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Invoice":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, INVOICE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "patient_id" in data:
            item.patient_id = data["patient_id"]
        if "issued" in data:
            item.issued = data["issued"]
        if "amount" in data:
            item.amount = data["amount"]
        if "paid" in data:
            item.paid = data["paid"]
        if "status" in data:
            item.status = data["status"]
        if "due" in data:
            item.due = data["due"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Invoice":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, INVOICE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Invoice #{self.id}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in INVOICE_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- LabResult
LAB_RESULT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "patient_id",
    "test_name",
    "value",
    "unit",
    "taken",
    "flagged",
})
LAB_RESULT_SORTABLE: Tuple[str, ...] = ('id', 'patient_id', 'test_name', 'value', 'unit', 'taken',)
LAB_RESULT_REQUIRED: Tuple[str, ...] = ('patient_id', 'test_name', 'unit', 'taken',)


def validate_lab_result_patient_id(value: Any) -> int:
    """Check LabResult.patient_id (ref)."""
    return check_ref("patient_id", value)


def validate_lab_result_test_name(value: Any) -> str:
    """Check LabResult.test_name (str)."""
    return check_text("test_name", value)


def validate_lab_result_value(value: Any) -> float:
    """Check LabResult.value (float)."""
    return check_number("value", value)


def validate_lab_result_unit(value: Any) -> str:
    """Check LabResult.unit (str)."""
    return check_text("unit", value)


def validate_lab_result_taken(value: Any) -> str:
    """Check LabResult.taken (date)."""
    return check_date("taken", value)


def validate_lab_result_flagged(value: Any) -> bool:
    """Check LabResult.flagged (bool)."""
    return check_flag("flagged", value)


@dataclass
class LabResult:
    """A lab result record."""

    id: int = 0
    patient_id: int = 0
    test_name: str = ""
    value: float = 0.0
    unit: str = ""
    taken: str = ""
    flagged: bool = False

    def validate(self) -> "LabResult":
        """Check every field and normalise the values in place."""
        self.patient_id = validate_lab_result_patient_id(self.patient_id)
        self.test_name = validate_lab_result_test_name(self.test_name)
        self.value = validate_lab_result_value(self.value)
        self.unit = validate_lab_result_unit(self.unit)
        self.taken = validate_lab_result_taken(self.taken)
        self.flagged = validate_lab_result_flagged(self.flagged)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "test_name": self.test_name,
            "value": self.value,
            "unit": self.unit,
            "taken": self.taken,
            "flagged": self.flagged,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabResult":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, LAB_RESULT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "patient_id" in data:
            item.patient_id = data["patient_id"]
        if "test_name" in data:
            item.test_name = data["test_name"]
        if "value" in data:
            item.value = data["value"]
        if "unit" in data:
            item.unit = data["unit"]
        if "taken" in data:
            item.taken = data["taken"]
        if "flagged" in data:
            item.flagged = data["flagged"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "LabResult":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, LAB_RESULT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"LabResult #{self.id}: {self.test_name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in LAB_RESULT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Document
DOCUMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "title",
    "pages",
    "signed",
    "version",
    "issued",
})
DOCUMENT_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'title', 'pages', 'version', 'issued',)
DOCUMENT_REQUIRED: Tuple[str, ...] = ('doctor_id', 'title', 'issued',)


def validate_document_doctor_id(value: Any) -> int:
    """Check Document.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_document_title(value: Any) -> str:
    """Check Document.title (str)."""
    return check_text("title", value)


def validate_document_pages(value: Any) -> int:
    """Check Document.pages (int)."""
    return check_int("pages", value)


def validate_document_signed(value: Any) -> bool:
    """Check Document.signed (bool)."""
    return check_flag("signed", value)


def validate_document_version(value: Any) -> int:
    """Check Document.version (int)."""
    return check_int("version", value)


def validate_document_issued(value: Any) -> str:
    """Check Document.issued (date)."""
    return check_date("issued", value)


@dataclass
class Document:
    """A document record."""

    id: int = 0
    doctor_id: int = 0
    title: str = ""
    pages: int = 0
    signed: bool = False
    version: int = 0
    issued: str = ""

    def validate(self) -> "Document":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_document_doctor_id(self.doctor_id)
        self.title = validate_document_title(self.title)
        self.pages = validate_document_pages(self.pages)
        self.signed = validate_document_signed(self.signed)
        self.version = validate_document_version(self.version)
        self.issued = validate_document_issued(self.issued)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "title": self.title,
            "pages": self.pages,
            "signed": self.signed,
            "version": self.version,
            "issued": self.issued,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, DOCUMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "title" in data:
            item.title = data["title"]
        if "pages" in data:
            item.pages = data["pages"]
        if "signed" in data:
            item.signed = data["signed"]
        if "version" in data:
            item.version = data["version"]
        if "issued" in data:
            item.issued = data["issued"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Document":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, DOCUMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Document #{self.id}: {self.title}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in DOCUMENT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Notification
NOTIFICATION_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "recipient",
    "title",
    "sent",
    "channel",
    "read",
})
NOTIFICATION_SORTABLE: Tuple[str, ...] = ('id', 'recipient', 'title', 'sent', 'channel',)
NOTIFICATION_REQUIRED: Tuple[str, ...] = ('recipient', 'title', 'sent',)


def validate_notification_recipient(value: Any) -> str:
    """Check Notification.recipient (email)."""
    return check_email("recipient", value)


def validate_notification_title(value: Any) -> str:
    """Check Notification.title (str)."""
    return check_text("title", value)


def validate_notification_sent(value: Any) -> str:
    """Check Notification.sent (date)."""
    return check_date("sent", value)


def validate_notification_channel(value: Any) -> NotificationChannel:
    """Check Notification.channel (enum)."""
    return check_choice("channel", value, NotificationChannel)


def validate_notification_read(value: Any) -> bool:
    """Check Notification.read (bool)."""
    return check_flag("read", value)


@dataclass
class Notification:
    """A notification record."""

    id: int = 0
    recipient: str = ""
    title: str = ""
    sent: str = ""
    channel: NotificationChannel = NotificationChannel.EMAIL
    read: bool = False

    def validate(self) -> "Notification":
        """Check every field and normalise the values in place."""
        self.recipient = validate_notification_recipient(self.recipient)
        self.title = validate_notification_title(self.title)
        self.sent = validate_notification_sent(self.sent)
        self.channel = validate_notification_channel(self.channel)
        self.read = validate_notification_read(self.read)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "recipient": self.recipient,
            "title": self.title,
            "sent": self.sent,
            "channel": self.channel.value,
            "read": self.read,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, NOTIFICATION_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "recipient" in data:
            item.recipient = data["recipient"]
        if "title" in data:
            item.title = data["title"]
        if "sent" in data:
            item.sent = data["sent"]
        if "channel" in data:
            item.channel = data["channel"]
        if "read" in data:
            item.read = data["read"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Notification":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, NOTIFICATION_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Notification #{self.id}: {self.recipient}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in NOTIFICATION_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Address
ADDRESS_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "street",
    "city",
    "postcode",
    "country",
    "billing",
})
ADDRESS_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'street', 'city', 'postcode', 'country',)
ADDRESS_REQUIRED: Tuple[str, ...] = ('doctor_id', 'street', 'city', 'postcode', 'country',)


def validate_address_doctor_id(value: Any) -> int:
    """Check Address.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_address_street(value: Any) -> str:
    """Check Address.street (str)."""
    return check_text("street", value)


def validate_address_city(value: Any) -> str:
    """Check Address.city (str)."""
    return check_text("city", value)


def validate_address_postcode(value: Any) -> str:
    """Check Address.postcode (str)."""
    return check_text("postcode", value)


def validate_address_country(value: Any) -> str:
    """Check Address.country (str)."""
    return check_text("country", value)


def validate_address_billing(value: Any) -> bool:
    """Check Address.billing (bool)."""
    return check_flag("billing", value)


@dataclass
class Address:
    """A address record."""

    id: int = 0
    doctor_id: int = 0
    street: str = ""
    city: str = ""
    postcode: str = ""
    country: str = ""
    billing: bool = False

    def validate(self) -> "Address":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_address_doctor_id(self.doctor_id)
        self.street = validate_address_street(self.street)
        self.city = validate_address_city(self.city)
        self.postcode = validate_address_postcode(self.postcode)
        self.country = validate_address_country(self.country)
        self.billing = validate_address_billing(self.billing)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "street": self.street,
            "city": self.city,
            "postcode": self.postcode,
            "country": self.country,
            "billing": self.billing,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Address":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ADDRESS_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "street" in data:
            item.street = data["street"]
        if "city" in data:
            item.city = data["city"]
        if "postcode" in data:
            item.postcode = data["postcode"]
        if "country" in data:
            item.country = data["country"]
        if "billing" in data:
            item.billing = data["billing"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Address":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ADDRESS_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Address #{self.id}: {self.street}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in ADDRESS_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Reminder
REMINDER_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "title",
    "remind_on",
    "done",
    "priority",
})
REMINDER_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'title', 'remind_on', 'priority',)
REMINDER_REQUIRED: Tuple[str, ...] = ('doctor_id', 'title', 'remind_on',)


def validate_reminder_doctor_id(value: Any) -> int:
    """Check Reminder.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_reminder_title(value: Any) -> str:
    """Check Reminder.title (str)."""
    return check_text("title", value)


def validate_reminder_remind_on(value: Any) -> str:
    """Check Reminder.remind_on (date)."""
    return check_date("remind_on", value)


def validate_reminder_done(value: Any) -> bool:
    """Check Reminder.done (bool)."""
    return check_flag("done", value)


def validate_reminder_priority(value: Any) -> ReminderPriority:
    """Check Reminder.priority (enum)."""
    return check_choice("priority", value, ReminderPriority)


@dataclass
class Reminder:
    """A reminder record."""

    id: int = 0
    doctor_id: int = 0
    title: str = ""
    remind_on: str = ""
    done: bool = False
    priority: ReminderPriority = ReminderPriority.LOW

    def validate(self) -> "Reminder":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_reminder_doctor_id(self.doctor_id)
        self.title = validate_reminder_title(self.title)
        self.remind_on = validate_reminder_remind_on(self.remind_on)
        self.done = validate_reminder_done(self.done)
        self.priority = validate_reminder_priority(self.priority)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "title": self.title,
            "remind_on": self.remind_on,
            "done": self.done,
            "priority": self.priority.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reminder":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, REMINDER_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "title" in data:
            item.title = data["title"]
        if "remind_on" in data:
            item.remind_on = data["remind_on"]
        if "done" in data:
            item.done = data["done"]
        if "priority" in data:
            item.priority = data["priority"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Reminder":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, REMINDER_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Reminder #{self.id}: {self.title}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in REMINDER_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Setting
SETTING_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "key_name",
    "value",
    "editable",
    "changed",
})
SETTING_SORTABLE: Tuple[str, ...] = ('id', 'key_name', 'value', 'changed',)
SETTING_REQUIRED: Tuple[str, ...] = ('key_name', 'value', 'changed',)


def validate_setting_key_name(value: Any) -> str:
    """Check Setting.key_name (str)."""
    return check_text("key_name", value)


def validate_setting_value(value: Any) -> str:
    """Check Setting.value (str)."""
    return check_text("value", value)


def validate_setting_editable(value: Any) -> bool:
    """Check Setting.editable (bool)."""
    return check_flag("editable", value)


def validate_setting_changed(value: Any) -> str:
    """Check Setting.changed (date)."""
    return check_date("changed", value)


@dataclass
class Setting:
    """A setting record."""

    id: int = 0
    key_name: str = ""
    value: str = ""
    editable: bool = False
    changed: str = ""

    def validate(self) -> "Setting":
        """Check every field and normalise the values in place."""
        self.key_name = validate_setting_key_name(self.key_name)
        self.value = validate_setting_value(self.value)
        self.editable = validate_setting_editable(self.editable)
        self.changed = validate_setting_changed(self.changed)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "key_name": self.key_name,
            "value": self.value,
            "editable": self.editable,
            "changed": self.changed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Setting":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, SETTING_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "key_name" in data:
            item.key_name = data["key_name"]
        if "value" in data:
            item.value = data["value"]
        if "editable" in data:
            item.editable = data["editable"]
        if "changed" in data:
            item.changed = data["changed"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Setting":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, SETTING_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Setting #{self.id}: {self.key_name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in SETTING_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- AuditEntry
AUDIT_ENTRY_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "actor",
    "action",
    "at",
    "details",
})
AUDIT_ENTRY_SORTABLE: Tuple[str, ...] = ('id', 'actor', 'action', 'at',)
AUDIT_ENTRY_REQUIRED: Tuple[str, ...] = ('actor', 'at',)


def validate_audit_entry_actor(value: Any) -> str:
    """Check AuditEntry.actor (str)."""
    return check_text("actor", value)


def validate_audit_entry_action(value: Any) -> AuditEntryAction:
    """Check AuditEntry.action (enum)."""
    return check_choice("action", value, AuditEntryAction)


def validate_audit_entry_at(value: Any) -> str:
    """Check AuditEntry.at (date)."""
    return check_date("at", value)


def validate_audit_entry_details(value: Any) -> str:
    """Check AuditEntry.details (text)."""
    return check_text("details", value, max_length=2000, required=False)


@dataclass
class AuditEntry:
    """A audit entry record."""

    id: int = 0
    actor: str = ""
    action: AuditEntryAction = AuditEntryAction.CREATE
    at: str = ""
    details: str = ""

    def validate(self) -> "AuditEntry":
        """Check every field and normalise the values in place."""
        self.actor = validate_audit_entry_actor(self.actor)
        self.action = validate_audit_entry_action(self.action)
        self.at = validate_audit_entry_at(self.at)
        self.details = validate_audit_entry_details(self.details)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "actor": self.actor,
            "action": self.action.value,
            "at": self.at,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, AUDIT_ENTRY_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "actor" in data:
            item.actor = data["actor"]
        if "action" in data:
            item.action = data["action"]
        if "at" in data:
            item.at = data["at"]
        if "details" in data:
            item.details = data["details"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "AuditEntry":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, AUDIT_ENTRY_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"AuditEntry #{self.id}: {self.actor}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in AUDIT_ENTRY_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Note
NOTE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "subject",
    "body",
    "pinned",
    "written",
})
NOTE_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'subject', 'written',)
NOTE_REQUIRED: Tuple[str, ...] = ('doctor_id', 'subject', 'written',)


def validate_note_doctor_id(value: Any) -> int:
    """Check Note.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_note_subject(value: Any) -> str:
    """Check Note.subject (str)."""
    return check_text("subject", value)


def validate_note_body(value: Any) -> str:
    """Check Note.body (text)."""
    return check_text("body", value, max_length=2000, required=False)


def validate_note_pinned(value: Any) -> bool:
    """Check Note.pinned (bool)."""
    return check_flag("pinned", value)


def validate_note_written(value: Any) -> str:
    """Check Note.written (date)."""
    return check_date("written", value)


@dataclass
class Note:
    """A note record."""

    id: int = 0
    doctor_id: int = 0
    subject: str = ""
    body: str = ""
    pinned: bool = False
    written: str = ""

    def validate(self) -> "Note":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_note_doctor_id(self.doctor_id)
        self.subject = validate_note_subject(self.subject)
        self.body = validate_note_body(self.body)
        self.pinned = validate_note_pinned(self.pinned)
        self.written = validate_note_written(self.written)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "subject": self.subject,
            "body": self.body,
            "pinned": self.pinned,
            "written": self.written,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, NOTE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "subject" in data:
            item.subject = data["subject"]
        if "body" in data:
            item.body = data["body"]
        if "pinned" in data:
            item.pinned = data["pinned"]
        if "written" in data:
            item.written = data["written"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Note":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, NOTE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Note #{self.id}: {self.subject}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in NOTE_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Review
REVIEW_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "author",
    "stars",
    "comment",
    "verified",
    "posted",
})
REVIEW_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'author', 'stars', 'posted',)
REVIEW_REQUIRED: Tuple[str, ...] = ('doctor_id', 'author', 'posted',)


def validate_review_doctor_id(value: Any) -> int:
    """Check Review.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_review_author(value: Any) -> str:
    """Check Review.author (str)."""
    return check_text("author", value)


def validate_review_stars(value: Any) -> int:
    """Check Review.stars (int)."""
    return check_int("stars", value)


def validate_review_comment(value: Any) -> str:
    """Check Review.comment (text)."""
    return check_text("comment", value, max_length=2000, required=False)


def validate_review_verified(value: Any) -> bool:
    """Check Review.verified (bool)."""
    return check_flag("verified", value)


def validate_review_posted(value: Any) -> str:
    """Check Review.posted (date)."""
    return check_date("posted", value)


@dataclass
class Review:
    """A review record."""

    id: int = 0
    doctor_id: int = 0
    author: str = ""
    stars: int = 0
    comment: str = ""
    verified: bool = False
    posted: str = ""

    def validate(self) -> "Review":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_review_doctor_id(self.doctor_id)
        self.author = validate_review_author(self.author)
        self.stars = validate_review_stars(self.stars)
        self.comment = validate_review_comment(self.comment)
        self.verified = validate_review_verified(self.verified)
        self.posted = validate_review_posted(self.posted)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "author": self.author,
            "stars": self.stars,
            "comment": self.comment,
            "verified": self.verified,
            "posted": self.posted,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, REVIEW_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "author" in data:
            item.author = data["author"]
        if "stars" in data:
            item.stars = data["stars"]
        if "comment" in data:
            item.comment = data["comment"]
        if "verified" in data:
            item.verified = data["verified"]
        if "posted" in data:
            item.posted = data["posted"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Review":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, REVIEW_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Review #{self.id}: {self.author}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in REVIEW_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- ContactPerson
CONTACT_PERSON_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "name",
    "email",
    "phone",
    "role",
    "primary",
})
CONTACT_PERSON_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'name', 'email', 'phone', 'role',)
CONTACT_PERSON_REQUIRED: Tuple[str, ...] = ('doctor_id', 'name', 'email', 'phone', 'role',)


def validate_contact_person_doctor_id(value: Any) -> int:
    """Check ContactPerson.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_contact_person_name(value: Any) -> str:
    """Check ContactPerson.name (str)."""
    return check_text("name", value)


def validate_contact_person_email(value: Any) -> str:
    """Check ContactPerson.email (email)."""
    return check_email("email", value)


def validate_contact_person_phone(value: Any) -> str:
    """Check ContactPerson.phone (str)."""
    return check_text("phone", value)


def validate_contact_person_role(value: Any) -> str:
    """Check ContactPerson.role (str)."""
    return check_text("role", value)


def validate_contact_person_primary(value: Any) -> bool:
    """Check ContactPerson.primary (bool)."""
    return check_flag("primary", value)


@dataclass
class ContactPerson:
    """A contact person record."""

    id: int = 0
    doctor_id: int = 0
    name: str = ""
    email: str = ""
    phone: str = ""
    role: str = ""
    primary: bool = False

    def validate(self) -> "ContactPerson":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_contact_person_doctor_id(self.doctor_id)
        self.name = validate_contact_person_name(self.name)
        self.email = validate_contact_person_email(self.email)
        self.phone = validate_contact_person_phone(self.phone)
        self.role = validate_contact_person_role(self.role)
        self.primary = validate_contact_person_primary(self.primary)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "primary": self.primary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContactPerson":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, CONTACT_PERSON_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "phone" in data:
            item.phone = data["phone"]
        if "role" in data:
            item.role = data["role"]
        if "primary" in data:
            item.primary = data["primary"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "ContactPerson":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, CONTACT_PERSON_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"ContactPerson #{self.id}: {self.name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in CONTACT_PERSON_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Discount
DISCOUNT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "code",
    "percent",
    "starts",
    "ends",
    "active",
})
DISCOUNT_SORTABLE: Tuple[str, ...] = ('id', 'code', 'percent', 'starts', 'ends',)
DISCOUNT_REQUIRED: Tuple[str, ...] = ('code', 'starts', 'ends',)


def validate_discount_code(value: Any) -> str:
    """Check Discount.code (str)."""
    return check_text("code", value)


def validate_discount_percent(value: Any) -> float:
    """Check Discount.percent (float)."""
    return check_number("percent", value)


def validate_discount_starts(value: Any) -> str:
    """Check Discount.starts (date)."""
    return check_date("starts", value)


def validate_discount_ends(value: Any) -> str:
    """Check Discount.ends (date)."""
    return check_date("ends", value)


def validate_discount_active(value: Any) -> bool:
    """Check Discount.active (bool)."""
    return check_flag("active", value)


@dataclass
class Discount:
    """A discount record."""

    id: int = 0
    code: str = ""
    percent: float = 0.0
    starts: str = ""
    ends: str = ""
    active: bool = False

    def validate(self) -> "Discount":
        """Check every field and normalise the values in place."""
        self.code = validate_discount_code(self.code)
        self.percent = validate_discount_percent(self.percent)
        self.starts = validate_discount_starts(self.starts)
        self.ends = validate_discount_ends(self.ends)
        self.active = validate_discount_active(self.active)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "code": self.code,
            "percent": self.percent,
            "starts": self.starts,
            "ends": self.ends,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Discount":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, DISCOUNT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "code" in data:
            item.code = data["code"]
        if "percent" in data:
            item.percent = data["percent"]
        if "starts" in data:
            item.starts = data["starts"]
        if "ends" in data:
            item.ends = data["ends"]
        if "active" in data:
            item.active = data["active"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Discount":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, DISCOUNT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Discount #{self.id}: {self.code}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in DISCOUNT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Tag
TAG_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "doctor_id",
    "label",
    "color",
    "usage",
})
TAG_SORTABLE: Tuple[str, ...] = ('id', 'doctor_id', 'label', 'color', 'usage',)
TAG_REQUIRED: Tuple[str, ...] = ('doctor_id', 'label', 'color',)


def validate_tag_doctor_id(value: Any) -> int:
    """Check Tag.doctor_id (ref)."""
    return check_ref("doctor_id", value)


def validate_tag_label(value: Any) -> str:
    """Check Tag.label (str)."""
    return check_text("label", value)


def validate_tag_color(value: Any) -> str:
    """Check Tag.color (str)."""
    return check_text("color", value)


def validate_tag_usage(value: Any) -> int:
    """Check Tag.usage (int)."""
    return check_int("usage", value)


@dataclass
class Tag:
    """A tag record."""

    id: int = 0
    doctor_id: int = 0
    label: str = ""
    color: str = ""
    usage: int = 0

    def validate(self) -> "Tag":
        """Check every field and normalise the values in place."""
        self.doctor_id = validate_tag_doctor_id(self.doctor_id)
        self.label = validate_tag_label(self.label)
        self.color = validate_tag_color(self.color)
        self.usage = validate_tag_usage(self.usage)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "label": self.label,
            "color": self.color,
            "usage": self.usage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, TAG_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "doctor_id" in data:
            item.doctor_id = data["doctor_id"]
        if "label" in data:
            item.label = data["label"]
        if "color" in data:
            item.color = data["color"]
        if "usage" in data:
            item.usage = data["usage"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Tag":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, TAG_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Tag #{self.id}: {self.label}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in TAG_REQUIRED if not getattr(self, name))
