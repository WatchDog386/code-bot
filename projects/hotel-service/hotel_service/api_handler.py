"""Api (continued)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .models import (
    BOOKING_SORTABLE,
    BookingStatus,
    CHARGE_SORTABLE,
    ChargeCategory,
    GUEST_SORTABLE,
    HOUSEKEEPING_SORTABLE,
    ROOM_SORTABLE,
    ROOM_TYPE_SORTABLE,
    RoomStatus,
    ValidationError,
    check_choice,
    check_date,
)
from .services import Conflict, NotFound, Services

Response = Tuple[int, Any]
Query = Dict[str, str]
from .api_api import *  # noqa: F401,F403


class Handler(BaseHTTPRequestHandler):
    """Turns HTTP requests into `Api.handle` calls."""

    api = Api()

    def _respond(self, status: int, payload: Any) -> None:
        data = b"" if payload is None else json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self, method: str) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = None
        if length:
            try:
                body = json.loads(self.rfile.read(length))
            except ValueError:
                self._respond(400, {"error": "invalid JSON"})
                return
        status, payload = self.api.handle(method, self.path, body)
        self._respond(status, payload)

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    def do_PATCH(self) -> None:  # noqa: N802
        self._dispatch("PATCH")

    def do_PUT(self) -> None:  # noqa: N802
        self._dispatch("PUT")

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch("DELETE")
