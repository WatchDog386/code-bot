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
from .services_housekeeping_service import *  # noqa: F401,F403


def sample_guest(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new guest (refs point at seeded records)."""
    return {
        "name": f"Guest name {index}",
        "email": f"guest{index}@example.com",
        "phone": f"Guest phone {index}",
        "country": f"Guest country {index}",
        "vip": index % 2 == 1,
        "loyalty_points": index + 1,
    }
