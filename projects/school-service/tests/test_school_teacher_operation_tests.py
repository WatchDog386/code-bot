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


class TeacherOperationTests(unittest.TestCase):
    """Teacher: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.teachers
        self.repo = self.services.store.teachers

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_search_email(self) -> None:
        target = self.service.get(2).email
        self.assertIn(self.service.get(2), self.repo.search_email(target.upper()))
        self.assertEqual(len(self.repo.find_by_email(target)), len([i for i in self.repo.list() if i.email == target]))

    def test_search_subject(self) -> None:
        target = self.service.get(2).subject
        self.assertIn(self.service.get(2), self.repo.search_subject(target.upper()))
        self.assertEqual(len(self.repo.find_by_subject(target)), len([i for i in self.repo.list() if i.subject == target]))

    def test_hired_ranges(self) -> None:
        day = self.service.get(2).hired
        total = len(self.repo.hired_before(day)) + len(self.repo.hired_on(day)) + len(self.repo.hired_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_salary(self) -> None:
        before = self.service.get(1).salary
        self.assertAlmostEqual(self.service.adjust_salary(1, 1.5).salary, before + 1.5, places=2)

    def test_toggle_full_time(self) -> None:
        before = self.service.get(1).full_time
        self.assertEqual(self.service.toggle_full_time(1).full_time, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_teacher(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_teacher(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)
