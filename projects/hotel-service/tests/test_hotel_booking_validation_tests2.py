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


class BookingValidationTests2(unittest.TestCase):
    """Booking: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.bookings
        self.repo = self.services.store.bookings

    def test_rejects_bad_total(self) -> None:
        data = sample_booking(12)
        data["total"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "total")

    def test_rejects_bad_status(self) -> None:
        data = sample_booking(12)
        data["status"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "status")

    def test_rejects_bad_notes(self) -> None:
        data = sample_booking(12)
        data["notes"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "notes")

    def test_room_id_must_exist(self) -> None:
        data = sample_booking(13)
        data["room_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_guest_id_must_exist(self) -> None:
        data = sample_booking(13)
        data["guest_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
