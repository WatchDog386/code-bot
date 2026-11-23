"""Repository (continued)."""

from __future__ import annotations

import csv
import io
import json
import threading
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import (
    Booking,
    BookingStatus,
    Charge,
    ChargeCategory,
    Guest,
    Housekeeping,
    Room,
    RoomStatus,
    RoomType,
)

T = TypeVar("T")
from .repository_booking_repository_part1 import *  # noqa: F401,F403


class BookingRepository(BookingRepositoryPart1):
    """All bookings, with the lookups the services need (continued)."""

    def average_total(self) -> float:
        items = self.list()
        return sum(item.total for item in items) / len(items) if items else 0.0

    def max_total(self) -> Optional[Booking]:
        """The record with the highest total."""
        items = self.list()
        return max(items, key=lambda item: item.total) if items else None

    def with_status(self, value: Any) -> List[Booking]:
        wanted = BookingStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in BookingStatus}
        for item in self.list():
            counts[BookingStatus(item.status).value] += 1
        return counts

    def find_by_notes(self, value: str) -> List[Booking]:
        """Records whose notes is exactly `value`."""
        return self.where(lambda item: item.notes == value)

    def search_notes(self, text: str) -> List[Booking]:
        """Records whose notes contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.notes.lower())

    def search(self, text: str) -> List[Booking]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.notes,
        )))
