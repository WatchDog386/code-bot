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
from .repository_base_repository import *  # noqa: F401,F403


class Repository(BaseRepository[T]):
    """Records with lookups, paging and JSON / CSV export."""

    def where(self, keep: Callable[[T], bool]) -> List[T]:
        """Records for which `keep(record)` is true."""
        return [item for item in self.list() if keep(item)]

    def first(self, keep: Callable[[T], bool]) -> Optional[T]:
        for item in self.list():
            if keep(item):
                return item
        return None

    def page(self, number: int = 1, size: int = 20) -> List[T]:
        """One page of records (pages start at 1)."""
        start = max(0, (number - 1) * size)
        return self.list()[start:start + size]

    def sorted_by(self, field_name: str, reverse: bool = False) -> List[T]:
        return sorted(self.list(), key=lambda item: getattr(item, field_name), reverse=reverse)

    def to_json(self) -> str:
        return json.dumps([item.to_dict() for item in self.list()], indent=2)  # type: ignore[attr-defined]

    def load_json(self, text: str) -> int:
        """Load records exported with `to_json()`; returns how many."""
        rows = json.loads(text)
        with self._lock:
            for row in rows:
                item = self.model.from_dict(row).validate()
                self._items[item.id] = item
                self._next_id = max(self._next_id, item.id + 1)
        return len(rows)

    def to_csv(self) -> str:
        """Every record as CSV with a header row."""
        names = ["id"] + [name for name in self.model.__dataclass_fields__ if name != "id"]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=names, lineterminator="\n")
        writer.writeheader()
        for item in self.list():
            writer.writerow(item.to_dict())  # type: ignore[attr-defined]
        return buffer.getvalue()
