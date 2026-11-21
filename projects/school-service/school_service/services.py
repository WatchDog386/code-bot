"""Business rules for the School Records service: validation, links between records
(a record can't point at something that doesn't exist, and can't be deleted while
others still point at it), small domain operations and statistics.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from .models import (
    ADDRESS_FIELDS,
    ASSIGNMENT_FIELDS,
    ATTENDANCE_FIELDS,
    AUDIT_ENTRY_FIELDS,
    Address,
    Assignment,
    Attendance,
    AuditEntry,
    CONTACT_PERSON_FIELDS,
    COURSE_FIELDS,
    ContactPerson,
    Course,
    DISCOUNT_FIELDS,
    DOCUMENT_FIELDS,
    Discount,
    Document,
    ENROLLMENT_FIELDS,
    Enrollment,
    NOTE_FIELDS,
    NOTIFICATION_FIELDS,
    Note,
    Notification,
    REMINDER_FIELDS,
    REVIEW_FIELDS,
    Reminder,
    Review,
    SETTING_FIELDS,
    STUDENT_FIELDS,
    Setting,
    Student,
    TAG_FIELDS,
    TEACHER_FIELDS,
    Tag,
    Teacher,
    ValidationError,
)
from .repository import (
    TeacherRepository,
    StudentRepository,
    CourseRepository,
    EnrollmentRepository,
    AssignmentRepository,
    AttendanceRepository,
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
        self.teachers = TeacherRepository()
        self.students = StudentRepository()
        self.courses = CourseRepository()
        self.enrollments = EnrollmentRepository()
        self.assignments = AssignmentRepository()
        self.attendances = AttendanceRepository()
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
            "teachers": self.teachers.count(),
            "students": self.students.count(),
            "courses": self.courses.count(),
            "enrollments": self.enrollments.count(),
            "assignments": self.assignments.count(),
            "attendances": self.attendances.count(),
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


class TeacherService:
    """Create, change and remove teachers."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.teachers

    def create(self, data: Dict[str, Any]) -> Teacher:
        """Validate and store a new teacher."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Teacher.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Teacher:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("teacher", item_id)
        return item

    def list(self, **filters: Any) -> List[Teacher]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in TEACHER_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Teacher:
        """Change some fields of a teacher."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a teacher nobody points at any more."""
        self.get(item_id)
        if self.store.courses.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by courses")
        if self.store.documents.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by documents")
        if self.store.addresses.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by addresses")
        if self.store.reminders.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by reminders")
        if self.store.notes.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by notes")
        if self.store.reviews.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by reviews")
        if self.store.contact_persons.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by contact persons")
        if self.store.tags.count_for_teacher(item_id):
            raise Conflict(f"teacher {item_id} is still used by tags")
        self.repo.remove(item_id)

    def _check_links(self, item: Teacher) -> None:
        """Teacher doesn't point at other records."""
        return None

    def adjust_salary(self, item_id: int, delta: float) -> Teacher:
        item = self.get(item_id)
        return self.update(item_id, {"salary": round(item.salary + delta, 2)})

    def toggle_full_time(self, item_id: int) -> Teacher:
        item = self.get(item_id)
        return self.update(item_id, {"full_time": not item.full_time})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every teacher."""
        return {
            "count": self.repo.count(),
            "total_salary": round(self.repo.total_salary(), 2),
            "average_salary": round(self.repo.average_salary(), 2),
            "full_time": len(self.repo.where_full_time(True)),
        }


class StudentService:
    """Create, change and remove students."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.students

    def create(self, data: Dict[str, Any]) -> Student:
        """Validate and store a new student."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Student.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Student:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("student", item_id)
        return item

    def list(self, **filters: Any) -> List[Student]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in STUDENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Student:
        """Change some fields of a student."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a student nobody points at any more."""
        self.get(item_id)
        if self.store.enrollments.count_for_student(item_id):
            raise Conflict(f"student {item_id} is still used by enrollments")
        if self.store.attendances.count_for_student(item_id):
            raise Conflict(f"student {item_id} is still used by attendances")
        self.repo.remove(item_id)

    def _check_links(self, item: Student) -> None:
        """Student doesn't point at other records."""
        return None

    def adjust_grade_level(self, item_id: int, delta: int) -> Student:
        """Add `delta` to the grade level (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"grade_level": item.grade_level + delta})

    def toggle_active(self, item_id: int) -> Student:
        item = self.get(item_id)
        return self.update(item_id, {"active": not item.active})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every student."""
        return {
            "count": self.repo.count(),
            "total_grade_level": round(self.repo.total_grade_level(), 2),
            "average_grade_level": round(self.repo.average_grade_level(), 2),
            "active": len(self.repo.where_active(True)),
        }


