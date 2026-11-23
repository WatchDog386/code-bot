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


class RoomValidationTests(unittest.TestCase):
    """Room: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.rooms
        self.repo = self.services.store.rooms

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_room(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_room(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_room_type_id(self) -> None:
        data = sample_room(12)
        data["room_type_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "room_type_id")

    def test_rejects_bad_number(self) -> None:
        data = sample_room(12)
        data["number"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "number")

    def test_rejects_bad_floor(self) -> None:
        data = sample_room(12)
        data["floor"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "floor")

    def test_rejects_bad_status(self) -> None:
        data = sample_room(12)
        data["status"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "status")

    def test_rejects_bad_sea_view(self) -> None:
        data = sample_room(12)
        data["sea_view"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "sea_view")
