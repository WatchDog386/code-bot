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
from .repository_student_repository import *  # noqa: F401,F403


class CourseRepositoryPart1(Repository[Course]):
    """All courses, with the lookups the services need."""

    model = Course
    entity_name = "course"

    def for_teacher(self, teacher_id: int) -> List[Course]:
        """Records linked to teacher `teacher_id`."""
        return self.where(lambda item: item.teacher_id == teacher_id)

    def count_for_teacher(self, teacher_id: int) -> int:
        return len(self.for_teacher(teacher_id))

    def find_by_title(self, value: str) -> List[Course]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Course]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def find_by_code(self, value: str) -> List[Course]:
        """Records whose code is exactly `value`."""
        return self.where(lambda item: item.code == value)

    def search_code(self, text: str) -> List[Course]:
        """Records whose code contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.code.lower())

    def between_credits(self, low: float, high: float) -> List[Course]:
        """Records whose credits is within [low, high]."""
        return self.where(lambda item: low <= item.credits <= high)

    def total_credits(self) -> float:
        return sum(item.credits for item in self.list())

    def average_credits(self) -> float:
        items = self.list()
        return sum(item.credits for item in items) / len(items) if items else 0.0

    def max_credits(self) -> Optional[Course]:
        """The record with the highest credits."""
        items = self.list()
        return max(items, key=lambda item: item.credits) if items else None

    def find_by_room(self, value: str) -> List[Course]:
        """Records whose room is exactly `value`."""
        return self.where(lambda item: item.room == value)

    def search_room(self, text: str) -> List[Course]:
        """Records whose room contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.room.lower())

    def with_term(self, value: Any) -> List[Course]:
        wanted = CourseTerm(value)
        return self.where(lambda item: item.term == wanted)
