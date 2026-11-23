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


class DoctorOperationTests(unittest.TestCase):
    """Doctor: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.doctors
        self.repo = self.services.store.doctors

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_search_email(self) -> None:
        target = self.service.get(2).email
        self.assertIn(self.service.get(2), self.repo.search_email(target.upper()))
        self.assertEqual(len(self.repo.find_by_email(target)), len([i for i in self.repo.list() if i.email == target]))

    def test_set_specialty(self) -> None:
        item = self.service.set_specialty(1, "orthopedics")
        self.assertEqual(item.specialty.value, "orthopedics")
        self.assertEqual(self.repo.count_by_specialty()["orthopedics"], len(self.repo.with_specialty("orthopedics")))

    def test_search_room(self) -> None:
        target = self.service.get(2).room
        self.assertIn(self.service.get(2), self.repo.search_room(target.upper()))
        self.assertEqual(len(self.repo.find_by_room(target)), len([i for i in self.repo.list() if i.room == target]))

    def test_adjust_hourly_rate(self) -> None:
        before = self.service.get(1).hourly_rate
        self.assertAlmostEqual(self.service.adjust_hourly_rate(1, 1.5).hourly_rate, before + 1.5, places=2)

    def test_toggle_accepting(self) -> None:
        before = self.service.get(1).accepting
        self.assertEqual(self.service.toggle_accepting(1).accepting, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_doctor(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_doctor(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)
