"""Domain models for the School Records service.

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


class CourseTerm(str, Enum):
    """Allowed values of Course.term."""

    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"

    @property
    def label(self) -> str:
        """Human-friendly name, e.g. for a drop-down."""
        return self.value.replace("_", " ").capitalize()

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)


class EnrollmentStatus(str, Enum):
    """Allowed values of Enrollment.status."""

    ACTIVE = "active"
    DROPPED = "dropped"
    COMPLETED = "completed"

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


# -------------------------------------------------------------------------- Teacher
TEACHER_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "subject",
    "hired",
    "salary",
    "full_time",
})
TEACHER_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'subject', 'hired', 'salary',)
TEACHER_REQUIRED: Tuple[str, ...] = ('name', 'email', 'subject', 'hired',)


def validate_teacher_name(value: Any) -> str:
    """Check Teacher.name (str)."""
    return check_text("name", value)


def validate_teacher_email(value: Any) -> str:
    """Check Teacher.email (email)."""
    return check_email("email", value)


def validate_teacher_subject(value: Any) -> str:
    """Check Teacher.subject (str)."""
    return check_text("subject", value)


def validate_teacher_hired(value: Any) -> str:
    """Check Teacher.hired (date)."""
    return check_date("hired", value)


def validate_teacher_salary(value: Any) -> float:
    """Check Teacher.salary (money)."""
    return check_money("salary", value)


def validate_teacher_full_time(value: Any) -> bool:
    """Check Teacher.full_time (bool)."""
    return check_flag("full_time", value)


@dataclass
class Teacher:
    """A teacher record."""

    id: int = 0
    name: str = ""
    email: str = ""
    subject: str = ""
    hired: str = ""
    salary: float = 0.0
    full_time: bool = False

    def validate(self) -> "Teacher":
        """Check every field and normalise the values in place."""
        self.name = validate_teacher_name(self.name)
        self.email = validate_teacher_email(self.email)
        self.subject = validate_teacher_subject(self.subject)
        self.hired = validate_teacher_hired(self.hired)
        self.salary = validate_teacher_salary(self.salary)
        self.full_time = validate_teacher_full_time(self.full_time)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "hired": self.hired,
            "salary": self.salary,
            "full_time": self.full_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Teacher":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, TEACHER_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "subject" in data:
            item.subject = data["subject"]
        if "hired" in data:
            item.hired = data["hired"]
        if "salary" in data:
            item.salary = data["salary"]
        if "full_time" in data:
            item.full_time = data["full_time"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Teacher":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, TEACHER_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Teacher #{self.id}: {self.name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in TEACHER_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Student
STUDENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "name",
    "email",
    "birth_date",
    "grade_level",
    "guardian",
    "active",
})
STUDENT_SORTABLE: Tuple[str, ...] = ('id', 'name', 'email', 'birth_date', 'grade_level', 'guardian',)
STUDENT_REQUIRED: Tuple[str, ...] = ('name', 'email', 'birth_date', 'guardian',)


def validate_student_name(value: Any) -> str:
    """Check Student.name (str)."""
    return check_text("name", value)


def validate_student_email(value: Any) -> str:
    """Check Student.email (email)."""
    return check_email("email", value)


def validate_student_birth_date(value: Any) -> str:
    """Check Student.birth_date (date)."""
    return check_date("birth_date", value)


def validate_student_grade_level(value: Any) -> int:
    """Check Student.grade_level (int)."""
    return check_int("grade_level", value)


def validate_student_guardian(value: Any) -> str:
    """Check Student.guardian (str)."""
    return check_text("guardian", value)


def validate_student_active(value: Any) -> bool:
    """Check Student.active (bool)."""
    return check_flag("active", value)


@dataclass
class Student:
    """A student record."""

    id: int = 0
    name: str = ""
    email: str = ""
    birth_date: str = ""
    grade_level: int = 0
    guardian: str = ""
    active: bool = False

    def validate(self) -> "Student":
        """Check every field and normalise the values in place."""
        self.name = validate_student_name(self.name)
        self.email = validate_student_email(self.email)
        self.birth_date = validate_student_birth_date(self.birth_date)
        self.grade_level = validate_student_grade_level(self.grade_level)
        self.guardian = validate_student_guardian(self.guardian)
        self.active = validate_student_active(self.active)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "birth_date": self.birth_date,
            "grade_level": self.grade_level,
            "guardian": self.guardian,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, STUDENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "birth_date" in data:
            item.birth_date = data["birth_date"]
        if "grade_level" in data:
            item.grade_level = data["grade_level"]
        if "guardian" in data:
            item.guardian = data["guardian"]
        if "active" in data:
            item.active = data["active"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Student":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, STUDENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Student #{self.id}: {self.name}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in STUDENT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Course
COURSE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "teacher_id",
    "title",
    "code",
    "credits",
    "room",
    "term",
})
COURSE_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'title', 'code', 'credits', 'room', 'term',)
COURSE_REQUIRED: Tuple[str, ...] = ('teacher_id', 'title', 'code', 'room',)


def validate_course_teacher_id(value: Any) -> int:
    """Check Course.teacher_id (ref)."""
    return check_ref("teacher_id", value)


def validate_course_title(value: Any) -> str:
    """Check Course.title (str)."""
    return check_text("title", value)


def validate_course_code(value: Any) -> str:
    """Check Course.code (str)."""
    return check_text("code", value)


def validate_course_credits(value: Any) -> int:
    """Check Course.credits (int)."""
    return check_int("credits", value)


def validate_course_room(value: Any) -> str:
    """Check Course.room (str)."""
    return check_text("room", value)


def validate_course_term(value: Any) -> CourseTerm:
    """Check Course.term (enum)."""
    return check_choice("term", value, CourseTerm)


@dataclass
class Course:
    """A course record."""

    id: int = 0
    teacher_id: int = 0
    title: str = ""
    code: str = ""
    credits: int = 0
    room: str = ""
    term: CourseTerm = CourseTerm.FALL

    def validate(self) -> "Course":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_course_teacher_id(self.teacher_id)
        self.title = validate_course_title(self.title)
        self.code = validate_course_code(self.code)
        self.credits = validate_course_credits(self.credits)
        self.room = validate_course_room(self.room)
        self.term = validate_course_term(self.term)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "title": self.title,
            "code": self.code,
            "credits": self.credits,
            "room": self.room,
            "term": self.term.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, COURSE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
        if "title" in data:
            item.title = data["title"]
        if "code" in data:
            item.code = data["code"]
        if "credits" in data:
            item.credits = data["credits"]
        if "room" in data:
            item.room = data["room"]
        if "term" in data:
            item.term = data["term"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Course":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, COURSE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Course #{self.id}: {self.title}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in COURSE_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Enrollment
ENROLLMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "course_id",
    "student_id",
    "enrolled",
    "status",
    "final_score",
})
ENROLLMENT_SORTABLE: Tuple[str, ...] = ('id', 'course_id', 'student_id', 'enrolled', 'status', 'final_score',)
ENROLLMENT_REQUIRED: Tuple[str, ...] = ('course_id', 'student_id', 'enrolled',)


def validate_enrollment_course_id(value: Any) -> int:
    """Check Enrollment.course_id (ref)."""
    return check_ref("course_id", value)


def validate_enrollment_student_id(value: Any) -> int:
    """Check Enrollment.student_id (ref)."""
    return check_ref("student_id", value)


def validate_enrollment_enrolled(value: Any) -> str:
    """Check Enrollment.enrolled (date)."""
    return check_date("enrolled", value)


def validate_enrollment_status(value: Any) -> EnrollmentStatus:
    """Check Enrollment.status (enum)."""
    return check_choice("status", value, EnrollmentStatus)


def validate_enrollment_final_score(value: Any) -> float:
    """Check Enrollment.final_score (float)."""
    return check_number("final_score", value)


@dataclass
class Enrollment:
    """A enrollment record."""

    id: int = 0
    course_id: int = 0
    student_id: int = 0
    enrolled: str = ""
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    final_score: float = 0.0

    def validate(self) -> "Enrollment":
        """Check every field and normalise the values in place."""
        self.course_id = validate_enrollment_course_id(self.course_id)
        self.student_id = validate_enrollment_student_id(self.student_id)
        self.enrolled = validate_enrollment_enrolled(self.enrolled)
        self.status = validate_enrollment_status(self.status)
        self.final_score = validate_enrollment_final_score(self.final_score)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "student_id": self.student_id,
            "enrolled": self.enrolled,
            "status": self.status.value,
            "final_score": self.final_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Enrollment":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ENROLLMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "course_id" in data:
            item.course_id = data["course_id"]
        if "student_id" in data:
            item.student_id = data["student_id"]
        if "enrolled" in data:
            item.enrolled = data["enrolled"]
        if "status" in data:
            item.status = data["status"]
        if "final_score" in data:
            item.final_score = data["final_score"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Enrollment":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ENROLLMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Enrollment #{self.id}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in ENROLLMENT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Assignment
ASSIGNMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "course_id",
    "title",
    "due",
    "max_points",
    "weight",
    "published",
})
ASSIGNMENT_SORTABLE: Tuple[str, ...] = ('id', 'course_id', 'title', 'due', 'max_points', 'weight',)
ASSIGNMENT_REQUIRED: Tuple[str, ...] = ('course_id', 'title', 'due',)


def validate_assignment_course_id(value: Any) -> int:
    """Check Assignment.course_id (ref)."""
    return check_ref("course_id", value)


def validate_assignment_title(value: Any) -> str:
    """Check Assignment.title (str)."""
    return check_text("title", value)


def validate_assignment_due(value: Any) -> str:
    """Check Assignment.due (date)."""
    return check_date("due", value)


def validate_assignment_max_points(value: Any) -> int:
    """Check Assignment.max_points (int)."""
    return check_int("max_points", value)


def validate_assignment_weight(value: Any) -> float:
    """Check Assignment.weight (float)."""
    return check_number("weight", value)


def validate_assignment_published(value: Any) -> bool:
    """Check Assignment.published (bool)."""
    return check_flag("published", value)


@dataclass
class Assignment:
    """A assignment record."""

    id: int = 0
    course_id: int = 0
    title: str = ""
    due: str = ""
    max_points: int = 0
    weight: float = 0.0
    published: bool = False

    def validate(self) -> "Assignment":
        """Check every field and normalise the values in place."""
        self.course_id = validate_assignment_course_id(self.course_id)
        self.title = validate_assignment_title(self.title)
        self.due = validate_assignment_due(self.due)
        self.max_points = validate_assignment_max_points(self.max_points)
        self.weight = validate_assignment_weight(self.weight)
        self.published = validate_assignment_published(self.published)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "due": self.due,
            "max_points": self.max_points,
            "weight": self.weight,
            "published": self.published,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignment":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ASSIGNMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "course_id" in data:
            item.course_id = data["course_id"]
        if "title" in data:
            item.title = data["title"]
        if "due" in data:
            item.due = data["due"]
        if "max_points" in data:
            item.max_points = data["max_points"]
        if "weight" in data:
            item.weight = data["weight"]
        if "published" in data:
            item.published = data["published"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Assignment":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ASSIGNMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Assignment #{self.id}: {self.title}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in ASSIGNMENT_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Attendance
ATTENDANCE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "student_id",
    "course_id",
    "day",
    "present",
    "minutes_late",
    "note",
})
ATTENDANCE_SORTABLE: Tuple[str, ...] = ('id', 'student_id', 'course_id', 'day', 'minutes_late',)
ATTENDANCE_REQUIRED: Tuple[str, ...] = ('student_id', 'course_id', 'day',)


def validate_attendance_student_id(value: Any) -> int:
    """Check Attendance.student_id (ref)."""
    return check_ref("student_id", value)


def validate_attendance_course_id(value: Any) -> int:
    """Check Attendance.course_id (ref)."""
    return check_ref("course_id", value)


def validate_attendance_day(value: Any) -> str:
    """Check Attendance.day (date)."""
    return check_date("day", value)


def validate_attendance_present(value: Any) -> bool:
    """Check Attendance.present (bool)."""
    return check_flag("present", value)


def validate_attendance_minutes_late(value: Any) -> int:
    """Check Attendance.minutes_late (int)."""
    return check_int("minutes_late", value)


def validate_attendance_note(value: Any) -> str:
    """Check Attendance.note (text)."""
    return check_text("note", value, max_length=2000, required=False)


@dataclass
class Attendance:
    """A attendance record."""

    id: int = 0
    student_id: int = 0
    course_id: int = 0
    day: str = ""
    present: bool = False
    minutes_late: int = 0
    note: str = ""

    def validate(self) -> "Attendance":
        """Check every field and normalise the values in place."""
        self.student_id = validate_attendance_student_id(self.student_id)
        self.course_id = validate_attendance_course_id(self.course_id)
        self.day = validate_attendance_day(self.day)
        self.present = validate_attendance_present(self.present)
        self.minutes_late = validate_attendance_minutes_late(self.minutes_late)
        self.note = validate_attendance_note(self.note)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "day": self.day,
            "present": self.present,
            "minutes_late": self.minutes_late,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attendance":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ATTENDANCE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "student_id" in data:
            item.student_id = data["student_id"]
        if "course_id" in data:
            item.course_id = data["course_id"]
        if "day" in data:
            item.day = data["day"]
        if "present" in data:
            item.present = data["present"]
        if "minutes_late" in data:
            item.minutes_late = data["minutes_late"]
        if "note" in data:
            item.note = data["note"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Attendance":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ATTENDANCE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Attendance #{self.id}"

    def missing(self) -> Tuple[str, ...]:
        """Required fields that are still empty."""
        return tuple(name for name in ATTENDANCE_REQUIRED if not getattr(self, name))


# -------------------------------------------------------------------------- Document
DOCUMENT_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "teacher_id",
    "title",
    "pages",
    "signed",
    "version",
    "issued",
})
DOCUMENT_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'title', 'pages', 'version', 'issued',)
DOCUMENT_REQUIRED: Tuple[str, ...] = ('teacher_id', 'title', 'issued',)


def validate_document_teacher_id(value: Any) -> int:
    """Check Document.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    title: str = ""
    pages: int = 0
    signed: bool = False
    version: int = 0
    issued: str = ""

    def validate(self) -> "Document":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_document_teacher_id(self.teacher_id)
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
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
    "teacher_id",
    "street",
    "city",
    "postcode",
    "country",
    "billing",
})
ADDRESS_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'street', 'city', 'postcode', 'country',)
ADDRESS_REQUIRED: Tuple[str, ...] = ('teacher_id', 'street', 'city', 'postcode', 'country',)


