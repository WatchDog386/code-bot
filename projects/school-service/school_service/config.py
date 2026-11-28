"""Environment based settings for the School Records API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    seed_size: int = 3

    @classmethod
    def from_env(cls, environ: Optional[Mapping[str, str]] = None) -> "Settings":
        """Load validated settings, using an explicit mapping in tests when supplied."""
        values = os.environ if environ is None else environ
        host = values.get("SCHOOL_HOST", "127.0.0.1").strip()
        if not host:
            raise ValueError("SCHOOL_HOST must not be empty")
        port = _integer(values, "SCHOOL_PORT", 8000, 1, 65535)
        seed_size = _integer(values, "SCHOOL_SEED_SIZE", 3, 0, 1000)
        return cls(host=host, port=port, seed_size=seed_size)


def _integer(values: Mapping[str, str], key: str, default: int, low: int, high: int) -> int:
    raw = values.get(key, str(default))
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be a whole number") from None
    if not low <= value <= high:
        raise ValueError(f"{key} must be between {low} and {high}")
    return value
