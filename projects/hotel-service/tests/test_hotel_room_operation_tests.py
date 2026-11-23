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


class RoomOperationTests(unittest.TestCase):
    """Room: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.rooms
        self.repo = self.services.store.rooms

    def test_search_number(self) -> None:
        target = self.service.get(2).number
        self.assertIn(self.service.get(2), self.repo.search_number(target.upper()))
        self.assertEqual(len(self.repo.find_by_number(target)), len([i for i in self.repo.list() if i.number == target]))

    def test_adjust_floor(self) -> None:
        before = self.service.get(1).floor
        self.assertEqual(self.service.adjust_floor(1, 2).floor, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_floor(1, -(before + 100))

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "maintenance")
        self.assertEqual(item.status.value, "maintenance")
        self.assertEqual(self.repo.count_by_status()["maintenance"], len(self.repo.with_status("maintenance")))

    def test_toggle_sea_view(self) -> None:
        before = self.service.get(1).sea_view
        self.assertEqual(self.service.toggle_sea_view(1).sea_view, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_room(20)["number"]
        after = self.service.update(1, {"number": new_value})
        self.assertEqual(after.number, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_room(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = RoomRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)
