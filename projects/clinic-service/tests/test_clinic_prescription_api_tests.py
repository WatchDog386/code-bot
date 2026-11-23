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


class PrescriptionApiTests(unittest.TestCase):
    """Prescription: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.prescriptions
        self.repo = self.services.store.prescriptions

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/prescriptions", sample_prescription(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/prescriptions/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/prescriptions?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/prescriptions/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/prescriptions/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/prescriptions/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/prescriptions", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/prescriptions?sort=nope")[0], 400)
