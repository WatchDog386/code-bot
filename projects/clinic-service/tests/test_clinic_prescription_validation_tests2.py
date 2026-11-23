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


class PrescriptionValidationTests2(unittest.TestCase):
    """Prescription: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.prescriptions
        self.repo = self.services.store.prescriptions

    def test_rejects_bad_refills(self) -> None:
        data = sample_prescription(12)
        data["refills"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "refills")

    def test_rejects_bad_notes(self) -> None:
        data = sample_prescription(12)
        data["notes"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "notes")

    def test_appointment_id_must_exist(self) -> None:
        data = sample_prescription(13)
        data["appointment_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
