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
from .repository_repository import *  # noqa: F401,F403


class RoomTypeRepositoryPart1(Repository[RoomType]):
    """All room types, with the lookups the services need."""

    model = RoomType
    entity_name = "room_type"

    def find_by_name(self, value: str) -> List[RoomType]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[RoomType]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def between_beds(self, low: float, high: float) -> List[RoomType]:
        """Records whose beds is within [low, high]."""
        return self.where(lambda item: low <= item.beds <= high)

    def total_beds(self) -> float:
        return sum(item.beds for item in self.list())

    def average_beds(self) -> float:
        items = self.list()
        return sum(item.beds for item in items) / len(items) if items else 0.0

    def max_beds(self) -> Optional[RoomType]:
        """The record with the highest beds."""
        items = self.list()
        return max(items, key=lambda item: item.beds) if items else None

    def between_max_guests(self, low: float, high: float) -> List[RoomType]:
        """Records whose max guests is within [low, high]."""
        return self.where(lambda item: low <= item.max_guests <= high)

    def total_max_guests(self) -> float:
        return sum(item.max_guests for item in self.list())

    def average_max_guests(self) -> float:
        items = self.list()
        return sum(item.max_guests for item in items) / len(items) if items else 0.0

    def max_max_guests(self) -> Optional[RoomType]:
        """The record with the highest max guests."""
        items = self.list()
        return max(items, key=lambda item: item.max_guests) if items else None

    def between_nightly_rate(self, low: float, high: float) -> List[RoomType]:
        """Records whose nightly rate is within [low, high]."""
        return self.where(lambda item: low <= item.nightly_rate <= high)

    def total_nightly_rate(self) -> float:
        return sum(item.nightly_rate for item in self.list())

    def average_nightly_rate(self) -> float:
        items = self.list()
        return sum(item.nightly_rate for item in items) / len(items) if items else 0.0
