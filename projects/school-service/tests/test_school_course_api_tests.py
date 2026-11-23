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


class CourseApiTests(unittest.TestCase):
    """Course: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.courses
        self.repo = self.services.store.courses

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/courses", sample_course(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/courses/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/courses?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/courses/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/courses/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/courses/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/courses", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/courses?sort=nope")[0], 400)
