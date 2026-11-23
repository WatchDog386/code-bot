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
from .services_not_found import *  # noqa: F401,F403


class RoomTypeServicePart1:
    """Create, change and remove room types."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.room_types

    def create(self, data: Dict[str, Any]) -> RoomType:
        """Validate and store a new room type."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = RoomType.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> RoomType:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("room type", item_id)
        return item

    def list(self, **filters: Any) -> List[RoomType]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in ROOM_TYPE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> RoomType:
        """Change some fields of a room type."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a room type nobody points at any more."""
        self.get(item_id)
        if self.store.rooms.count_for_room_type(item_id):
            raise Conflict(f"room type {item_id} is still used by rooms")
        self.repo.remove(item_id)

    def _check_links(self, item: RoomType) -> None:
        """RoomType doesn't point at other records."""
        return None

    def adjust_beds(self, item_id: int, delta: int) -> RoomType:
        """Add `delta` to the beds (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"beds": item.beds + delta})

    def adjust_max_guests(self, item_id: int, delta: int) -> RoomType:
        """Add `delta` to the max guests (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"max_guests": item.max_guests + delta})
