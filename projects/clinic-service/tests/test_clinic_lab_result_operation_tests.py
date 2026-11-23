"""Test clinic (continued)."""

import unittest

from clinic_service.api import Api
from clinic_service.models import ValidationError
from clinic_service.repository import (
    DoctorRepository,
    PatientRepository,
    AppointmentRepository,
    PrescriptionRepository,
    InvoiceRepository,
    LabResultRepository,
)
from clinic_service.services import (
    Conflict,
    NotFound,
    Services,
    sample_doctor,
    sample_patient,
    sample_appointment,
    sample_prescription,
    sample_invoice,
    sample_lab_result,
)


class LabResultOperationTests(unittest.TestCase):
    """LabResult: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.lab_results
        self.repo = self.services.store.lab_results

    def test_search_test_name(self) -> None:
        target = self.service.get(2).test_name
        self.assertIn(self.service.get(2), self.repo.search_test_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_test_name(target)), len([i for i in self.repo.list() if i.test_name == target]))

    def test_adjust_value(self) -> None:
        before = self.service.get(1).value
        self.assertAlmostEqual(self.service.adjust_value(1, 1.5).value, before + 1.5, places=2)

    def test_search_unit(self) -> None:
        target = self.service.get(2).unit
        self.assertIn(self.service.get(2), self.repo.search_unit(target.upper()))
        self.assertEqual(len(self.repo.find_by_unit(target)), len([i for i in self.repo.list() if i.unit == target]))

    def test_taken_ranges(self) -> None:
        day = self.service.get(2).taken
        total = len(self.repo.taken_before(day)) + len(self.repo.taken_on(day)) + len(self.repo.taken_after(day))
        self.assertEqual(total, self.repo.count())

    def test_toggle_flagged(self) -> None:
        before = self.service.get(1).flagged
        self.assertEqual(self.service.toggle_flagged(1).flagged, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_lab_result(20)["test_name"]
        after = self.service.update(1, {"test_name": new_value})
        self.assertEqual(after.test_name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_lab_result(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = LabResultRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)
