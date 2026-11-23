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
from .services_room_service import *  # noqa: F401,F403


class GuestServicePart1:
    """Create, change and remove guests."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.guests

    def create(self, data: Dict[str, Any]) -> Guest:
        """Validate and store a new guest."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Guest.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Guest:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("guest", item_id)
        return item

    def list(self, **filters: Any) -> List[Guest]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in GUEST_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Guest:
        """Change some fields of a guest."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a guest nobody points at any more."""
        self.get(item_id)
        if self.store.bookings.count_for_guest(item_id):
            raise Conflict(f"guest {item_id} is still used by bookings")
        self.repo.remove(item_id)

    def _check_links(self, item: Guest) -> None:
        """Guest doesn't point at other records."""
        return None

    def toggle_vip(self, item_id: int) -> Guest:
        item = self.get(item_id)
        return self.update(item_id, {"vip": not item.vip})

    def adjust_loyalty_points(self, item_id: int, delta: int) -> Guest:
        """Add `delta` to the loyalty points (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"loyalty_points": item.loyalty_points + delta})
