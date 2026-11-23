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
from .repository_room_repository import *  # noqa: F401,F403


class GuestRepositoryPart1(Repository[Guest]):
    """All guests, with the lookups the services need."""

    model = Guest
    entity_name = "guest"

    def find_by_name(self, value: str) -> List[Guest]:
        """Records whose name is exactly `value`."""
        return self.where(lambda item: item.name == value)

    def search_name(self, text: str) -> List[Guest]:
        """Records whose name contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.name.lower())

    def find_by_email(self, value: str) -> List[Guest]:
        """Records whose email is exactly `value`."""
        return self.where(lambda item: item.email == value)

    def search_email(self, text: str) -> List[Guest]:
        """Records whose email contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.email.lower())

    def find_by_phone(self, value: str) -> List[Guest]:
        """Records whose phone is exactly `value`."""
        return self.where(lambda item: item.phone == value)

    def search_phone(self, text: str) -> List[Guest]:
        """Records whose phone contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.phone.lower())

    def find_by_country(self, value: str) -> List[Guest]:
        """Records whose country is exactly `value`."""
        return self.where(lambda item: item.country == value)

    def search_country(self, text: str) -> List[Guest]:
        """Records whose country contains `text` (any case)."""
        needle = text.strip().lower()
        return self.where(lambda item: needle in item.country.lower())

    def where_vip(self, flag: bool = True) -> List[Guest]:
        return self.where(lambda item: item.vip is flag)

    def between_loyalty_points(self, low: float, high: float) -> List[Guest]:
        """Records whose loyalty points is within [low, high]."""
        return self.where(lambda item: low <= item.loyalty_points <= high)

    def total_loyalty_points(self) -> float:
        return sum(item.loyalty_points for item in self.list())

    def average_loyalty_points(self) -> float:
        items = self.list()
        return sum(item.loyalty_points for item in items) / len(items) if items else 0.0

    def max_loyalty_points(self) -> Optional[Guest]:
        """The record with the highest loyalty points."""
        items = self.list()
        return max(items, key=lambda item: item.loyalty_points) if items else None
