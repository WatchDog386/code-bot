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
from .models_validate_student_active import *  # noqa: F401,F403


@dataclass
class Student:
    """A student record."""

    id: int = 0
    name: str = ""
    email: str = ""
    birth_date: str = ""
    grade_level: int = 0
    guardian: str = ""
    active: bool = False

    def validate(self) -> "Student":
        """Check every field and normalise the values in place."""
        self.name = validate_student_name(self.name)
        self.email = validate_student_email(self.email)
        self.birth_date = validate_student_birth_date(self.birth_date)
        self.grade_level = validate_student_grade_level(self.grade_level)
        self.guardian = validate_student_guardian(self.guardian)
        self.active = validate_student_active(self.active)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "birth_date": self.birth_date,
            "grade_level": self.grade_level,
            "guardian": self.guardian,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, STUDENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "birth_date" in data:
            item.birth_date = data["birth_date"]
        if "grade_level" in data:
            item.grade_level = data["grade_level"]
        if "guardian" in data:
            item.guardian = data["guardian"]
        if "active" in data:
            item.active = data["active"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Student":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, STUDENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Student #{self.id}: {self.name}"
