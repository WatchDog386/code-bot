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
from .repository_charge_repository_part1 import *  # noqa: F401,F403


class ChargeRepository(ChargeRepositoryPart1):
    """All charges, with the lookups the services need (continued)."""

    def search(self, text: str) -> List[Charge]:
        """Records where any text field contains `text`."""
        needle = text.strip().lower()
        return self.where(lambda item: any(needle in value.lower() for value in (
            item.description,
        )))