class CourseService:
    """Create, change and remove courses."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.courses

    def create(self, data: Dict[str, Any]) -> Course:
        """Validate and store a new course."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Course.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Course:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("course", item_id)
        return item

    def list(self, **filters: Any) -> List[Course]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in COURSE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Course:
        """Change some fields of a course."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a course nobody points at any more."""
        self.get(item_id)
        if self.store.enrollments.count_for_course(item_id):
            raise Conflict(f"course {item_id} is still used by enrollments")
        if self.store.assignments.count_for_course(item_id):
            raise Conflict(f"course {item_id} is still used by assignments")
        if self.store.attendances.count_for_course(item_id):
            raise Conflict(f"course {item_id} is still used by attendances")
        self.repo.remove(item_id)

    def _check_links(self, item: Course) -> None:
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

    def adjust_credits(self, item_id: int, delta: int) -> Course:
        """Add `delta` to the credits (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"credits": item.credits + delta})

    def set_term(self, item_id: int, value: Any) -> Course:
        """Move a course to another term."""
        return self.update(item_id, {"term": value})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every course."""
        return {
            "count": self.repo.count(),
            "total_credits": round(self.repo.total_credits(), 2),
            "average_credits": round(self.repo.average_credits(), 2),
            "by_term": self.repo.count_by_term(),
        }


class EnrollmentService:
    """Create, change and remove enrollments."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.enrollments

    def create(self, data: Dict[str, Any]) -> Enrollment:
        """Validate and store a new enrollment."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Enrollment.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Enrollment:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("enrollment", item_id)
        return item

    def list(self, **filters: Any) -> List[Enrollment]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ENROLLMENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Enrollment:
        """Change some fields of a enrollment."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a enrollment nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Enrollment) -> None:
        if self.store.courses.get(item.course_id) is None:
            raise NotFound("course", item.course_id)
        if self.store.students.get(item.student_id) is None:
            raise NotFound("student", item.student_id)

    def set_status(self, item_id: int, value: Any) -> Enrollment:
        """Move a enrollment to another status."""
        return self.update(item_id, {"status": value})

    def adjust_final_score(self, item_id: int, delta: float) -> Enrollment:
        item = self.get(item_id)
        return self.update(item_id, {"final_score": round(item.final_score + delta, 2)})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every enrollment."""
        return {
            "count": self.repo.count(),
            "by_status": self.repo.count_by_status(),
            "total_final_score": round(self.repo.total_final_score(), 2),
            "average_final_score": round(self.repo.average_final_score(), 2),
        }


