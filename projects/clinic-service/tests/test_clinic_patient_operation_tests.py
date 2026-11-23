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


class PatientOperationTests(unittest.TestCase):
    """Patient: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.patients
        self.repo = self.services.store.patients

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

    def test_birth_date_ranges(self) -> None:
        day = self.service.get(2).birth_date
        total = len(self.repo.birth_date_before(day)) + len(self.repo.birth_date_on(day)) + len(self.repo.birth_date_after(day))
        self.assertEqual(total, self.repo.count())

    def test_search_insurance(self) -> None:
        target = self.service.get(2).insurance
        self.assertIn(self.service.get(2), self.repo.search_insurance(target.upper()))
        self.assertEqual(len(self.repo.find_by_insurance(target)), len([i for i in self.repo.list() if i.insurance == target]))

    def test_search_allergies(self) -> None:
        target = self.service.get(2).allergies
        self.assertIn(self.service.get(2), self.repo.search_allergies(target.upper()))
        self.assertEqual(len(self.repo.find_by_allergies(target)), len([i for i in self.repo.list() if i.allergies == target]))

    def test_toggle_active(self) -> None:
        before = self.service.get(1).active
        self.assertEqual(self.service.toggle_active(1).active, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_patient(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_patient(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)
