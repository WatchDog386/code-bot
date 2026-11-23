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


class LabResultOperationTests2(unittest.TestCase):
    """LabResult: operations, storage and export."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.lab_results
        self.repo = self.services.store.lab_results

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)


class LabResultApiTests(unittest.TestCase):
    """LabResult: the HTTP API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.lab_results
        self.repo = self.services.store.lab_results

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/lab-results", sample_lab_result(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/lab-results/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/lab-results?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/lab-results/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/lab-results/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/lab-results/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/lab-results", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/lab-results?sort=nope")[0], 400)


if __name__ == "__main__":
    unittest.main()
