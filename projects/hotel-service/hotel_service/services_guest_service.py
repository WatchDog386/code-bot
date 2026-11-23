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
from .services_guest_service_part1 import *  # noqa: F401,F403


class GuestService(GuestServicePart1):
    """Create, change and remove guests (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every guest."""
        return {
            "count": self.repo.count(),
            "vip": len(self.repo.where_vip(True)),
            "total_loyalty_points": round(self.repo.total_loyalty_points(), 2),
            "average_loyalty_points": round(self.repo.average_loyalty_points(), 2),
        }
