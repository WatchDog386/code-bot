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
from .models_enrollment_fields import *  # noqa: F401,F403


@dataclass
class Enrollment:
    """A enrollment record."""

    id: int = 0
    course_id: int = 0
    student_id: int = 0
    enrolled: str = ""
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    final_score: float = 0.0

    def validate(self) -> "Enrollment":
        """Check every field and normalise the values in place."""
        self.course_id = validate_enrollment_course_id(self.course_id)
        self.student_id = validate_enrollment_student_id(self.student_id)
        self.enrolled = validate_enrollment_enrolled(self.enrolled)
        self.status = validate_enrollment_status(self.status)
        self.final_score = validate_enrollment_final_score(self.final_score)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "student_id": self.student_id,
            "enrolled": self.enrolled,
            "status": self.status.value,
            "final_score": self.final_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Enrollment":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ENROLLMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "course_id" in data:
            item.course_id = data["course_id"]
        if "student_id" in data:
            item.student_id = data["student_id"]
        if "enrolled" in data:
            item.enrolled = data["enrolled"]
        if "status" in data:
            item.status = data["status"]
        if "final_score" in data:
            item.final_score = data["final_score"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Enrollment":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ENROLLMENT_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Enrollment #{self.id}"
