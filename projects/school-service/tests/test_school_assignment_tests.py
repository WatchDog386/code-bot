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


class AssignmentTests(unittest.TestCase):
    """Assignment: creating and reading."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.assignments
        self.repo = self.services.store.assignments

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_assignment(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)
