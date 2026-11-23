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
from .services_room_type_service import *  # noqa: F401,F403


class RoomServicePart1:
    """Create, change and remove rooms."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.rooms

    def create(self, data: Dict[str, Any]) -> Room:
        """Validate and store a new room."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Room.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Room:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("room", item_id)
        return item

    def list(self, **filters: Any) -> List[Room]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ROOM_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Room:
        """Change some fields of a room."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a room nobody points at any more."""
        self.get(item_id)
        if self.store.bookings.count_for_room(item_id):
            raise Conflict(f"room {item_id} is still used by bookings")
        if self.store.housekeepings.count_for_room(item_id):
            raise Conflict(f"room {item_id} is still used by housekeepings")
        self.repo.remove(item_id)

    def _check_links(self, item: Room) -> None:
        if self.store.room_types.get(item.room_type_id) is None:
            raise NotFound("room type", item.room_type_id)

    def adjust_floor(self, item_id: int, delta: int) -> Room:
        """Add `delta` to the floor (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"floor": item.floor + delta})

    def set_status(self, item_id: int, value: Any) -> Room:
        """Move a room to another status."""
        return self.update(item_id, {"status": value})
