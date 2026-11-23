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
from .repository_guest_repository_part1 import *  # noqa: F401,F403


class GuestRepository(GuestRepositoryPart1):
    """All guests, with the lookups the services need (continued)."""

    def search(self, text: str) -> List[Guest]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.name,
            item.email,
            item.phone,
            item.country,
        )))
