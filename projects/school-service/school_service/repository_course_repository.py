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
from .repository_course_repository_part1 import *  # noqa: F401,F403


class CourseRepository(CourseRepositoryPart1):
    """All courses, with the lookups the services need (continued)."""

    def count_by_term(self) -> Dict[str, int]:
        """How many records have each term."""
        counts = {member.value: 0 for member in CourseTerm}
        for item in self.list():
            counts[CourseTerm(item.term).value] += 1
        return counts

    def search(self, text: str) -> List[Course]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.title,
            item.code,
            item.room,
        )))
