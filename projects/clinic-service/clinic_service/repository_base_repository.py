"""Storage for the Clinic Scheduling service: one thread-safe in-memory repository per
model, with the lookups the services and the API need, and JSON / CSV import-export.
"""

from __future__ import annotations

import csv
import io
import json
import threading
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import (
    Appointment,
    AppointmentStatus,
    Doctor,
    DoctorSpecialty,
    Invoice,
    InvoiceStatus,
    LabResult,
    Patient,
    Prescription,
)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Records kept in memory, keyed by id. Subclasses set `model`."""

    model: Any = None
    entity_name = "record"

    def __init__(self) -> None:
        self._items: Dict[int, T] = {}
        self._next_id = 1
        self._lock = threading.RLock()

    def add(self, item: T) -> T:
        """Store a new record and give it the next id."""
        with self._lock:
            item.id = self._next_id  # type: ignore[attr-defined]
            self._next_id += 1
            self._items[item.id] = item  # type: ignore[attr-defined]
            return item

    def get(self, item_id: int) -> Optional[T]:
        with self._lock:
            return self._items.get(item_id)

    def list(self) -> List[T]:
        """Every record, oldest first."""
        with self._lock:
            return [self._items[key] for key in sorted(self._items)]

    def save(self, item: T) -> T:
        """Replace an existing record."""
        with self._lock:
            key = item.id  # type: ignore[attr-defined]
            if key not in self._items:
                raise KeyError(key)
            self._items[key] = item
            return item

    def remove(self, item_id: int) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None

    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._next_id = 1
