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


class StudentApiTests(unittest.TestCase):
    """Student: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.students
        self.repo = self.services.store.students

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/students", sample_student(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/students/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/students?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/students/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/students/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/students/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/students", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/students?sort=nope")[0], 400)


class CourseTests(unittest.TestCase):
    """Course: creating and reading."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.courses
        self.repo = self.services.store.courses

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_course(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)
