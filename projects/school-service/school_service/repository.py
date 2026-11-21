"""Storage for the School Records service: one thread-safe in-memory repository per
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
    Assignment,
    Attendance,
    AuditEntry,
    AuditEntryAction,
    ContactPerson,
    Course,
    CourseTerm,
    Discount,
    Document,
    Enrollment,
    EnrollmentStatus,
    Note,
    Notification,
    NotificationChannel,
    Reminder,
    ReminderPriority,
    Review,
    Setting,
    Student,
    Tag,
    Teacher,
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


class TeacherRepository(Repository[Teacher]):
    """All teachers, with the lookups the services need."""

    model = Teacher
    entity_name = "teacher"

    def find_by_name(self, value: str) -> List[Teacher]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Teacher]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Teacher]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Teacher]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def find_by_subject(self, value: str) -> List[Teacher]:
        """Records whose subject is exactly `value`."""
        return self.where(lambda item: item.subject == value)

    def search_subject(self, text: str) -> List[Teacher]:
        """Records whose subject contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.subject.lower())

    def hired_before(self, day: str) -> List[Teacher]:
        return self.where(lambda item: item.hired < day)

    def hired_after(self, day: str) -> List[Teacher]:
        return self.where(lambda item: item.hired > day)

    def hired_on(self, day: str) -> List[Teacher]:
        return self.where(lambda item: item.hired == day)

    def between_salary(self, low: float, high: float) -> List[Teacher]:
        """Records whose salary is within [low, high]."""
        return self.where(lambda item: low <= item.salary <= high)

    def total_salary(self) -> float:
        return sum(item.salary for item in self.list())

    def average_salary(self) -> float:
        items = self.list()
        return sum(item.salary for item in items) / len(items) if items else 0.0

    def max_salary(self) -> Optional[Teacher]:
        """The record with the highest salary."""
        items = self.list()
        return max(items, key=lambda item: item.salary) if items else None

    def where_full_time(self, flag: bool = True) -> List[Teacher]:
        return self.where(lambda item: item.full_time is flag)

    def search(self, text: str) -> List[Teacher]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.subject,
        )))


