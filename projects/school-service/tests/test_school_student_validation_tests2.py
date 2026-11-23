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


class StudentValidationTests2(unittest.TestCase):
    """Student: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.students
        self.repo = self.services.store.students

    def test_rejects_bad_active(self) -> None:
        data = sample_student(12)
        data["active"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "active")