def validate_address_teacher_id(value: Any) -> int:
    """Check Address.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    street: str = ""
    city: str = ""
    postcode: str = ""
    country: str = ""
    billing: bool = False

    def validate(self) -> "Address":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_address_teacher_id(self.teacher_id)
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
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
    "teacher_id",
    "title",
    "remind_on",
    "done",
    "priority",
})
REMINDER_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'title', 'remind_on', 'priority',)
REMINDER_REQUIRED: Tuple[str, ...] = ('teacher_id', 'title', 'remind_on',)


def validate_reminder_teacher_id(value: Any) -> int:
    """Check Reminder.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    title: str = ""
    remind_on: str = ""
    done: bool = False
    priority: ReminderPriority = ReminderPriority.LOW

    def validate(self) -> "Reminder":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_reminder_teacher_id(self.teacher_id)
        self.title = validate_reminder_title(self.title)
        self.remind_on = validate_reminder_remind_on(self.remind_on)
        self.done = validate_reminder_done(self.done)
        self.priority = validate_reminder_priority(self.priority)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
    "teacher_id",
    "subject",
    "body",
    "pinned",
    "written",
})
NOTE_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'subject', 'written',)
NOTE_REQUIRED: Tuple[str, ...] = ('teacher_id', 'subject', 'written',)


