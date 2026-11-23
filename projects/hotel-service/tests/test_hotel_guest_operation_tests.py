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


class GuestOperationTests(unittest.TestCase):
    """Guest: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.guests
        self.repo = self.services.store.guests

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_search_email(self) -> None:
        target = self.service.get(2).email
        self.assertIn(self.service.get(2), self.repo.search_email(target.upper()))
        self.assertEqual(len(self.repo.find_by_email(target)), len([i for i in self.repo.list() if i.email == target]))

    def test_search_phone(self) -> None:
        target = self.service.get(2).phone
        self.assertIn(self.service.get(2), self.repo.search_phone(target.upper()))
        self.assertEqual(len(self.repo.find_by_phone(target)), len([i for i in self.repo.list() if i.phone == target]))

    def test_search_country(self) -> None:
        target = self.service.get(2).country
        self.assertIn(self.service.get(2), self.repo.search_country(target.upper()))
        self.assertEqual(len(self.repo.find_by_country(target)), len([i for i in self.repo.list() if i.country == target]))

    def test_toggle_vip(self) -> None:
        before = self.service.get(1).vip
        self.assertEqual(self.service.toggle_vip(1).vip, not before)

    def test_adjust_loyalty_points(self) -> None:
        before = self.service.get(1).loyalty_points
        self.assertEqual(self.service.adjust_loyalty_points(1, 2).loyalty_points, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_loyalty_points(1, -(before + 100))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_guest(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_guest(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)
