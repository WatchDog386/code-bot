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
from .models_enrollment_status import *  # noqa: F401,F403


@dataclass
class Teacher:
    """A teacher record."""

    id: int = 0
    name: str = ""
    email: str = ""
    subject: str = ""
    hired: str = ""
    salary: float = 0.0
    full_time: bool = False

    def validate(self) -> "Teacher":
        """Check every field and normalise the values in place."""
        self.name = validate_teacher_name(self.name)
        self.email = validate_teacher_email(self.email)
        self.subject = validate_teacher_subject(self.subject)
        self.hired = validate_teacher_hired(self.hired)
        self.salary = validate_teacher_salary(self.salary)
        self.full_time = validate_teacher_full_time(self.full_time)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "hired": self.hired,
            "salary": self.salary,
            "full_time": self.full_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Teacher":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, TEACHER_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "name" in data:
            item.name = data["name"]
        if "email" in data:
            item.email = data["email"]
        if "subject" in data:
            item.subject = data["subject"]
        if "hired" in data:
            item.hired = data["hired"]
        if "salary" in data:
            item.salary = data["salary"]
        if "full_time" in data:
            item.full_time = data["full_time"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Teacher":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, TEACHER_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Teacher #{self.id}: {self.name}"
