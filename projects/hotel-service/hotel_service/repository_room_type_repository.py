"""Repository (continued)."""

from __future__ import annotations

import csv
import io
import json
import threading
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import (
    Booking,
    BookingStatus,
    Charge,
    ChargeCategory,
    Guest,
    Housekeeping,
    Room,
    RoomStatus,
    RoomType,
)

T = TypeVar("T")
from .repository_room_type_repository_part1 import *  # noqa: F401,F403


class RoomTypeRepository(RoomTypeRepositoryPart1):
    """All room types, with the lookups the services need (continued)."""

    def max_nightly_rate(self) -> Optional[RoomType]:
        """The record with the highest nightly rate."""
        items = self.list()
        return max(items, key=lambda item: item.nightly_rate) if items else None

    def where_smoking(self, flag: bool = True) -> List[RoomType]:
        return self.where(lambda item: item.smoking is flag)

    def search(self, text: str) -> List[RoomType]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
        )))
