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


class AppointmentOperationTests(unittest.TestCase):
    """Appointment: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.appointments
        self.repo = self.services.store.appointments

    def test_day_ranges(self) -> None:
        day = self.service.get(2).day
        total = len(self.repo.day_before(day)) + len(self.repo.day_on(day)) + len(self.repo.day_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_slot(self) -> None:
        before = self.service.get(1).slot
        self.assertEqual(self.service.adjust_slot(1, 2).slot, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_slot(1, -(before + 100))

    def test_adjust_duration(self) -> None:
        before = self.service.get(1).duration
        self.assertEqual(self.service.adjust_duration(1, 2).duration, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_duration(1, -(before + 100))

    def test_search_reason(self) -> None:
        target = self.service.get(2).reason
        self.assertIn(self.service.get(2), self.repo.search_reason(target.upper()))
        self.assertEqual(len(self.repo.find_by_reason(target)), len([i for i in self.repo.list() if i.reason == target]))

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "no_show")
        self.assertEqual(item.status.value, "no_show")
        self.assertEqual(self.repo.count_by_status()["no_show"], len(self.repo.with_status("no_show")))

    def test_adjust_fee(self) -> None:
        before = self.service.get(1).fee
        self.assertAlmostEqual(self.service.adjust_fee(1, 1.5).fee, before + 1.5, places=2)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_appointment(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())
