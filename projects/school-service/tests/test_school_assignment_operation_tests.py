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


class AssignmentOperationTests(unittest.TestCase):
    """Assignment: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.assignments
        self.repo = self.services.store.assignments

    def test_search_title(self) -> None:
        target = self.service.get(2).title
        self.assertIn(self.service.get(2), self.repo.search_title(target.upper()))
        self.assertEqual(len(self.repo.find_by_title(target)), len([i for i in self.repo.list() if i.title == target]))

    def test_due_ranges(self) -> None:
        day = self.service.get(2).due
        total = len(self.repo.due_before(day)) + len(self.repo.due_on(day)) + len(self.repo.due_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_max_points(self) -> None:
        before = self.service.get(1).max_points
        self.assertEqual(self.service.adjust_max_points(1, 2).max_points, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_max_points(1, -(before + 100))

    def test_adjust_weight(self) -> None:
        before = self.service.get(1).weight
        self.assertAlmostEqual(self.service.adjust_weight(1, 1.5).weight, before + 1.5, places=2)

    def test_toggle_published(self) -> None:
        before = self.service.get(1).published
        self.assertEqual(self.service.toggle_published(1).published, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_assignment(20)["title"]
        after = self.service.update(1, {"title": new_value})
        self.assertEqual(after.title, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_assignment(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = AssignmentRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)
