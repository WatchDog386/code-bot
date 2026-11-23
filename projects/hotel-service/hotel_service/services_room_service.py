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
from .services_room_service_part1 import *  # noqa: F401,F403


class RoomService(RoomServicePart1):
    """Create, change and remove rooms (continued)."""

    def toggle_sea_view(self, item_id: int) -> Room:
        item = self.get(item_id)
        return self.update(item_id, {"sea_view": not item.sea_view})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every room."""
        return {
            "count": self.repo.count(),
            "total_floor": round(self.repo.total_floor(), 2),
            "average_floor": round(self.repo.average_floor(), 2),
            "by_status": self.repo.count_by_status(),
            "sea_view": len(self.repo.where_sea_view(True)),
        }
