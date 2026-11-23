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
from .repository_enrollment_repository import *  # noqa: F401,F403


class AssignmentRepositoryPart1(Repository[Assignment]):
    """All assignments, with the lookups the services need."""

    model = Assignment
    entity_name = "assignment"

    def for_course(self, course_id: int) -> List[Assignment]:
        """Records linked to course `course_id`."""
        return self.where(lambda item: item.course_id == course_id)

    def count_for_course(self, course_id: int) -> int:
        return len(self.for_course(course_id))

    def find_by_title(self, value: str) -> List[Assignment]:
        """Records whose title is exactly `value`."""
        return self.where(lambda item: item.title == value)

    def search_title(self, text: str) -> List[Assignment]:
        """Records whose title contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.title.lower())

    def due_before(self, day: str) -> List[Assignment]:
        return self.where(lambda item: item.due < day)

    def due_after(self, day: str) -> List[Assignment]:
        return self.where(lambda item: item.due > day)

    def due_on(self, day: str) -> List[Assignment]:
        return self.where(lambda item: item.due == day)

    def between_max_points(self, low: float, high: float) -> List[Assignment]:
        """Records whose max points is within [low, high]."""
        return self.where(lambda item: low <= item.max_points <= high)

    def total_max_points(self) -> float:
        return sum(item.max_points for item in self.list())

    def average_max_points(self) -> float:
        items = self.list()
        return sum(item.max_points for item in items) / len(items) if items else 0.0

    def max_max_points(self) -> Optional[Assignment]:
        """The record with the highest max points."""
        items = self.list()
        return max(items, key=lambda item: item.max_points) if items else None

    def between_weight(self, low: float, high: float) -> List[Assignment]:
        """Records whose weight is within [low, high]."""
        return self.where(lambda item: low <= item.weight <= high)

    def total_weight(self) -> float:
        return sum(item.weight for item in self.list())

    def average_weight(self) -> float:
        items = self.list()
        return sum(item.weight for item in items) / len(items) if items else 0.0
