"""Business rules for the Hotel Reservations service: validation, links between records
(a record can't point at something that doesn't exist, and can't be deleted while
others still point at it), small domain operations and statistics.
"""

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


class NotFound(LookupError):
    """No record with that id."""

    def __init__(self, entity: str, item_id: int) -> None:
        super().__init__(f"{entity} {item_id} not found")
        self.entity = entity
        self.item_id = item_id


class Conflict(ValueError):
    """The change would break a link between records."""


def plain(value: Any) -> str:
    """A value as the text a query string would carry."""
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class Store:
    """Every repository of the service."""

    def __init__(self) -> None:
        self.room_types = RoomTypeRepository()
        self.rooms = RoomRepository()
        self.guests = GuestRepository()
        self.bookings = BookingRepository()
        self.charges = ChargeRepository()
        self.housekeepings = HousekeepingRepository()

    def counts(self) -> Dict[str, int]:
        return {
            "room_types": self.room_types.count(),
            "rooms": self.rooms.count(),
            "guests": self.guests.count(),
            "bookings": self.bookings.count(),
            "charges": self.charges.count(),
            "housekeepings": self.housekeepings.count(),
        }
