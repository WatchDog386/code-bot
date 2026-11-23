"""Models (continued)."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import date
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Tuple, Type

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_INT = 1_000_000_000
from .models_assignment_fields import *  # noqa: F401,F403


@dataclass
class Assignment:
    """A assignment record."""

    id: int = 0
    course_id: int = 0
    title: str = ""
    due: str = ""
    max_points: int = 0
    weight: float = 0.0
    published: bool = False

    def validate(self) -> "Assignment":
        """Check every field and normalise the values in place."""
        self.course_id = validate_assignment_course_id(self.course_id)
        self.title = validate_assignment_title(self.title)
        self.due = validate_assignment_due(self.due)
        self.max_points = validate_assignment_max_points(self.max_points)
        self.weight = validate_assignment_weight(self.weight)
        self.published = validate_assignment_published(self.published)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "due": self.due,
            "max_points": self.max_points,
            "weight": self.weight,
            "published": self.published,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assignment":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ASSIGNMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "course_id" in data:
            item.course_id = data["course_id"]
        if "title" in data:
            item.title = data["title"]
        if "due" in data:
            item.due = data["due"]
        if "max_points" in data:
            item.max_points = data["max_points"]
        if "weight" in data:
            item.weight = data["weight"]
        if "published" in data:
            item.published = data["published"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Assignment":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ASSIGNMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Assignment #{self.id}: {self.title}"


# -------------------------------------------------------------------------- Attendance
ATTENDANCE_FIELDS: FrozenSet[str] = frozenset({
    "id",
    "student_id",
    "course_id",
    "day",
    "present",
    "minutes_late",
    "note",
})
