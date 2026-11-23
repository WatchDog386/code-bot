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
from .repository_teacher_repository import *  # noqa: F401,F403


class StudentRepositoryPart1(Repository[Student]):
    """All students, with the lookups the services need."""

    model = Student
    entity_name = "student"

    def find_by_name(self, value: str) -> List[Student]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Student]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Student]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Student]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def birth_date_before(self, day: str) -> List[Student]:
        return self.where(lambda item: item.birth_date < day)

    def birth_date_after(self, day: str) -> List[Student]:
        return self.where(lambda item: item.birth_date > day)

    def birth_date_on(self, day: str) -> List[Student]:
        return self.where(lambda item: item.birth_date == day)

    def between_grade_level(self, low: float, high: float) -> List[Student]:
        """Records whose grade level is within [low, high]."""
        return self.where(lambda item: low <= item.grade_level <= high)

    def total_grade_level(self) -> float:
        return sum(item.grade_level for item in self.list())

    def average_grade_level(self) -> float:
        items = self.list()
        return sum(item.grade_level for item in items) / len(items) if items else 0.0

    def max_grade_level(self) -> Optional[Student]:
        """The record with the highest grade level."""
        items = self.list()
        return max(items, key=lambda item: item.grade_level) if items else None

    def find_by_guardian(self, value: str) -> List[Student]:
        """Records whose guardian is exactly `value`."""
        return self.where(lambda item: item.guardian == value)

    def search_guardian(self, text: str) -> List[Student]:
        """Records whose guardian contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.guardian.lower())

    def where_active(self, flag: bool = True) -> List[Student]:
        return self.where(lambda item: item.active is flag)
