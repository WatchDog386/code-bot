"""Tests for the Hotel Reservations service (run: python -m unittest discover -s tests -t .)."""

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


class RoomTypeTests(unittest.TestCase):
    """RoomType: creating and reading."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.room_types
        self.repo = self.services.store.room_types

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_room_type(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)
