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


class InvoiceValidationTests(unittest.TestCase):
    """Invoice: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.invoices
        self.repo = self.services.store.invoices

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_invoice(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_invoice(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_patient_id(self) -> None:
        data = sample_invoice(12)
        data["patient_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "patient_id")

    def test_rejects_bad_issued(self) -> None:
        data = sample_invoice(12)
        data["issued"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "issued")

    def test_rejects_bad_amount(self) -> None:
        data = sample_invoice(12)
        data["amount"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "amount")

    def test_rejects_bad_paid(self) -> None:
        data = sample_invoice(12)
        data["paid"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "paid")

    def test_rejects_bad_status(self) -> None:
        data = sample_invoice(12)
        data["status"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "status")
