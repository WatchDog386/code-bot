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
from .services_charge_service import *  # noqa: F401,F403


class HousekeepingServicePart1:
    """Create, change and remove housekeepings."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.housekeepings

    def create(self, data: Dict[str, Any]) -> Housekeeping:
        """Validate and store a new housekeeping."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Housekeeping.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Housekeeping:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("housekeeping", item_id)
        return item

    def list(self, **filters: Any) -> List[Housekeeping]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in HOUSEKEEPING_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Housekeeping:
        """Change some fields of a housekeeping."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a housekeeping nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Housekeeping) -> None:
        if self.store.rooms.get(item.room_id) is None:
            raise NotFound("room", item.room_id)

    def adjust_minutes(self, item_id: int, delta: int) -> Housekeeping:
        """Add `delta` to the minutes (it can't go below zero)."""
        item = self.get(item_id)
        return self.update(item_id, {"minutes": item.minutes + delta})

    def toggle_inspected(self, item_id: int) -> Housekeeping:
        item = self.get(item_id)
        return self.update(item_id, {"inspected": not item.inspected})