class AssignmentService:
    """Create, change and remove assignments."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.assignments

    def create(self, data: Dict[str, Any]) -> Assignment:
        """Validate and store a new assignment."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Assignment.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Assignment:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("assignment", item_id)
        return item

    def list(self, **filters: Any) -> List[Assignment]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ASSIGNMENT_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Assignment:
        """Change some fields of a assignment."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a assignment nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Assignment) -> None:
        if self.store.courses.get(item.course_id) is None:
            raise NotFound("course", item.course_id)

    def adjust_max_points(self, item_id: int, delta: int) -> Assignment:
        """Add `delta` to the max points (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"max_points": item.max_points + delta})

    def adjust_weight(self, item_id: int, delta: float) -> Assignment:
        item = self.get(item_id)
        return self.update(item_id, {"weight": round(item.weight + delta, 2)})

    def toggle_published(self, item_id: int) -> Assignment:
        item = self.get(item_id)
        return self.update(item_id, {"published": not item.published})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every assignment."""
        return {
            "count": self.repo.count(),
            "total_max_points": round(self.repo.total_max_points(), 2),
            "average_max_points": round(self.repo.average_max_points(), 2),
            "total_weight": round(self.repo.total_weight(), 2),
            "average_weight": round(self.repo.average_weight(), 2),
            "published": len(self.repo.where_published(True)),
        }


class AttendanceService:
    """Create, change and remove attendances."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.attendances

    def create(self, data: Dict[str, Any]) -> Attendance:
        """Validate and store a new attendance."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Attendance.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Attendance:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("attendance", item_id)
        return item

    def list(self, **filters: Any) -> List[Attendance]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ATTENDANCE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Attendance:
        """Change some fields of a attendance."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a attendance nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Attendance) -> None:
        if self.store.students.get(item.student_id) is None:
            raise NotFound("student", item.student_id)
        if self.store.courses.get(item.course_id) is None:
            raise NotFound("course", item.course_id)

    def toggle_present(self, item_id: int) -> Attendance:
        item = self.get(item_id)
        return self.update(item_id, {"present": not item.present})

    def adjust_minutes_late(self, item_id: int, delta: int) -> Attendance:
        """Add `delta` to the minutes late (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"minutes_late": item.minutes_late + delta})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every attendance."""
        return {
            "count": self.repo.count(),
            "present": len(self.repo.where_present(True)),
            "total_minutes_late": round(self.repo.total_minutes_late(), 2),
            "average_minutes_late": round(self.repo.average_minutes_late(), 2),
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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        if self.store.teachers.get(item.teacher_id) is None:
            raise NotFound("teacher", item.teacher_id)

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
        self.teachers = TeacherService(self.store)
        self.students = StudentService(self.store)
        self.courses = CourseService(self.store)
        self.enrollments = EnrollmentService(self.store)
        self.assignments = AssignmentService(self.store)
        self.attendances = AttendanceService(self.store)
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
            self.teachers.create(sample_teacher(index))
            self.students.create(sample_student(index))
            self.courses.create(sample_course(index))
            self.enrollments.create(sample_enrollment(index))
            self.assignments.create(sample_assignment(index))
            self.attendances.create(sample_attendance(index))
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
            "teachers": self.teachers.stats(),
            "students": self.students.stats(),
            "courses": self.courses.stats(),
            "enrollments": self.enrollments.stats(),
            "assignments": self.assignments.stats(),
            "attendances": self.attendances.stats(),
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


def sample_teacher(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new teacher (refs point at seeded records)."""
    return {
        "name": f"Teacher name {index}",
        "email": f"teacher{index}@example.com",
        "subject": f"Teacher subject {index}",
        "hired": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "salary": round(10.0 * index + 0.99, 2),
        "full_time": index % 2 == 1,
    }


def sample_student(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new student (refs point at seeded records)."""
    return {
        "name": f"Student name {index}",
        "email": f"student{index}@example.com",
        "birth_date": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "grade_level": index + 1,
        "guardian": f"Student guardian {index}",
        "active": index % 2 == 1,
    }


def sample_course(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new course (refs point at seeded records)."""
    return {
        "teacher_id": (index - 1) % 3 + 1,
        "title": f"Course title {index}",
        "code": f"Course code {index}",
        "credits": index + 1,
        "room": f"Course room {index}",
        "term": ['fall', 'spring', 'summer'][index % 3],
    }


def sample_enrollment(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new enrollment (refs point at seeded records)."""
    return {
        "course_id": (index - 1) % 3 + 1,
        "student_id": (index - 1) % 3 + 1,
        "enrolled": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "status": ['active', 'dropped', 'completed'][index % 3],
        "final_score": round(1.5 * index + 0.25, 2),
    }


def sample_assignment(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new assignment (refs point at seeded records)."""
    return {
        "course_id": (index - 1) % 3 + 1,
        "title": f"Assignment title {index}",
        "due": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "max_points": index + 1,
        "weight": round(1.5 * index + 0.25, 2),
        "published": index % 2 == 1,
    }


def sample_attendance(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new attendance (refs point at seeded records)."""
    return {
        "student_id": (index - 1) % 3 + 1,
        "course_id": (index - 1) % 3 + 1,
        "day": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "present": index % 2 == 1,
        "minutes_late": index + 1,
        "note": f"Notes about attendance {index}.",
    }


def sample_document(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new document (refs point at seeded records)."""
    return {
        "teacher_id": (index - 1) % 3 + 1,
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
        "teacher_id": (index - 1) % 3 + 1,
        "street": f"Address street {index}",
        "city": f"Address city {index}",
        "postcode": f"Address postcode {index}",
        "country": f"Address country {index}",
        "billing": index % 2 == 1,
    }


def sample_reminder(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new reminder (refs point at seeded records)."""
    return {
        "teacher_id": (index - 1) % 3 + 1,
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
        "teacher_id": (index - 1) % 3 + 1,
        "subject": f"Note subject {index}",
        "body": f"Notes about note {index}.",
        "pinned": index % 2 == 1,
        "written": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_review(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new review (refs point at seeded records)."""
    return {
        "teacher_id": (index - 1) % 3 + 1,
        "author": f"Review author {index}",
        "stars": index + 1,
        "comment": f"Notes about review {index}.",
        "verified": index % 2 == 1,
        "posted": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
    }


def sample_contact_person(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new contact person (refs point at seeded records)."""
    return {
        "teacher_id": (index - 1) % 3 + 1,
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
        "teacher_id": (index - 1) % 3 + 1,
        "label": f"Tag label {index}",
        "color": f"Tag color {index}",
        "usage": index + 1,
    }
