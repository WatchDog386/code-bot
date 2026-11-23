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
from .services_housekeeping_service_part1 import *  # noqa: F401,F403


class HousekeepingService(HousekeepingServicePart1):
    """Create, change and remove housekeepings (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every housekeeping."""
        return {
            "count": self.repo.count(),
            "total_minutes": round(self.repo.total_minutes(), 2),
            "average_minutes": round(self.repo.average_minutes(), 2),
            "inspected": len(self.repo.where_inspected(True)),
        }


def sample_room_type(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new room type (refs point at seeded records)."""
    return {
        "name": f"Room type name {index}",
        "beds": index + 1,
        "max_guests": index + 1,
        "nightly_rate": round(10.0 * index + 0.99, 2),
        "smoking": index % 2 == 1,
    }


def sample_room(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new room (refs point at seeded records)."""
    return {
        "room_type_id": (index - 1) % 3 + 1,
        "number": f"Room number {index}",
        "floor": index + 1,
        "status": ['clean', 'dirty', 'occupied', 'maintenance'][index % 4],
        "sea_view": index % 2 == 1,
    }
