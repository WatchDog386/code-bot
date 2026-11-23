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
from .models_course_fields import *  # noqa: F401,F403


@dataclass
class Course:
    """A course record."""

    id: int = 0
    teacher_id: int = 0
    title: str = ""
    code: str = ""
    credits: int = 0
    room: str = ""
    term: CourseTerm = CourseTerm.FALL

    def validate(self) -> "Course":
        """Check every field and normalise the values in place."""
        self.teacher_id = validate_course_teacher_id(self.teacher_id)
        self.title = validate_course_title(self.title)
        self.code = validate_course_code(self.code)
        self.credits = validate_course_credits(self.credits)
        self.room = validate_course_room(self.room)
        self.term = validate_course_term(self.term)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "title": self.title,
            "code": self.code,
            "credits": self.credits,
            "room": self.room,
            "term": self.term.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Course":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, COURSE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "teacher_id" in data:
            item.teacher_id = data["teacher_id"]
        if "title" in data:
            item.title = data["title"]
        if "code" in data:
            item.code = data["code"]
        if "credits" in data:
            item.credits = data["credits"]
        if "room" in data:
            item.room = data["room"]
        if "term" in data:
            item.term = data["term"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Course":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, COURSE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Course #{self.id}: {self.title}"
