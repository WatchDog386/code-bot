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


class HousekeepingApiTests(unittest.TestCase):
    """Housekeeping: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.housekeepings
        self.repo = self.services.store.housekeepings

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/housekeepings", sample_housekeeping(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/housekeepings/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/housekeepings?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/housekeepings/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/housekeepings/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/housekeepings/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/housekeepings", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/housekeepings?sort=nope")[0], 400)


if __name__ == "__main__":
    unittest.main()