class StudentRepository(Repository[Student]):
    """All students, with the lookups the services need."""

    model = Student
    entity_name = "student"

    def find_by_name(self, value: str) -> List[Student]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Student]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Student]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Student]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def birth_date_before(self, day: str) -> List[Student]:
        return self.where(lambda item: item.birth_date < day)

    def birth_date_after(self, day: str) -> List[Student]:
        return self.where(lambda item: item.birth_date > day)

    def birth_date_on(self, day: str) -> List[Student]:
        return self.where(lambda item: item.birth_date == day)

    def between_grade_level(self, low: float, high: float) -> List[Student]:
        """Records whose grade level is within [low, high]."""
        return self.where(lambda item: low <= item.grade_level <= high)

    def total_grade_level(self) -> float:
        return sum(item.grade_level for item in self.list())

    def average_grade_level(self) -> float:
        items = self.list()
        return sum(item.grade_level for item in items) / len(items) if items else 0.0

    def max_grade_level(self) -> Optional[Student]:
        """The record with the highest grade level."""
        items = self.list()
        return max(items, key=lambda item: item.grade_level) if items else None

    def find_by_guardian(self, value: str) -> List[Student]:
        """Records whose guardian is exactly `value`."""
        return self.where(lambda item: item.guardian == value)

    def search_guardian(self, text: str) -> List[Student]:
        """Records whose guardian contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.guardian.lower())

    def where_active(self, flag: bool = True) -> List[Student]:
        return self.where(lambda item: item.active is flag)

    def search(self, text: str) -> List[Student]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.guardian,
        )))


class CourseRepository(Repository[Course]):
    """All courses, with the lookups the services need."""

    model = Course
    entity_name = "course"

    def for_teacher(self, teacher_id: int) -> List[Course]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

    def find_by_title(self, value: str) -> List[Course]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Course]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def find_by_code(self, value: str) -> List[Course]:
        """Records whose code is exactly `value`."""
        return self.where(lambda item: item.code == value)

    def search_code(self, text: str) -> List[Course]:
        """Records whose code contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.code.lower())

    def between_credits(self, low: float, high: float) -> List[Course]:
        """Records whose credits is within [low, high]."""
        return self.where(lambda item: low <= item.credits <= high)

    def total_credits(self) -> float:
        return sum(item.credits for item in self.list())

    def average_credits(self) -> float:
        items = self.list()
        return sum(item.credits for item in items) / len(items) if items else 0.0

    def max_credits(self) -> Optional[Course]:
        """The record with the highest credits."""
        items = self.list()
        return max(items, key=lambda item: item.credits) if items else None

    def find_by_room(self, value: str) -> List[Course]:
        """Records whose room is exactly `value`."""
        return self.where(lambda item: item.room == value)

    def search_room(self, text: str) -> List[Course]:
        """Records whose room contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.room.lower())

    def with_term(self, value: Any) -> List[Course]:
        wanted = CourseTerm(value)
        return self.where(lambda item: item.term == wanted)

    def count_by_term(self) -> Dict[str, int]:
        """How many records have each term."""
        counts = {member.value: 0 for member in CourseTerm}
        for item in self.list():
            counts[CourseTerm(item.term).value] += 1
        return counts

    def search(self, text: str) -> List[Course]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.title,
            item.code,
            item.room,
        )))


class EnrollmentRepository(Repository[Enrollment]):
    """All enrollments, with the lookups the services need."""

    model = Enrollment
    entity_name = "enrollment"

    def for_course(self, course_id: int) -> List[Enrollment]:
        """Records linked to course `course_id`."""
        return self.where(lambda item: item.course_id == course_id)

    def count_for_course(self, course_id: int) -> int:
        return len(self.for_course(course_id))

    def for_student(self, student_id: int) -> List[Enrollment]:
        """Records linked to student `student_id`."""
        return self.where(lambda item: item.student_id == student_id)

    def count_for_student(self, student_id: int) -> int:
        return len(self.for_student(student_id))

    def enrolled_before(self, day: str) -> List[Enrollment]:
        return self.where(lambda item: item.enrolled < day)

    def enrolled_after(self, day: str) -> List[Enrollment]:
        return self.where(lambda item: item.enrolled > day)

    def enrolled_on(self, day: str) -> List[Enrollment]:
        return self.where(lambda item: item.enrolled == day)

    def with_status(self, value: Any) -> List[Enrollment]:
        wanted = EnrollmentStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in EnrollmentStatus}
        for item in self.list():
            counts[EnrollmentStatus(item.status).value] += 1
        return counts

    def between_final_score(self, low: float, high: float) -> List[Enrollment]:
        """Records whose final score is within [low, high]."""
        return self.where(lambda item: low <= item.final_score <= high)

    def total_final_score(self) -> float:
        return sum(item.final_score for item in self.list())

    def average_final_score(self) -> float:
        items = self.list()
        return sum(item.final_score for item in items) / len(items) if items else 0.0

    def max_final_score(self) -> Optional[Enrollment]:
        """The record with the highest final score."""
        items = self.list()
        return max(items, key=lambda item: item.final_score) if items else None

    def search(self, text: str) -> List[Enrollment]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: needle == str(item.id))


class AssignmentRepository(Repository[Assignment]):
    """All assignments, with the lookups the services need."""

    model = Assignment
    entity_name = "assignment"

    def for_course(self, course_id: int) -> List[Assignment]:
        """Records linked to course `course_id`."""
        return self.where(lambda item: item.course_id == course_id)

    def count_for_course(self, course_id: int) -> int:
        return len(self.for_course(course_id))

    def find_by_title(self, value: str) -> List[Assignment]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Assignment]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def due_before(self, day: str) -> List[Assignment]:
        return self.where(lambda item: item.due < day)

    def due_after(self, day: str) -> List[Assignment]:
        return self.where(lambda item: item.due > day)

    def due_on(self, day: str) -> List[Assignment]:
        return self.where(lambda item: item.due == day)

    def between_max_points(self, low: float, high: float) -> List[Assignment]:
        """Records whose max points is within [low, high]."""
        return self.where(lambda item: low <= item.max_points <= high)

    def total_max_points(self) -> float:
        return sum(item.max_points for item in self.list())

    def average_max_points(self) -> float:
        items = self.list()
        return sum(item.max_points for item in items) / len(items) if items else 0.0

    def max_max_points(self) -> Optional[Assignment]:
        """The record with the highest max points."""
        items = self.list()
        return max(items, key=lambda item: item.max_points) if items else None

    def between_weight(self, low: float, high: float) -> List[Assignment]:
        """Records whose weight is within [low, high]."""
        return self.where(lambda item: low <= item.weight <= high)

    def total_weight(self) -> float:
        return sum(item.weight for item in self.list())

    def average_weight(self) -> float:
        items = self.list()
        return sum(item.weight for item in items) / len(items) if items else 0.0

    def max_weight(self) -> Optional[Assignment]:
        """The record with the highest weight."""
        items = self.list()
        return max(items, key=lambda item: item.weight) if items else None

    def where_published(self, flag: bool = True) -> List[Assignment]:
        return self.where(lambda item: item.published is flag)

    def search(self, text: str) -> List[Assignment]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.title,
        )))


class AttendanceRepository(Repository[Attendance]):
    """All attendances, with the lookups the services need."""

    model = Attendance
    entity_name = "attendance"

    def for_student(self, student_id: int) -> List[Attendance]:
        """Records linked to student `student_id`."""
        return self.where(lambda item: item.student_id == student_id)

    def count_for_student(self, student_id: int) -> int:
        return len(self.for_student(student_id))

    def for_course(self, course_id: int) -> List[Attendance]:
        """Records linked to course `course_id`."""
        return self.where(lambda item: item.course_id == course_id)

    def count_for_course(self, course_id: int) -> int:
        return len(self.for_course(course_id))

    def day_before(self, day: str) -> List[Attendance]:
        return self.where(lambda item: item.day < day)

    def day_after(self, day: str) -> List[Attendance]:
        return self.where(lambda item: item.day > day)

    def day_on(self, day: str) -> List[Attendance]:
        return self.where(lambda item: item.day == day)

    def where_present(self, flag: bool = True) -> List[Attendance]:
        return self.where(lambda item: item.present is flag)

    def between_minutes_late(self, low: float, high: float) -> List[Attendance]:
        """Records whose minutes late is within [low, high]."""
        return self.where(lambda item: low <= item.minutes_late <= high)

    def total_minutes_late(self) -> float:
        return sum(item.minutes_late for item in self.list())

    def average_minutes_late(self) -> float:
        items = self.list()
        return sum(item.minutes_late for item in items) / len(items) if items else 0.0

    def max_minutes_late(self) -> Optional[Attendance]:
        """The record with the highest minutes late."""
        items = self.list()
        return max(items, key=lambda item: item.minutes_late) if items else None

    def find_by_note(self, value: str) -> List[Attendance]:
        """Records whose note is exactly `value`."""
        return self.where(lambda item: item.note == value)

    def search_note(self, text: str) -> List[Attendance]:
        """Records whose note contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.note.lower())

    def search(self, text: str) -> List[Attendance]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.note,
        )))


class DocumentRepository(Repository[Document]):
    """All documents, with the lookups the services need."""

    model = Document
    entity_name = "document"

    def for_teacher(self, teacher_id: int) -> List[Document]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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

    def for_teacher(self, teacher_id: int) -> List[Address]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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

    def for_teacher(self, teacher_id: int) -> List[Reminder]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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

    def for_teacher(self, teacher_id: int) -> List[Note]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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

    def for_teacher(self, teacher_id: int) -> List[Review]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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

    def for_teacher(self, teacher_id: int) -> List[ContactPerson]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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

    def for_teacher(self, teacher_id: int) -> List[Tag]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

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
