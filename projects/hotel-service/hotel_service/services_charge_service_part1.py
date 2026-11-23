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
from .services_booking_service import *  # noqa: F401,F403


class ChargeServicePart1:
    """Create, change and remove charges."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self.repo = store.charges

    def create(self, data: Dict[str, Any]) -> Charge:
        """Validate and store a new charge."""
        if "id" in data:
            raise ValidationError("id", "is assigned automatically")
        item = Charge.from_dict(data).validate()
        self._check_links(item)
        return self.repo.add(item)

    def get(self, item_id: int) -> Charge:
        item = self.repo.get(item_id)
        if item is None:
            raise NotFound("charge", item_id)
        return item

    def list(self, **filters: Any) -> List[Charge]:
        """Records whose fields equal the given values (as query-string text)."""
        items = self.repo.list()
        for key, value in filters.items():
            if key not in CHARGE_FIELDS:
                raise ValidationError(key, "is not a field you can filter on")
            items = [item for item in items if plain(getattr(item, key)) == plain(value)]
        return items

    def update(self, item_id: int, changes: Dict[str, Any]) -> Charge:
        """Change some fields of a charge."""
        updated = self.get(item_id).apply(changes)
        self._check_links(updated)
        return self.repo.save(updated)

    def delete(self, item_id: int) -> None:
        """Remove a charge nobody points at any more."""
        self.get(item_id)
        self.repo.remove(item_id)

    def _check_links(self, item: Charge) -> None:
        if self.store.bookings.get(item.booking_id) is None:
            raise NotFound("booking", item.booking_id)

    def adjust_amount(self, item_id: int, delta: float) -> Charge:
        item = self.get(item_id)
        return self.update(item_id, {"amount": round(item.amount + delta, 2)})

    def set_category(self, item_id: int, value: Any) -> Charge:
        """Move a charge to another category."""
        return self.update(item_id, {"category": value})
