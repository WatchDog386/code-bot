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
from .services_room_type_service_part1 import *  # noqa: F401,F403


class RoomTypeService(RoomTypeServicePart1):
    """Create, change and remove room types (continued)."""

    def adjust_nightly_rate(self, item_id: int, delta: float) -> RoomType:
        item = self.get(item_id)
        return self.update(item_id, {"nightly_rate": round(item.nightly_rate + delta, 2)})

    def toggle_smoking(self, item_id: int) -> RoomType:
        item = self.get(item_id)
        return self.update(item_id, {"smoking": not item.smoking})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every room type."""
        return {
            "count": self.repo.count(),
            "total_beds": round(self.repo.total_beds(), 2),
            "average_beds": round(self.repo.average_beds(), 2),
            "total_max_guests": round(self.repo.total_max_guests(), 2),
            "average_max_guests": round(self.repo.average_max_guests(), 2),
            "total_nightly_rate": round(self.repo.total_nightly_rate(), 2),
            "average_nightly_rate": round(self.repo.average_nightly_rate(), 2),
            "smoking": len(self.repo.where_smoking(True)),
        }
