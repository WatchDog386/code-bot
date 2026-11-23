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


class AttendanceValidationTests2(unittest.TestCase):
    """Attendance: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.attendances
        self.repo = self.services.store.attendances

    def test_rejects_bad_note(self) -> None:
        data = sample_attendance(12)
        data["note"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "note")

    def test_student_id_must_exist(self) -> None:
        data = sample_attendance(13)
        data["student_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_course_id_must_exist(self) -> None:
        data = sample_attendance(13)
        data["course_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
