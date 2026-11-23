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


class CourseOperationTests(unittest.TestCase):
    """Course: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.courses
        self.repo = self.services.store.courses

    def test_search_title(self) -> None:
        target = self.service.get(2).title
        self.assertIn(self.service.get(2), self.repo.search_title(target.upper()))
        self.assertEqual(len(self.repo.find_by_title(target)), len([i for i in self.repo.list() if i.title == target]))

    def test_search_code(self) -> None:
        target = self.service.get(2).code
        self.assertIn(self.service.get(2), self.repo.search_code(target.upper()))
        self.assertEqual(len(self.repo.find_by_code(target)), len([i for i in self.repo.list() if i.code == target]))

    def test_adjust_credits(self) -> None:
        before = self.service.get(1).credits
        self.assertEqual(self.service.adjust_credits(1, 2).credits, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_credits(1, -(before + 100))

    def test_search_room(self) -> None:
        target = self.service.get(2).room
        self.assertIn(self.service.get(2), self.repo.search_room(target.upper()))
        self.assertEqual(len(self.repo.find_by_room(target)), len([i for i in self.repo.list() if i.room == target]))

    def test_set_term(self) -> None:
        item = self.service.set_term(1, "summer")
        self.assertEqual(item.term.value, "summer")
        self.assertEqual(self.repo.count_by_term()["summer"], len(self.repo.with_term("summer")))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_course(20)["title"]
        after = self.service.update(1, {"title": new_value})
        self.assertEqual(after.title, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_course(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())
