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


class ChargeOperationTests(unittest.TestCase):
    """Charge: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.charges
        self.repo = self.services.store.charges

    def test_search_description(self) -> None:
        target = self.service.get(2).description
        self.assertIn(self.service.get(2), self.repo.search_description(target.upper()))
        self.assertEqual(len(self.repo.find_by_description(target)), len([i for i in self.repo.list() if i.description == target]))

    def test_adjust_amount(self) -> None:
        before = self.service.get(1).amount
        self.assertAlmostEqual(self.service.adjust_amount(1, 1.5).amount, before + 1.5, places=2)

    def test_posted_ranges(self) -> None:
        day = self.service.get(2).posted
        total = len(self.repo.posted_before(day)) + len(self.repo.posted_on(day)) + len(self.repo.posted_after(day))
        self.assertEqual(total, self.repo.count())

    def test_set_category(self) -> None:
        item = self.service.set_category(1, "other")
        self.assertEqual(item.category.value, "other")
        self.assertEqual(self.repo.count_by_category()["other"], len(self.repo.with_category("other")))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_charge(20)["description"]
        after = self.service.update(1, {"description": new_value})
        self.assertEqual(after.description, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_charge(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = ChargeRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)
