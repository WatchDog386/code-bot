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


class EnrollmentApiTests(unittest.TestCase):
    """Enrollment: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.enrollments
        self.repo = self.services.store.enrollments

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/enrollments", sample_enrollment(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/enrollments/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/enrollments?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/enrollments/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/enrollments/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/enrollments/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/enrollments", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/enrollments?sort=nope")[0], 400)
