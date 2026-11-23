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


class RoomTypeValidationTests(unittest.TestCase):
    """RoomType: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.room_types
        self.repo = self.services.store.room_types

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_room_type(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_room_type(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_name(self) -> None:
        data = sample_room_type(12)
        data["name"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "name")

    def test_rejects_bad_beds(self) -> None:
        data = sample_room_type(12)
        data["beds"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "beds")

    def test_rejects_bad_max_guests(self) -> None:
        data = sample_room_type(12)
        data["max_guests"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "max_guests")

    def test_rejects_bad_nightly_rate(self) -> None:
        data = sample_room_type(12)
        data["nightly_rate"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "nightly_rate")

    def test_rejects_bad_smoking(self) -> None:
        data = sample_room_type(12)
        data["smoking"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "smoking")
