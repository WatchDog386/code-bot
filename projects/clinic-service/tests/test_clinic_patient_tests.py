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


class PatientTests(unittest.TestCase):
    """Patient: creating and reading."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.patients
        self.repo = self.services.store.patients

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_patient(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)