def validate_note_teacher_id(value: Any) -> int:
    """Check Note.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    subject: str = ""
    body: str = ""
    pinned: bool = False
    written: str = ""

    def validate(self) -> "Note":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_note_teacher_id(self.teacher_id)
        self.subject = validate_note_subject(self.subject)
        self.body = validate_note_body(self.body)
        self.pinned = validate_note_pinned(self.pinned)
        self.written = validate_note_written(self.written)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
    "teacher_id",
    "author",
    "stars",
    "comment",
    "verified",
    "posted",
})
REVIEW_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'author', 'stars', 'posted',)
REVIEW_REQUIRED: Tuple[str, ...] = ('teacher_id', 'author', 'posted',)


def validate_review_teacher_id(value: Any) -> int:
    """Check Review.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    author: str = ""
    stars: int = 0
    comment: str = ""
    verified: bool = False
    posted: str = ""

    def validate(self) -> "Review":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_review_teacher_id(self.teacher_id)
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
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
    "teacher_id",
    "name",
    "email",
    "phone",
    "role",
    "primary",
})
CONTACT_PERSON_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'name', 'email', 'phone', 'role',)
CONTACT_PERSON_REQUIRED: Tuple[str, ...] = ('teacher_id', 'name', 'email', 'phone', 'role',)


def validate_contact_person_teacher_id(value: Any) -> int:
    """Check ContactPerson.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    name: str = ""
    email: str = ""
    phone: str = ""
    role: str = ""
    primary: bool = False

    def validate(self) -> "ContactPerson":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_contact_person_teacher_id(self.teacher_id)
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
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
    "teacher_id",
    "label",
    "color",
    "usage",
})
TAG_SORTABLE: Tuple[str, ...] = ('id', 'teacher_id', 'label', 'color', 'usage',)
TAG_REQUIRED: Tuple[str, ...] = ('teacher_id', 'label', 'color',)


def validate_tag_teacher_id(value: Any) -> int:
    """Check Tag.teacher_id (ref)."""
    return check_ref("teacher_id", value)


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
    teacher_id: int = 0
    label: str = ""
    color: str = ""
    usage: int = 0

    def validate(self) -> "Tag":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_tag_teacher_id(self.teacher_id)
        self.label = validate_tag_label(self.label)
        self.color = validate_tag_color(self.color)
        self.usage = validate_tag_usage(self.usage)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
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
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
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
