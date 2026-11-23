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


class AppointmentValidationTests2(unittest.TestCase):
    """Appointment: rejecting bad data."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.appointments
        self.repo = self.services.store.appointments

    def test_rejects_bad_reason(self) -> None:
        data = sample_appointment(12)
        data["reason"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "reason")

    def test_rejects_bad_status(self) -> None:
        data = sample_appointment(12)
        data["status"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "status")

    def test_rejects_bad_fee(self) -> None:
        data = sample_appointment(12)
        data["fee"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "fee")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_appointment(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_patient_id_must_exist(self) -> None:
        data = sample_appointment(13)
        data["patient_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)
