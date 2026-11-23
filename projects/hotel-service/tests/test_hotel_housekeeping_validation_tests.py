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


class HousekeepingValidationTests(unittest.TestCase):
    """Housekeeping: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.housekeepings
        self.repo = self.services.store.housekeepings

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_housekeeping(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_housekeeping(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_room_id(self) -> None:
        data = sample_housekeeping(12)
        data["room_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "room_id")

    def test_rejects_bad_cleaned(self) -> None:
        data = sample_housekeeping(12)
        data["cleaned"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "cleaned")

    def test_rejects_bad_minutes(self) -> None:
        data = sample_housekeeping(12)
        data["minutes"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "minutes")

    def test_rejects_bad_staff(self) -> None:
        data = sample_housekeeping(12)
        data["staff"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "staff")

    def test_rejects_bad_inspected(self) -> None:
        data = sample_housekeeping(12)
        data["inspected"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "inspected")
