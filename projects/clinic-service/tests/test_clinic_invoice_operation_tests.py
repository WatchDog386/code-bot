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


class InvoiceOperationTests(unittest.TestCase):
    """Invoice: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.invoices
        self.repo = self.services.store.invoices

    def test_issued_ranges(self) -> None:
        day = self.service.get(2).issued
        total = len(self.repo.issued_before(day)) + len(self.repo.issued_on(day)) + len(self.repo.issued_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_amount(self) -> None:
        before = self.service.get(1).amount
        self.assertAlmostEqual(self.service.adjust_amount(1, 1.5).amount, before + 1.5, places=2)

    def test_adjust_paid(self) -> None:
        before = self.service.get(1).paid
        self.assertAlmostEqual(self.service.adjust_paid(1, 1.5).paid, before + 1.5, places=2)

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "void")
        self.assertEqual(item.status.value, "void")
        self.assertEqual(self.repo.count_by_status()["void"], len(self.repo.with_status("void")))

    def test_due_ranges(self) -> None:
        day = self.service.get(2).due
        total = len(self.repo.due_before(day)) + len(self.repo.due_on(day)) + len(self.repo.due_after(day))
        self.assertEqual(total, self.repo.count())

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_invoice(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = InvoiceRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)
