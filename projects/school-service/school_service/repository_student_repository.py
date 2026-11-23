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
from .repository_student_repository_part1 import *  # noqa: F401,F403


class StudentRepository(StudentRepositoryPart1):
    """All students, with the lookups the services need (continued)."""

    def search(self, text: str) -> List[Student]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.guardian,
        )))
