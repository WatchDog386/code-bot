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
from .models_attendance_sortable import *  # noqa: F401,F403


@dataclass
class Attendance:
    """A attendance record."""

    id: int = 0
    student_id: int = 0
    course_id: int = 0
    day: str = ""
    present: bool = False
    minutes_late: int = 0
    note: str = ""

    def validate(self) -> "Attendance":
        """Check every field and normalise the values in place."""
        self.student_id = validate_attendance_student_id(self.student_id)
        self.course_id = validate_attendance_course_id(self.course_id)
        self.day = validate_attendance_day(self.day)
        self.present = validate_attendance_present(self.present)
        self.minutes_late = validate_attendance_minutes_late(self.minutes_late)
        self.note = validate_attendance_note(self.note)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Plain JSON-ready values."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "day": self.day,
            "present": self.present,
            "minutes_late": self.minutes_late,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attendance":
        """Build an (unvalidated) record from JSON values."""
        extra = unknown_fields(data, ATTENDANCE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        item = cls(id=check_int("id", data.get("id", 0)))
        if "student_id" in data:
            item.student_id = data["student_id"]
        if "course_id" in data:
            item.course_id = data["course_id"]
        if "day" in data:
            item.day = data["day"]
        if "present" in data:
            item.present = data["present"]
        if "minutes_late" in data:
            item.minutes_late = data["minutes_late"]
        if "note" in data:
            item.note = data["note"]
        return item

    def apply(self, changes: Dict[str, Any]) -> "Attendance":
        """A validated copy with `changes` applied; the id never changes."""
        if "id" in changes:
            raise ValidationError("id", "cannot be changed")
        extra = unknown_fields(changes, ATTENDANCE_FIELDS)
        if extra:
            raise ValidationError(extra, "is not a known field")
        return replace(self, **changes).validate()

    def summary(self) -> str:
        """One line for logs and lists."""
        return f"Attendance #{self.id}"
