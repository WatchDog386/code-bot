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


class EnrollmentValidationTests(unittest.TestCase):
    """Enrollment: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.enrollments
        self.repo = self.services.store.enrollments

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_enrollment(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_enrollment(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_course_id(self) -> None:
        data = sample_enrollment(12)
        data["course_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "course_id")

    def test_rejects_bad_student_id(self) -> None:
        data = sample_enrollment(12)
        data["student_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "student_id")

    def test_rejects_bad_enrolled(self) -> None:
        data = sample_enrollment(12)
        data["enrolled"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "enrolled")

    def test_rejects_bad_status(self) -> None:
        data = sample_enrollment(12)
        data["status"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "status")

    def test_rejects_bad_final_score(self) -> None:
        data = sample_enrollment(12)
        data["final_score"] = -1.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "final_score")
