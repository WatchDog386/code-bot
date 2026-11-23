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


class LabResultValidationTests(unittest.TestCase):
    """LabResult: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.lab_results
        self.repo = self.services.store.lab_results

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_lab_result(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_lab_result(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_patient_id(self) -> None:
        data = sample_lab_result(12)
        data["patient_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "patient_id")

    def test_rejects_bad_test_name(self) -> None:
        data = sample_lab_result(12)
        data["test_name"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "test_name")

    def test_rejects_bad_value(self) -> None:
        data = sample_lab_result(12)
        data["value"] = -1.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "value")

    def test_rejects_bad_unit(self) -> None:
        data = sample_lab_result(12)
        data["unit"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "unit")

    def test_rejects_bad_taken(self) -> None:
        data = sample_lab_result(12)
        data["taken"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "taken")
