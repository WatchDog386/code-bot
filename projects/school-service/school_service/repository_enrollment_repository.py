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
from .repository_course_repository import *  # noqa: F401,F403


class EnrollmentRepository(Repository[Enrollment]):
    """All enrollments, with the lookups the services need."""

    model = Enrollment
    entity_name = "enrollment"

    def for_course(self, course_id: int) -> List[Enrollment]:
        """Records linked to course `course_id`."""
        return self.where(lambda item: item.course_id == course_id)

    def count_for_course(self, course_id: int) -> int:
        return len(self.for_course(course_id))

    def for_student(self, student_id: int) -> List[Enrollment]:
        """Records linked to student `student_id`."""
        return self.where(lambda item: item.student_id == student_id)

    def count_for_student(self, student_id: int) -> int:
        return len(self.for_student(student_id))

    def enrolled_before(self, day: str) -> List[Enrollment]:
        return self.where(lambda item: item.enrolled < day)

    def enrolled_after(self, day: str) -> List[Enrollment]:
        return self.where(lambda item: item.enrolled > day)

    def enrolled_on(self, day: str) -> List[Enrollment]:
        return self.where(lambda item: item.enrolled == day)

    def with_status(self, value: Any) -> List[Enrollment]:
        wanted = EnrollmentStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in EnrollmentStatus}
        for item in self.list():
            counts[EnrollmentStatus(item.status).value] += 1
        return counts

    def between_final_score(self, low: float, high: float) -> List[Enrollment]:
        """Records whose final score is within [low, high]."""
        return self.where(lambda item: low <= item.final_score <= high)

    def total_final_score(self) -> float:
        return sum(item.final_score for item in self.list())

    def average_final_score(self) -> float:
        items = self.list()
        return sum(item.final_score for item in items) / len(items) if items else 0.0

    def max_final_score(self) -> Optional[Enrollment]:
        """The record with the highest final score."""
        items = self.list()
        return max(items, key=lambda item: item.final_score) if items else None

    def search(self, text: str) -> List[Enrollment]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: needle == str(item.id))
