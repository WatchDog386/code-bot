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


class PrescriptionValidationTests(unittest.TestCase):
    """Prescription: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.prescriptions
        self.repo = self.services.store.prescriptions

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_prescription(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_prescription(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_appointment_id(self) -> None:
        data = sample_prescription(12)
        data["appointment_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "appointment_id")

    def test_rejects_bad_drug(self) -> None:
        data = sample_prescription(12)
        data["drug"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "drug")

    def test_rejects_bad_dose_mg(self) -> None:
        data = sample_prescription(12)
        data["dose_mg"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "dose_mg")

    def test_rejects_bad_times_per_day(self) -> None:
        data = sample_prescription(12)
        data["times_per_day"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "times_per_day")

    def test_rejects_bad_days(self) -> None:
        data = sample_prescription(12)
        data["days"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "days")
