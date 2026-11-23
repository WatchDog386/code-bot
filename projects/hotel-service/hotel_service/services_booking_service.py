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
from .services_booking_service_part1 import *  # noqa: F401,F403


class BookingService(BookingServicePart1):
    """Create, change and remove bookings (continued)."""

    def set_status(self, item_id: int, value: Any) -> Booking:
        """Move a booking to another status."""
        return self.update(item_id, {"status": value})

    def stats(self) -> Dict[str, Any]:
        """Totals and breakdowns over every booking."""
        return {
            "count": self.repo.count(),
            "total_guests": round(self.repo.total_guests(), 2),
            "average_guests": round(self.repo.average_guests(), 2),
            "total_total": round(self.repo.total_total(), 2),
            "average_total": round(self.repo.average_total(), 2),
            "by_status": self.repo.count_by_status(),
        }
