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


class PrescriptionOperationTests(unittest.TestCase):
    """Prescription: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.prescriptions
        self.repo = self.services.store.prescriptions

    def test_search_drug(self) -> None:
        target = self.service.get(2).drug
        self.assertIn(self.service.get(2), self.repo.search_drug(target.upper()))
        self.assertEqual(len(self.repo.find_by_drug(target)), len([i for i in self.repo.list() if i.drug == target]))

    def test_adjust_dose_mg(self) -> None:
        before = self.service.get(1).dose_mg
        self.assertEqual(self.service.adjust_dose_mg(1, 2).dose_mg, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_dose_mg(1, -(before + 100))

    def test_adjust_times_per_day(self) -> None:
        before = self.service.get(1).times_per_day
        self.assertEqual(self.service.adjust_times_per_day(1, 2).times_per_day, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_times_per_day(1, -(before + 100))

    def test_adjust_days(self) -> None:
        before = self.service.get(1).days
        self.assertEqual(self.service.adjust_days(1, 2).days, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_days(1, -(before + 100))

    def test_adjust_refills(self) -> None:
        before = self.service.get(1).refills
        self.assertEqual(self.service.adjust_refills(1, 2).refills, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_refills(1, -(before + 100))

    def test_search_notes(self) -> None:
        target = self.service.get(2).notes
        self.assertIn(self.service.get(2), self.repo.search_notes(target.upper()))
        self.assertEqual(len(self.repo.find_by_notes(target)), len([i for i in self.repo.list() if i.notes == target]))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_prescription(20)["drug"]
        after = self.service.update(1, {"drug": new_value})
        self.assertEqual(after.drug, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_prescription(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)
