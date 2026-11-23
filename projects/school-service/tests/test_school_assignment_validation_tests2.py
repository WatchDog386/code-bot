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


class AssignmentValidationTests2(unittest.TestCase):
    """Assignment: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.assignments
        self.repo = self.services.store.assignments

    def test_rejects_bad_published(self) -> None:
        data = sample_assignment(12)
        data["published"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "published")

    def test_course_id_must_exist(self) -> None:
        data = sample_assignment(13)
        data["course_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
