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


class InvoiceValidationTests2(unittest.TestCase):
    """Invoice: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.invoices
        self.repo = self.services.store.invoices

    def test_rejects_bad_due(self) -> None:
        data = sample_invoice(12)
        data["due"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "due")

    def test_patient_id_must_exist(self) -> None:
        data = sample_invoice(13)
        data["patient_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
