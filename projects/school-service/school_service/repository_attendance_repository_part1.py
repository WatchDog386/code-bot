"""Repository (continued)."""

from __future__ import annotations

import csv
import io
import json
import threading
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import (
    Assignment,
    Attendance,
    Course,
    CourseTerm,
    Enrollment,
    EnrollmentStatus,
    Student,
    Teacher,
)

T = TypeVar("T")
from .repository_assignment_repository import *  # noqa: F401,F403


class AttendanceRepositoryPart1(Repository[Attendance]):
    """All attendances, with the lookups the services need."""

    model = Attendance
    entity_name = "attendance"

    def for_student(self, student_id: int) -> List[Attendance]:
        """Records linked to student `student_id`."""
        return self.where(lambda item: item.student_id == student_id)

    def count_for_student(self, student_id: int) -> int:
        return len(self.for_student(student_id))

    def for_course(self, course_id: int) -> List[Attendance]:
        """Records linked to course `course_id`."""
        return self.where(lambda item: item.course_id == course_id)

    def count_for_course(self, course_id: int) -> int:
        return len(self.for_course(course_id))

    def day_before(self, day: str) -> List[Attendance]:
        return self.where(lambda item: item.day < day)

    def day_after(self, day: str) -> List[Attendance]:
        return self.where(lambda item: item.day > day)

    def day_on(self, day: str) -> List[Attendance]:
        return self.where(lambda item: item.day == day)

    def where_present(self, flag: bool = True) -> List[Attendance]:
        return self.where(lambda item: item.present is flag)

    def between_minutes_late(self, low: float, high: float) -> List[Attendance]:
        """Records whose minutes late is within [low, high]."""
        return self.where(lambda item: low <= item.minutes_late <= high)

    def total_minutes_late(self) -> float:
        return sum(item.minutes_late for item in self.list())

    def average_minutes_late(self) -> float:
        items = self.list()
        return sum(item.minutes_late for item in items) / len(items) if items else 0.0

    def max_minutes_late(self) -> Optional[Attendance]:
        """The record with the highest minutes late."""
        items = self.list()
        return max(items, key=lambda item: item.minutes_late) if items else None

    def find_by_note(self, value: str) -> List[Attendance]:
        """Records whose note is exactly `value`."""
        return self.where(lambda item: item.note == value)

    def search_note(self, text: str) -> List[Attendance]:
        """Records whose note contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.note.lower())
