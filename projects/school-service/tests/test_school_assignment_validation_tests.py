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


class AssignmentValidationTests(unittest.TestCase):
    """Assignment: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.assignments
        self.repo = self.services.store.assignments

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_assignment(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_assignment(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_course_id(self) -> None:
        data = sample_assignment(12)
        data["course_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "course_id")

    def test_rejects_bad_title(self) -> None:
        data = sample_assignment(12)
        data["title"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "title")

    def test_rejects_bad_due(self) -> None:
        data = sample_assignment(12)
        data["due"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "due")

    def test_rejects_bad_max_points(self) -> None:
        data = sample_assignment(12)
        data["max_points"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "max_points")

    def test_rejects_bad_weight(self) -> None:
        data = sample_assignment(12)
        data["weight"] = -1.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "weight")
