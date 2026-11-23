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
from .repository_charge_repository import *  # noqa: F401,F403


class HousekeepingRepository(Repository[Housekeeping]):
    """All housekeepings, with the lookups the services need."""

    model = Housekeeping
    entity_name = "housekeeping"

    def for_room(self, room_id: int) -> List[Housekeeping]:
        """Records linked to room `room_id`."""
        return self.where(lambda item: item.room_id == room_id)

    def count_for_room(self, room_id: int) -> int:
        return len(self.for_room(room_id))

    def cleaned_before(self, day: str) -> List[Housekeeping]:
        return self.where(lambda item: item.cleaned < day)

    def cleaned_after(self, day: str) -> List[Housekeeping]:
        return self.where(lambda item: item.cleaned > day)

    def cleaned_on(self, day: str) -> List[Housekeeping]:
        return self.where(lambda item: item.cleaned == day)

    def between_minutes(self, low: float, high: float) -> List[Housekeeping]:
        """Records whose minutes is within [low, high]."""
        return self.where(lambda item: low <= item.minutes <= high)

    def total_minutes(self) -> float:
        return sum(item.minutes for item in self.list())

    def average_minutes(self) -> float:
        items = self.list()
        return sum(item.minutes for item in items) / len(items) if items else 0.0

    def max_minutes(self) -> Optional[Housekeeping]:
        """The record with the highest minutes."""
        items = self.list()
        return max(items, key=lambda item: item.minutes) if items else None

    def find_by_staff(self, value: str) -> List[Housekeeping]:
        """Records whose staff is exactly `value`."""
        return self.where(lambda item: item.staff == value)

    def search_staff(self, text: str) -> List[Housekeeping]:
        """Records whose staff contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.staff.lower())

    def where_inspected(self, flag: bool = True) -> List[Housekeeping]:
        return self.where(lambda item: item.inspected is flag)

    def search(self, text: str) -> List[Housekeeping]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.staff,
        )))
