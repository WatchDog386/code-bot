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


class EnrollmentValidationTests2(unittest.TestCase):
    """Enrollment: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.enrollments
        self.repo = self.services.store.enrollments

    def test_course_id_must_exist(self) -> None:
        data = sample_enrollment(13)
        data["course_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_student_id_must_exist(self) -> None:
        data = sample_enrollment(13)
        data["student_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
