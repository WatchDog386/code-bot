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


class DoctorValidationTests(unittest.TestCase):
    """Doctor: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.doctors
        self.repo = self.services.store.doctors

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_doctor(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_doctor(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_name(self) -> None:
        data = sample_doctor(12)
        data["name"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "name")

    def test_rejects_bad_email(self) -> None:
        data = sample_doctor(12)
        data["email"] = "not-an-email"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "email")

    def test_rejects_bad_specialty(self) -> None:
        data = sample_doctor(12)
        data["specialty"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "specialty")

    def test_rejects_bad_room(self) -> None:
        data = sample_doctor(12)
        data["room"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "room")

    def test_rejects_bad_hourly_rate(self) -> None:
        data = sample_doctor(12)
        data["hourly_rate"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "hourly_rate")
