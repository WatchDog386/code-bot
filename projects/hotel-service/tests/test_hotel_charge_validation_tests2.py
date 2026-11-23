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


class ChargeValidationTests2(unittest.TestCase):
    """Charge: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.charges
        self.repo = self.services.store.charges

    def test_booking_id_must_exist(self) -> None:
        data = sample_charge(13)
        data["booking_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
