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
from .repository_assignment_repository_part1 import *  # noqa: F401,F403


class AssignmentRepository(AssignmentRepositoryPart1):
    """All assignments, with the lookups the services need (continued)."""

    def max_weight(self) -> Optional[Assignment]:
        """The record with the highest weight."""
        items = self.list()
        return max(items, key=lambda item: item.weight) if items else None

    def where_published(self, flag: bool = True) -> List[Assignment]:
        return self.where(lambda item: item.published is flag)

    def search(self, text: str) -> List[Assignment]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.title,
        )))
