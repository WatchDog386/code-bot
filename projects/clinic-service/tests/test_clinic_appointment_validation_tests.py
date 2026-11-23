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


class AppointmentValidationTests(unittest.TestCase):
    """Appointment: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.appointments
        self.repo = self.services.store.appointments

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_appointment(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_appointment(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_appointment(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_patient_id(self) -> None:
        data = sample_appointment(12)
        data["patient_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "patient_id")

    def test_rejects_bad_day(self) -> None:
        data = sample_appointment(12)
        data["day"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "day")

    def test_rejects_bad_slot(self) -> None:
        data = sample_appointment(12)
        data["slot"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "slot")

    def test_rejects_bad_duration(self) -> None:
        data = sample_appointment(12)
        data["duration"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "duration")
