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


class HousekeepingOperationTests(unittest.TestCase):
    """Housekeeping: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.housekeepings
        self.repo = self.services.store.housekeepings

    def test_cleaned_ranges(self) -> None:
        day = self.service.get(2).cleaned
        total = len(self.repo.cleaned_before(day)) + len(self.repo.cleaned_on(day)) + len(self.repo.cleaned_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_minutes(self) -> None:
        before = self.service.get(1).minutes
        self.assertEqual(self.service.adjust_minutes(1, 2).minutes, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_minutes(1, -(before + 100))

    def test_search_staff(self) -> None:
        target = self.service.get(2).staff
        self.assertIn(self.service.get(2), self.repo.search_staff(target.upper()))
        self.assertEqual(len(self.repo.find_by_staff(target)), len([i for i in self.repo.list() if i.staff == target]))

    def test_toggle_inspected(self) -> None:
        before = self.service.get(1).inspected
        self.assertEqual(self.service.toggle_inspected(1).inspected, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_housekeeping(20)["staff"]
        after = self.service.update(1, {"staff": new_value})
        self.assertEqual(after.staff, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_housekeeping(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = HousekeepingRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)
