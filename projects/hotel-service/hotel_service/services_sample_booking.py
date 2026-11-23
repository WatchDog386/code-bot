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
from .services_sample_guest import *  # noqa: F401,F403


def sample_booking(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new booking (refs point at seeded records)."""
    return {
        "room_id": (index - 1) % 3 + 1,
        "guest_id": (index - 1) % 3 + 1,
        "check_in": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "check_out": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "guests": index + 1,
        "total": round(10.0 * index + 0.99, 2),
        "status": ['pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled'][index % 5],
        "notes": f"Notes about booking {index}.",
    }


def sample_charge(index: int = 1) -> Dict[str, Any]:
    """Valid data for a new charge (refs point at seeded records)."""
    return {
        "booking_id": (index - 1) % 3 + 1,
        "description": f"Charge description {index}",
        "amount": round(10.0 * index + 0.99, 2),
        "posted": f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}",
        "category": ['minibar', 'restaurant', 'spa', 'laundry', 'other'][index % 5],
    }
