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
from .repository_guest_repository import *  # noqa: F401,F403


class BookingRepositoryPart1(Repository[Booking]):
    """All bookings, with the lookups the services need."""

    model = Booking
    entity_name = "booking"

    def for_room(self, room_id: int) -> List[Booking]:
        """Records linked to room `room_id`."""
        return self.where(lambda item: item.room_id == room_id)

    def count_for_room(self, room_id: int) -> int:
        return len(self.for_room(room_id))

    def for_guest(self, guest_id: int) -> List[Booking]:
        """Records linked to guest `guest_id`."""
        return self.where(lambda item: item.guest_id == guest_id)

    def count_for_guest(self, guest_id: int) -> int:
        return len(self.for_guest(guest_id))

    def check_in_before(self, day: str) -> List[Booking]:
        return self.where(lambda item: item.check_in < day)

    def check_in_after(self, day: str) -> List[Booking]:
        return self.where(lambda item: item.check_in > day)

    def check_in_on(self, day: str) -> List[Booking]:
        return self.where(lambda item: item.check_in == day)

    def check_out_before(self, day: str) -> List[Booking]:
        return self.where(lambda item: item.check_out < day)

    def check_out_after(self, day: str) -> List[Booking]:
        return self.where(lambda item: item.check_out > day)

    def check_out_on(self, day: str) -> List[Booking]:
        return self.where(lambda item: item.check_out == day)

    def between_guests(self, low: float, high: float) -> List[Booking]:
        """Records whose guests is within [low, high]."""
        return self.where(lambda item: low <= item.guests <= high)

    def total_guests(self) -> float:
        return sum(item.guests for item in self.list())

    def average_guests(self) -> float:
        items = self.list()
        return sum(item.guests for item in items) / len(items) if items else 0.0

    def max_guests(self) -> Optional[Booking]:
        """The record with the highest guests."""
        items = self.list()
        return max(items, key=lambda item: item.guests) if items else None

    def between_total(self, low: float, high: float) -> List[Booking]:
        """Records whose total is within [low, high]."""
        return self.where(lambda item: low <= item.total <= high)

    def total_total(self) -> float:
        return sum(item.total for item in self.list())
