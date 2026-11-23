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


class RoomTypeOperationTests(unittest.TestCase):
    """RoomType: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.room_types
        self.repo = self.services.store.room_types

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_adjust_beds(self) -> None:
        before = self.service.get(1).beds
        self.assertEqual(self.service.adjust_beds(1, 2).beds, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_beds(1, -(before + 100))

    def test_adjust_max_guests(self) -> None:
        before = self.service.get(1).max_guests
        self.assertEqual(self.service.adjust_max_guests(1, 2).max_guests, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_max_guests(1, -(before + 100))

    def test_adjust_nightly_rate(self) -> None:
        before = self.service.get(1).nightly_rate
        self.assertAlmostEqual(self.service.adjust_nightly_rate(1, 1.5).nightly_rate, before + 1.5, places=2)

    def test_toggle_smoking(self) -> None:
        before = self.service.get(1).smoking
        self.assertEqual(self.service.toggle_smoking(1).smoking, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_room_type(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_room_type(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())
