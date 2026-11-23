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


class CourseValidationTests2(unittest.TestCase):
    """Course: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.courses
        self.repo = self.services.store.courses

    def test_rejects_bad_term(self) -> None:
        data = sample_course(12)
        data["term"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "term")

    def test_teacher_id_must_exist(self) -> None:
        data = sample_course(13)
        data["teacher_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
