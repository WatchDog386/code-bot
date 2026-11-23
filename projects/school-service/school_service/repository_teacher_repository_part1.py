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
from .repository_repository import *  # noqa: F401,F403


class TeacherRepositoryPart1(Repository[Teacher]):
    """All teachers, with the lookups the services need."""

    model = Teacher
    entity_name = "teacher"

    def find_by_name(self, value: str) -> List[Teacher]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Teacher]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Teacher]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Teacher]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def find_by_subject(self, value: str) -> List[Teacher]:
        """Records whose subject is exactly `value`."""
        return self.where(lambda item: item.subject == value)

    def search_subject(self, text: str) -> List[Teacher]:
        """Records whose subject contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.subject.lower())

    def hired_before(self, day: str) -> List[Teacher]:
        return self.where(lambda item: item.hired < day)

    def hired_after(self, day: str) -> List[Teacher]:
        return self.where(lambda item: item.hired > day)

    def hired_on(self, day: str) -> List[Teacher]:
        return self.where(lambda item: item.hired == day)

    def between_salary(self, low: float, high: float) -> List[Teacher]:
        """Records whose salary is within [low, high]."""
        return self.where(lambda item: low <= item.salary <= high)

    def total_salary(self) -> float:
        return sum(item.salary for item in self.list())

    def average_salary(self) -> float:
        items = self.list()
        return sum(item.salary for item in items) / len(items) if items else 0.0

    def max_salary(self) -> Optional[Teacher]:
        """The record with the highest salary."""
        items = self.list()
        return max(items, key=lambda item: item.salary) if items else None

    def where_full_time(self, flag: bool = True) -> List[Teacher]:
        return self.where(lambda item: item.full_time is flag)
