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
from .repository_room_type_repository import *  # noqa: F401,F403


class RoomRepository(Repository[Room]):
    """All rooms, with the lookups the services need."""

    model = Room
    entity_name = "room"

    def for_room_type(self, room_type_id: int) -> List[Room]:
        """Records linked to room type `room_type_id`."""
        return self.where(lambda item: item.room_type_id == room_type_id)

    def count_for_room_type(self, room_type_id: int) -> int:
        return len(self.for_room_type(room_type_id))

    def find_by_number(self, value: str) -> List[Room]:
        """Records whose number is exactly `value`."""
        return self.where(lambda item: item.number == value)

    def search_number(self, text: str) -> List[Room]:
        """Records whose number contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.number.lower())

    def between_floor(self, low: float, high: float) -> List[Room]:
        """Records whose floor is within [low, high]."""
        return self.where(lambda item: low <= item.floor <= high)

    def total_floor(self) -> float:
        return sum(item.floor for item in self.list())

    def average_floor(self) -> float:
        items = self.list()
        return sum(item.floor for item in items) / len(items) if items else 0.0

    def max_floor(self) -> Optional[Room]:
        """The record with the highest floor."""
        items = self.list()
        return max(items, key=lambda item: item.floor) if items else None

    def with_status(self, value: Any) -> List[Room]:
        wanted = RoomStatus(value)
        return self.where(lambda item: item.status == wanted)

    def count_by_status(self) -> Dict[str, int]:
        """How many records have each status."""
        counts = {member.value: 0 for member in RoomStatus}
        for item in self.list():
            counts[RoomStatus(item.status).value] += 1
        return counts

    def where_sea_view(self, flag: bool = True) -> List[Room]:
        return self.where(lambda item: item.sea_view is flag)

    def search(self, text: str) -> List[Room]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.number,
        )))
