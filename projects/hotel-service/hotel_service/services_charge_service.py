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
from .services_charge_service_part1 import *  # noqa: F401,F403


class ChargeService(ChargeServicePart1):
    """Create, change and remove charges (continued)."""

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every charge."""
        return {
            "count": self.repo.count(),
            "total_amount": round(self.repo.total_amount(), 2),
            "average_amount": round(self.repo.average_amount(), 2),
            "by_category": self.repo.count_by_category(),
        }
