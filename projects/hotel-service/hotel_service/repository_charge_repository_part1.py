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
from .repository_booking_repository import *  # noqa: F401,F403


class ChargeRepositoryPart1(Repository[Charge]):
    """All charges, with the lookups the services need."""

    model = Charge
    entity_name = "charge"

    def for_booking(self, booking_id: int) -> List[Charge]:
        """Records linked to booking `booking_id`."""
        return self.where(lambda item: item.booking_id == booking_id)

    def count_for_booking(self, booking_id: int) -> int:
        return len(self.for_booking(booking_id))

    def find_by_description(self, value: str) -> List[Charge]:
        """Records whose description is exactly `value`."""
        return self.where(lambda item: item.description == value)

    def search_description(self, text: str) -> List[Charge]:
        """Records whose description contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.description.lower())

    def between_amount(self, low: float, high: float) -> List[Charge]:
        """Records whose amount is within [low, high]."""
        return self.where(lambda item: low <= item.amount <= high)

    def total_amount(self) -> float:
        return sum(item.amount for item in self.list())

    def average_amount(self) -> float:
        items = self.list()
        return sum(item.amount for item in items) / len(items) if items else 0.0

    def max_amount(self) -> Optional[Charge]:
        """The record with the highest amount."""
        items = self.list()
        return max(items, key=lambda item: item.amount) if items else None

    def posted_before(self, day: str) -> List[Charge]:
        return self.where(lambda item: item.posted < day)

    def posted_after(self, day: str) -> List[Charge]:
        return self.where(lambda item: item.posted > day)

    def posted_on(self, day: str) -> List[Charge]:
        return self.where(lambda item: item.posted == day)

    def with_category(self, value: Any) -> List[Charge]:
        wanted = ChargeCategory(value)
        return self.where(lambda item: item.category == wanted)

    def count_by_category(self) -> Dict[str, int]:
        """How many records have each category."""
        counts = {member.value: 0 for member in ChargeCategory}
        for item in self.list():
            counts[ChargeCategory(item.category).value] += 1
        return counts
