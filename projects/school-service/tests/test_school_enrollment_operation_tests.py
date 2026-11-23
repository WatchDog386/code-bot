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


class EnrollmentOperationTests(unittest.TestCase):
    """Enrollment: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.enrollments
        self.repo = self.services.store.enrollments

    def test_enrolled_ranges(self) -> None:
        day = self.service.get(2).enrolled
        total = len(self.repo.enrolled_before(day)) + len(self.repo.enrolled_on(day)) + len(self.repo.enrolled_after(day))
        self.assertEqual(total, self.repo.count())

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "completed")
        self.assertEqual(item.status.value, "completed")
        self.assertEqual(self.repo.count_by_status()["completed"], len(self.repo.with_status("completed")))

    def test_adjust_final_score(self) -> None:
        before = self.service.get(1).final_score
        self.assertAlmostEqual(self.service.adjust_final_score(1, 1.5).final_score, before + 1.5, places=2)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_enrollment(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = EnrollmentRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)
