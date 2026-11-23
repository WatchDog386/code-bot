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


class BookingOperationTests(unittest.TestCase):
    """Booking: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.bookings
        self.repo = self.services.store.bookings

    def test_check_in_ranges(self) -> None:
        day = self.service.get(2).check_in
        total = len(self.repo.check_in_before(day)) + len(self.repo.check_in_on(day)) + len(self.repo.check_in_after(day))
        self.assertEqual(total, self.repo.count())

    def test_check_out_ranges(self) -> None:
        day = self.service.get(2).check_out
        total = len(self.repo.check_out_before(day)) + len(self.repo.check_out_on(day)) + len(self.repo.check_out_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_guests(self) -> None:
        before = self.service.get(1).guests
        self.assertEqual(self.service.adjust_guests(1, 2).guests, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_guests(1, -(before + 100))

    def test_adjust_total(self) -> None:
        before = self.service.get(1).total
        self.assertAlmostEqual(self.service.adjust_total(1, 1.5).total, before + 1.5, places=2)

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "cancelled")
        self.assertEqual(item.status.value, "cancelled")
        self.assertEqual(self.repo.count_by_status()["cancelled"], len(self.repo.with_status("cancelled")))

    def test_search_notes(self) -> None:
        target = self.service.get(2).notes
        self.assertIn(self.service.get(2), self.repo.search_notes(target.upper()))
        self.assertEqual(len(self.repo.find_by_notes(target)), len([i for i in self.repo.list() if i.notes == target]))

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_booking(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())
