"""Test school (continued)."""

import unittest

from school_service.api import Api
from school_service.models import ValidationError
from school_service.repository import (
    TeacherRepository,
    StudentRepository,
    CourseRepository,
    EnrollmentRepository,
    AssignmentRepository,
    AttendanceRepository,
)
from school_service.services import (
    Conflict,
    NotFound,
    Services,
    sample_teacher,
    sample_student,
    sample_course,
    sample_enrollment,
    sample_assignment,
    sample_attendance,
)


class AttendanceOperationTests(unittest.TestCase):
    """Attendance: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.attendances
        self.repo = self.services.store.attendances

    def test_day_ranges(self) -> None:
        day = self.service.get(2).day
        total = len(self.repo.day_before(day)) + len(self.repo.day_on(day)) + len(self.repo.day_after(day))
        self.assertEqual(total, self.repo.count())

    def test_toggle_present(self) -> None:
        before = self.service.get(1).present
        self.assertEqual(self.service.toggle_present(1).present, not before)

    def test_adjust_minutes_late(self) -> None:
        before = self.service.get(1).minutes_late
        self.assertEqual(self.service.adjust_minutes_late(1, 2).minutes_late, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_minutes_late(1, -(before + 100))

    def test_search_note(self) -> None:
        target = self.service.get(2).note
        self.assertIn(self.service.get(2), self.repo.search_note(target.upper()))
        self.assertEqual(len(self.repo.find_by_note(target)), len([i for i in self.repo.list() if i.note == target]))

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_attendance(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = AttendanceRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)
