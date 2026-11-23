"""Test hotel (continued)."""

import unittest

from hotel_service.api import Api
from hotel_service.models import ValidationError
from hotel_service.repository import (
    RoomTypeRepository,
    RoomRepository,
    GuestRepository,
    BookingRepository,
    ChargeRepository,
    HousekeepingRepository,
)
from hotel_service.services import (
    Conflict,
    NotFound,
    Services,
    sample_room_type,
    sample_room,
    sample_guest,
    sample_booking,
    sample_charge,
    sample_housekeeping,
)


class GuestApiTests(unittest.TestCase):
    """Guest: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.guests
        self.repo = self.services.store.guests

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/guests", sample_guest(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/guests/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/guests?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/guests/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/guests/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/guests/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/guests", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/guests?sort=nope")[0], 400)


class BookingTests(unittest.TestCase):
    """Booking: creating and reading."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.bookings
        self.repo = self.services.store.bookings

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_booking(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)
