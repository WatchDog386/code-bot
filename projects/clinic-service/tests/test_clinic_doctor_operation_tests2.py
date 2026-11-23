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


class DoctorOperationTests2(unittest.TestCase):
    """Doctor: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.doctors
        self.repo = self.services.store.doctors

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = DoctorRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)
