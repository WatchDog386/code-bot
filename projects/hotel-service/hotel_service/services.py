"""Services (continued)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from .models import (
    BOOKING_FIELDS,
    Booking,
    CHARGE_FIELDS,
    Charge,
    GUEST_FIELDS,
    Guest,
    HOUSEKEEPING_FIELDS,
    Housekeeping,
    ROOM_FIELDS,
    ROOM_TYPE_FIELDS,
    Room,
    RoomType,
    ValidationError,
)
from .repository import (
    RoomTypeRepository,
    RoomRepository,
    GuestRepository,
    BookingRepository,
    ChargeRepository,
    HousekeepingRepository,
)
from .services_sample_booking import *  # noqa: F401,F403


def sample_housekeeping(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new housekeeping (refs point at seeded records)."""
    return {
        "room_id": (index - 1) % 3 + 1,
        "cleaned": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "minutes": index + 1,
        "staff": f"Housekeeping staff {index}",
        "inspected": index % 2 == 1,
    }


class Services:
    """The whole service: storage plus one service object per model."""

    def __init__(self, store: Optional[Store] = None) -> None:
        self.store = store or Store()
        self.room_types = RoomTypeService(self.store)
        self.rooms = RoomService(self.store)
        self.guests = GuestService(self.store)
        self.bookings = BookingService(self.store)
        self.charges = ChargeService(self.store)
        self.housekeepings = HousekeepingService(self.store)

    def seed(self, count: int = 3) -> None:
        """Fill every repository with `count` sample records."""
        for index in range(1, count + 1):
            self.room_types.create(sample_room_type(index))
            self.rooms.create(sample_room(index))
            self.guests.create(sample_guest(index))
            self.bookings.create(sample_booking(index))
            self.charges.create(sample_charge(index))
            self.housekeepings.create(sample_housekeeping(index))

    def summary(self) -> Dict[str, Any]:
        return {
            "room_types": self.room_types.stats(),
            "rooms": self.rooms.stats(),
            "guests": self.guests.stats(),
            "bookings": self.bookings.stats(),
            "charges": self.charges.stats(),
            "housekeepings": self.housekeepings.stats(),
        }
