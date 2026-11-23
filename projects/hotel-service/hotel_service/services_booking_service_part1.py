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
from .services_guest_service import *  # noqa: F401,F403


class BookingServicePart1:
    """Create, change and remove bookings."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.bookings

    def create(self, data: Dict[str, Any]) -> Booking:
        """Validate and store a new booking."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Booking.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Booking:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("booking", item_id)
        return item

    def list(self, **filters: Any) -> List[Booking]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in BOOKING_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Booking:
        """Change some fields of a booking."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a booking nobody points at any more."""
        self.get(item_id)
        if self.store.charges.count_for_booking(item_id):
            raise Conflict(f"booking {item_id} is still used by charges")
        self.repo.remove(item_id)

    def _check_links(self, item: Booking) -> None:
        if self.store.rooms.get(item.room_id) is None:
            raise NotFound("room", item.room_id)
        if self.store.guests.get(item.guest_id) is None:
            raise NotFound("guest", item.guest_id)

    def adjust_guests(self, item_id: int, delta: int) -> Booking:
        """Add `delta` to the guests (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"guests": item.guests + delta})

    def adjust_total(self, item_id: int, delta: float) -> Booking:
        item = self.get(item_id)
        return self.update(item_id, {"total": round(item.total + delta, 2)})
