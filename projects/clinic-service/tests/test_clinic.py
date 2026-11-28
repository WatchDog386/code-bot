"""Tests for the Clinic Scheduling service (run: python -m unittest discover -s tests -t .)."""

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
    DocumentRepository,
    NotificationRepository,
    AddressRepository,
    ReminderRepository,
    SettingRepository,
    AuditEntryRepository,
    NoteRepository,
    ReviewRepository,
    ContactPersonRepository,
    DiscountRepository,
    TagRepository,
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
    sample_document,
    sample_notification,
    sample_address,
    sample_reminder,
    sample_setting,
    sample_audit_entry,
    sample_note,
    sample_review,
    sample_contact_person,
    sample_discount,
    sample_tag,
)


class DoctorTests(unittest.TestCase):
    """Doctor: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.doctors
        self.repo = self.services.store.doctors

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_doctor(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

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

    def test_rejects_bad_accepting(self) -> None:
        data = sample_doctor(12)
        data["accepting"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "accepting")

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_search_email(self) -> None:
        target = self.service.get(2).email
        self.assertIn(self.service.get(2), self.repo.search_email(target.upper()))
        self.assertEqual(len(self.repo.find_by_email(target)), len([i for i in self.repo.list() if i.email == target]))

    def test_set_specialty(self) -> None:
        item = self.service.set_specialty(1, "orthopedics")
        self.assertEqual(item.specialty.value, "orthopedics")
        self.assertEqual(self.repo.count_by_specialty()["orthopedics"], len(self.repo.with_specialty("orthopedics")))

    def test_search_room(self) -> None:
        target = self.service.get(2).room
        self.assertIn(self.service.get(2), self.repo.search_room(target.upper()))
        self.assertEqual(len(self.repo.find_by_room(target)), len([i for i in self.repo.list() if i.room == target]))

    def test_adjust_hourly_rate(self) -> None:
        before = self.service.get(1).hourly_rate
        self.assertAlmostEqual(self.service.adjust_hourly_rate(1, 1.5).hourly_rate, before + 1.5, places=2)

    def test_toggle_accepting(self) -> None:
        before = self.service.get(1).accepting
        self.assertEqual(self.service.toggle_accepting(1).accepting, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_doctor(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_doctor(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

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

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/doctors", sample_doctor(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/doctors/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/doctors?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/doctors/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/doctors/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/doctors/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/doctors", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/doctors?sort=nope")[0], 400)


class PatientTests(unittest.TestCase):
    """Patient: validation, links, operations, storage and the API."""

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

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_patient(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_patient(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_name(self) -> None:
        data = sample_patient(12)
        data["name"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "name")

    def test_rejects_bad_email(self) -> None:
        data = sample_patient(12)
        data["email"] = "not-an-email"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "email")

    def test_rejects_bad_phone(self) -> None:
        data = sample_patient(12)
        data["phone"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "phone")

    def test_rejects_bad_birth_date(self) -> None:
        data = sample_patient(12)
        data["birth_date"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "birth_date")

    def test_rejects_bad_insurance(self) -> None:
        data = sample_patient(12)
        data["insurance"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "insurance")

    def test_rejects_bad_allergies(self) -> None:
        data = sample_patient(12)
        data["allergies"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "allergies")

    def test_rejects_bad_active(self) -> None:
        data = sample_patient(12)
        data["active"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "active")

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_search_email(self) -> None:
        target = self.service.get(2).email
        self.assertIn(self.service.get(2), self.repo.search_email(target.upper()))
        self.assertEqual(len(self.repo.find_by_email(target)), len([i for i in self.repo.list() if i.email == target]))

    def test_search_phone(self) -> None:
        target = self.service.get(2).phone
        self.assertIn(self.service.get(2), self.repo.search_phone(target.upper()))
        self.assertEqual(len(self.repo.find_by_phone(target)), len([i for i in self.repo.list() if i.phone == target]))

    def test_birth_date_ranges(self) -> None:
        day = self.service.get(2).birth_date
        total = len(self.repo.birth_date_before(day)) + len(self.repo.birth_date_on(day)) + len(self.repo.birth_date_after(day))
        self.assertEqual(total, self.repo.count())

    def test_search_insurance(self) -> None:
        target = self.service.get(2).insurance
        self.assertIn(self.service.get(2), self.repo.search_insurance(target.upper()))
        self.assertEqual(len(self.repo.find_by_insurance(target)), len([i for i in self.repo.list() if i.insurance == target]))

    def test_search_allergies(self) -> None:
        target = self.service.get(2).allergies
        self.assertIn(self.service.get(2), self.repo.search_allergies(target.upper()))
        self.assertEqual(len(self.repo.find_by_allergies(target)), len([i for i in self.repo.list() if i.allergies == target]))

    def test_toggle_active(self) -> None:
        before = self.service.get(1).active
        self.assertEqual(self.service.toggle_active(1).active, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_patient(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_patient(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = PatientRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/patients", sample_patient(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/patients/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/patients?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/patients/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/patients/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/patients/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/patients", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/patients?sort=nope")[0], 400)


class AppointmentTests(unittest.TestCase):
    """Appointment: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.appointments
        self.repo = self.services.store.appointments

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_appointment(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

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

    def test_day_ranges(self) -> None:
        day = self.service.get(2).day
        total = len(self.repo.day_before(day)) + len(self.repo.day_on(day)) + len(self.repo.day_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_slot(self) -> None:
        before = self.service.get(1).slot
        self.assertEqual(self.service.adjust_slot(1, 2).slot, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_slot(1, -(before + 100))

    def test_adjust_duration(self) -> None:
        before = self.service.get(1).duration
        self.assertEqual(self.service.adjust_duration(1, 2).duration, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_duration(1, -(before + 100))

    def test_search_reason(self) -> None:
        target = self.service.get(2).reason
        self.assertIn(self.service.get(2), self.repo.search_reason(target.upper()))
        self.assertEqual(len(self.repo.find_by_reason(target)), len([i for i in self.repo.list() if i.reason == target]))

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "no_show")
        self.assertEqual(item.status.value, "no_show")
        self.assertEqual(self.repo.count_by_status()["no_show"], len(self.repo.with_status("no_show")))

    def test_adjust_fee(self) -> None:
        before = self.service.get(1).fee
        self.assertAlmostEqual(self.service.adjust_fee(1, 1.5).fee, before + 1.5, places=2)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_appointment(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_delete_record_in_use_conflicts(self) -> None:
        with self.assertRaises(Conflict):
            self.service.delete(1)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = AppointmentRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/appointments", sample_appointment(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/appointments/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/appointments?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/appointments/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/appointments/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/appointments/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/appointments", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/appointments?sort=nope")[0], 400)


class PrescriptionTests(unittest.TestCase):
    """Prescription: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.prescriptions
        self.repo = self.services.store.prescriptions

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_prescription(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

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

    def test_search_drug(self) -> None:
        target = self.service.get(2).drug
        self.assertIn(self.service.get(2), self.repo.search_drug(target.upper()))
        self.assertEqual(len(self.repo.find_by_drug(target)), len([i for i in self.repo.list() if i.drug == target]))

    def test_adjust_dose_mg(self) -> None:
        before = self.service.get(1).dose_mg
        self.assertEqual(self.service.adjust_dose_mg(1, 2).dose_mg, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_dose_mg(1, -(before + 100))

    def test_adjust_times_per_day(self) -> None:
        before = self.service.get(1).times_per_day
        self.assertEqual(self.service.adjust_times_per_day(1, 2).times_per_day, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_times_per_day(1, -(before + 100))

    def test_adjust_days(self) -> None:
        before = self.service.get(1).days
        self.assertEqual(self.service.adjust_days(1, 2).days, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_days(1, -(before + 100))

    def test_adjust_refills(self) -> None:
        before = self.service.get(1).refills
        self.assertEqual(self.service.adjust_refills(1, 2).refills, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_refills(1, -(before + 100))

    def test_search_notes(self) -> None:
        target = self.service.get(2).notes
        self.assertIn(self.service.get(2), self.repo.search_notes(target.upper()))
        self.assertEqual(len(self.repo.find_by_notes(target)), len([i for i in self.repo.list() if i.notes == target]))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_prescription(20)["drug"]
        after = self.service.update(1, {"drug": new_value})
        self.assertEqual(after.drug, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_prescription(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = PrescriptionRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

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


class InvoiceTests(unittest.TestCase):
    """Invoice: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.invoices
        self.repo = self.services.store.invoices

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_invoice(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_invoice(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_invoice(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_patient_id(self) -> None:
        data = sample_invoice(12)
        data["patient_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "patient_id")

    def test_rejects_bad_issued(self) -> None:
        data = sample_invoice(12)
        data["issued"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "issued")

    def test_rejects_bad_amount(self) -> None:
        data = sample_invoice(12)
        data["amount"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "amount")

    def test_rejects_bad_paid(self) -> None:
        data = sample_invoice(12)
        data["paid"] = -5.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "paid")

    def test_rejects_bad_status(self) -> None:
        data = sample_invoice(12)
        data["status"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "status")

    def test_rejects_bad_due(self) -> None:
        data = sample_invoice(12)
        data["due"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "due")

    def test_patient_id_must_exist(self) -> None:
        data = sample_invoice(13)
        data["patient_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_issued_ranges(self) -> None:
        day = self.service.get(2).issued
        total = len(self.repo.issued_before(day)) + len(self.repo.issued_on(day)) + len(self.repo.issued_after(day))
        self.assertEqual(total, self.repo.count())

    def test_adjust_amount(self) -> None:
        before = self.service.get(1).amount
        self.assertAlmostEqual(self.service.adjust_amount(1, 1.5).amount, before + 1.5, places=2)

    def test_adjust_paid(self) -> None:
        before = self.service.get(1).paid
        self.assertAlmostEqual(self.service.adjust_paid(1, 1.5).paid, before + 1.5, places=2)

    def test_set_status(self) -> None:
        item = self.service.set_status(1, "void")
        self.assertEqual(item.status.value, "void")
        self.assertEqual(self.repo.count_by_status()["void"], len(self.repo.with_status("void")))

    def test_due_ranges(self) -> None:
        day = self.service.get(2).due
        total = len(self.repo.due_before(day)) + len(self.repo.due_on(day)) + len(self.repo.due_after(day))
        self.assertEqual(total, self.repo.count())

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_invoice(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = InvoiceRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/invoices", sample_invoice(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/invoices/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/invoices?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/invoices/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/invoices/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/invoices/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/invoices", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/invoices?sort=nope")[0], 400)


class LabResultTests(unittest.TestCase):
    """LabResult: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.lab_results
        self.repo = self.services.store.lab_results

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_lab_result(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

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

    def test_rejects_bad_flagged(self) -> None:
        data = sample_lab_result(12)
        data["flagged"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "flagged")

    def test_patient_id_must_exist(self) -> None:
        data = sample_lab_result(13)
        data["patient_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_test_name(self) -> None:
        target = self.service.get(2).test_name
        self.assertIn(self.service.get(2), self.repo.search_test_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_test_name(target)), len([i for i in self.repo.list() if i.test_name == target]))

    def test_adjust_value(self) -> None:
        before = self.service.get(1).value
        self.assertAlmostEqual(self.service.adjust_value(1, 1.5).value, before + 1.5, places=2)

    def test_search_unit(self) -> None:
        target = self.service.get(2).unit
        self.assertIn(self.service.get(2), self.repo.search_unit(target.upper()))
        self.assertEqual(len(self.repo.find_by_unit(target)), len([i for i in self.repo.list() if i.unit == target]))

    def test_taken_ranges(self) -> None:
        day = self.service.get(2).taken
        total = len(self.repo.taken_before(day)) + len(self.repo.taken_on(day)) + len(self.repo.taken_after(day))
        self.assertEqual(total, self.repo.count())

    def test_toggle_flagged(self) -> None:
        before = self.service.get(1).flagged
        self.assertEqual(self.service.toggle_flagged(1).flagged, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_lab_result(20)["test_name"]
        after = self.service.update(1, {"test_name": new_value})
        self.assertEqual(after.test_name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_lab_result(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = LabResultRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

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


class DocumentTests(unittest.TestCase):
    """Document: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.documents
        self.repo = self.services.store.documents

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_document(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_document(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_document(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_document(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_title(self) -> None:
        data = sample_document(12)
        data["title"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "title")

    def test_rejects_bad_pages(self) -> None:
        data = sample_document(12)
        data["pages"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "pages")

    def test_rejects_bad_signed(self) -> None:
        data = sample_document(12)
        data["signed"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "signed")

    def test_rejects_bad_version(self) -> None:
        data = sample_document(12)
        data["version"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "version")

    def test_rejects_bad_issued(self) -> None:
        data = sample_document(12)
        data["issued"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "issued")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_document(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_title(self) -> None:
        target = self.service.get(2).title
        self.assertIn(self.service.get(2), self.repo.search_title(target.upper()))
        self.assertEqual(len(self.repo.find_by_title(target)), len([i for i in self.repo.list() if i.title == target]))

    def test_adjust_pages(self) -> None:
        before = self.service.get(1).pages
        self.assertEqual(self.service.adjust_pages(1, 2).pages, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_pages(1, -(before + 100))

    def test_toggle_signed(self) -> None:
        before = self.service.get(1).signed
        self.assertEqual(self.service.toggle_signed(1).signed, not before)

    def test_adjust_version(self) -> None:
        before = self.service.get(1).version
        self.assertEqual(self.service.adjust_version(1, 2).version, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_version(1, -(before + 100))

    def test_issued_ranges(self) -> None:
        day = self.service.get(2).issued
        total = len(self.repo.issued_before(day)) + len(self.repo.issued_on(day)) + len(self.repo.issued_after(day))
        self.assertEqual(total, self.repo.count())

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_document(20)["title"]
        after = self.service.update(1, {"title": new_value})
        self.assertEqual(after.title, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_document(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = DocumentRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/documents", sample_document(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/documents/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/documents?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/documents/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/documents/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/documents/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/documents", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/documents?sort=nope")[0], 400)


class NotificationTests(unittest.TestCase):
    """Notification: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.notifications
        self.repo = self.services.store.notifications

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_notification(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_notification(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_notification(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_recipient(self) -> None:
        data = sample_notification(12)
        data["recipient"] = "not-an-email"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "recipient")

    def test_rejects_bad_title(self) -> None:
        data = sample_notification(12)
        data["title"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "title")

    def test_rejects_bad_sent(self) -> None:
        data = sample_notification(12)
        data["sent"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "sent")

    def test_rejects_bad_channel(self) -> None:
        data = sample_notification(12)
        data["channel"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "channel")

    def test_rejects_bad_read(self) -> None:
        data = sample_notification(12)
        data["read"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "read")

    def test_search_recipient(self) -> None:
        target = self.service.get(2).recipient
        self.assertIn(self.service.get(2), self.repo.search_recipient(target.upper()))
        self.assertEqual(len(self.repo.find_by_recipient(target)), len([i for i in self.repo.list() if i.recipient == target]))

    def test_search_title(self) -> None:
        target = self.service.get(2).title
        self.assertIn(self.service.get(2), self.repo.search_title(target.upper()))
        self.assertEqual(len(self.repo.find_by_title(target)), len([i for i in self.repo.list() if i.title == target]))

    def test_sent_ranges(self) -> None:
        day = self.service.get(2).sent
        total = len(self.repo.sent_before(day)) + len(self.repo.sent_on(day)) + len(self.repo.sent_after(day))
        self.assertEqual(total, self.repo.count())

    def test_set_channel(self) -> None:
        item = self.service.set_channel(1, "push")
        self.assertEqual(item.channel.value, "push")
        self.assertEqual(self.repo.count_by_channel()["push"], len(self.repo.with_channel("push")))

    def test_toggle_read(self) -> None:
        before = self.service.get(1).read
        self.assertEqual(self.service.toggle_read(1).read, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_notification(20)["recipient"]
        after = self.service.update(1, {"recipient": new_value})
        self.assertEqual(after.recipient, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_notification(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = NotificationRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/notifications", sample_notification(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/notifications/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/notifications?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/notifications/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/notifications/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/notifications/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/notifications", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/notifications?sort=nope")[0], 400)


class AddressTests(unittest.TestCase):
    """Address: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.addresses
        self.repo = self.services.store.addresses

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_address(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_address(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_address(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_address(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_street(self) -> None:
        data = sample_address(12)
        data["street"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "street")

    def test_rejects_bad_city(self) -> None:
        data = sample_address(12)
        data["city"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "city")

    def test_rejects_bad_postcode(self) -> None:
        data = sample_address(12)
        data["postcode"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "postcode")

    def test_rejects_bad_country(self) -> None:
        data = sample_address(12)
        data["country"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "country")

    def test_rejects_bad_billing(self) -> None:
        data = sample_address(12)
        data["billing"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "billing")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_address(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_street(self) -> None:
        target = self.service.get(2).street
        self.assertIn(self.service.get(2), self.repo.search_street(target.upper()))
        self.assertEqual(len(self.repo.find_by_street(target)), len([i for i in self.repo.list() if i.street == target]))

    def test_search_city(self) -> None:
        target = self.service.get(2).city
        self.assertIn(self.service.get(2), self.repo.search_city(target.upper()))
        self.assertEqual(len(self.repo.find_by_city(target)), len([i for i in self.repo.list() if i.city == target]))

    def test_search_postcode(self) -> None:
        target = self.service.get(2).postcode
        self.assertIn(self.service.get(2), self.repo.search_postcode(target.upper()))
        self.assertEqual(len(self.repo.find_by_postcode(target)), len([i for i in self.repo.list() if i.postcode == target]))

    def test_search_country(self) -> None:
        target = self.service.get(2).country
        self.assertIn(self.service.get(2), self.repo.search_country(target.upper()))
        self.assertEqual(len(self.repo.find_by_country(target)), len([i for i in self.repo.list() if i.country == target]))

    def test_toggle_billing(self) -> None:
        before = self.service.get(1).billing
        self.assertEqual(self.service.toggle_billing(1).billing, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_address(20)["street"]
        after = self.service.update(1, {"street": new_value})
        self.assertEqual(after.street, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_address(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = AddressRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/addresses", sample_address(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/addresses/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/addresses?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/addresses/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/addresses/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/addresses/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/addresses", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/addresses?sort=nope")[0], 400)


class ReminderTests(unittest.TestCase):
    """Reminder: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.reminders
        self.repo = self.services.store.reminders

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_reminder(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_reminder(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_reminder(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_reminder(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_title(self) -> None:
        data = sample_reminder(12)
        data["title"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "title")

    def test_rejects_bad_remind_on(self) -> None:
        data = sample_reminder(12)
        data["remind_on"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "remind_on")

    def test_rejects_bad_done(self) -> None:
        data = sample_reminder(12)
        data["done"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "done")

    def test_rejects_bad_priority(self) -> None:
        data = sample_reminder(12)
        data["priority"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "priority")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_reminder(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_title(self) -> None:
        target = self.service.get(2).title
        self.assertIn(self.service.get(2), self.repo.search_title(target.upper()))
        self.assertEqual(len(self.repo.find_by_title(target)), len([i for i in self.repo.list() if i.title == target]))

    def test_remind_on_ranges(self) -> None:
        day = self.service.get(2).remind_on
        total = len(self.repo.remind_on_before(day)) + len(self.repo.remind_on_on(day)) + len(self.repo.remind_on_after(day))
        self.assertEqual(total, self.repo.count())

    def test_toggle_done(self) -> None:
        before = self.service.get(1).done
        self.assertEqual(self.service.toggle_done(1).done, not before)

    def test_set_priority(self) -> None:
        item = self.service.set_priority(1, "high")
        self.assertEqual(item.priority.value, "high")
        self.assertEqual(self.repo.count_by_priority()["high"], len(self.repo.with_priority("high")))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_reminder(20)["title"]
        after = self.service.update(1, {"title": new_value})
        self.assertEqual(after.title, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_reminder(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = ReminderRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/reminders", sample_reminder(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/reminders/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/reminders?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/reminders/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/reminders/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/reminders/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/reminders", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/reminders?sort=nope")[0], 400)


class SettingTests(unittest.TestCase):
    """Setting: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.settings
        self.repo = self.services.store.settings

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_setting(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_setting(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_setting(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_key_name(self) -> None:
        data = sample_setting(12)
        data["key_name"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "key_name")

    def test_rejects_bad_value(self) -> None:
        data = sample_setting(12)
        data["value"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "value")

    def test_rejects_bad_editable(self) -> None:
        data = sample_setting(12)
        data["editable"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "editable")

    def test_rejects_bad_changed(self) -> None:
        data = sample_setting(12)
        data["changed"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "changed")

    def test_search_key_name(self) -> None:
        target = self.service.get(2).key_name
        self.assertIn(self.service.get(2), self.repo.search_key_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_key_name(target)), len([i for i in self.repo.list() if i.key_name == target]))

    def test_search_value(self) -> None:
        target = self.service.get(2).value
        self.assertIn(self.service.get(2), self.repo.search_value(target.upper()))
        self.assertEqual(len(self.repo.find_by_value(target)), len([i for i in self.repo.list() if i.value == target]))

    def test_toggle_editable(self) -> None:
        before = self.service.get(1).editable
        self.assertEqual(self.service.toggle_editable(1).editable, not before)

    def test_changed_ranges(self) -> None:
        day = self.service.get(2).changed
        total = len(self.repo.changed_before(day)) + len(self.repo.changed_on(day)) + len(self.repo.changed_after(day))
        self.assertEqual(total, self.repo.count())

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_setting(20)["key_name"]
        after = self.service.update(1, {"key_name": new_value})
        self.assertEqual(after.key_name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_setting(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = SettingRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/settings", sample_setting(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/settings/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/settings?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/settings/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/settings/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/settings/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/settings", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/settings?sort=nope")[0], 400)


class AuditEntryTests(unittest.TestCase):
    """AuditEntry: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.audit_entries
        self.repo = self.services.store.audit_entries

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_audit_entry(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_audit_entry(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_audit_entry(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_actor(self) -> None:
        data = sample_audit_entry(12)
        data["actor"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "actor")

    def test_rejects_bad_action(self) -> None:
        data = sample_audit_entry(12)
        data["action"] = "nope"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "action")

    def test_rejects_bad_at(self) -> None:
        data = sample_audit_entry(12)
        data["at"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "at")

    def test_rejects_bad_details(self) -> None:
        data = sample_audit_entry(12)
        data["details"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "details")

    def test_search_actor(self) -> None:
        target = self.service.get(2).actor
        self.assertIn(self.service.get(2), self.repo.search_actor(target.upper()))
        self.assertEqual(len(self.repo.find_by_actor(target)), len([i for i in self.repo.list() if i.actor == target]))

    def test_set_action(self) -> None:
        item = self.service.set_action(1, "export")
        self.assertEqual(item.action.value, "export")
        self.assertEqual(self.repo.count_by_action()["export"], len(self.repo.with_action("export")))

    def test_at_ranges(self) -> None:
        day = self.service.get(2).at
        total = len(self.repo.at_before(day)) + len(self.repo.at_on(day)) + len(self.repo.at_after(day))
        self.assertEqual(total, self.repo.count())

    def test_search_details(self) -> None:
        target = self.service.get(2).details
        self.assertIn(self.service.get(2), self.repo.search_details(target.upper()))
        self.assertEqual(len(self.repo.find_by_details(target)), len([i for i in self.repo.list() if i.details == target]))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_audit_entry(20)["actor"]
        after = self.service.update(1, {"actor": new_value})
        self.assertEqual(after.actor, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_audit_entry(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = AuditEntryRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/audit-entries", sample_audit_entry(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/audit-entries/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/audit-entries?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/audit-entries/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/audit-entries/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/audit-entries/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/audit-entries", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/audit-entries?sort=nope")[0], 400)


class NoteTests(unittest.TestCase):
    """Note: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.notes
        self.repo = self.services.store.notes

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_note(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_note(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_note(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_note(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_subject(self) -> None:
        data = sample_note(12)
        data["subject"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "subject")

    def test_rejects_bad_body(self) -> None:
        data = sample_note(12)
        data["body"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "body")

    def test_rejects_bad_pinned(self) -> None:
        data = sample_note(12)
        data["pinned"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "pinned")

    def test_rejects_bad_written(self) -> None:
        data = sample_note(12)
        data["written"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "written")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_note(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_subject(self) -> None:
        target = self.service.get(2).subject
        self.assertIn(self.service.get(2), self.repo.search_subject(target.upper()))
        self.assertEqual(len(self.repo.find_by_subject(target)), len([i for i in self.repo.list() if i.subject == target]))

    def test_search_body(self) -> None:
        target = self.service.get(2).body
        self.assertIn(self.service.get(2), self.repo.search_body(target.upper()))
        self.assertEqual(len(self.repo.find_by_body(target)), len([i for i in self.repo.list() if i.body == target]))

    def test_toggle_pinned(self) -> None:
        before = self.service.get(1).pinned
        self.assertEqual(self.service.toggle_pinned(1).pinned, not before)

    def test_written_ranges(self) -> None:
        day = self.service.get(2).written
        total = len(self.repo.written_before(day)) + len(self.repo.written_on(day)) + len(self.repo.written_after(day))
        self.assertEqual(total, self.repo.count())

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_note(20)["subject"]
        after = self.service.update(1, {"subject": new_value})
        self.assertEqual(after.subject, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_note(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = NoteRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/notes", sample_note(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/notes/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/notes?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/notes/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/notes/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/notes/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/notes", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/notes?sort=nope")[0], 400)


class ReviewTests(unittest.TestCase):
    """Review: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.reviews
        self.repo = self.services.store.reviews

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_review(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_review(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_review(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_review(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_author(self) -> None:
        data = sample_review(12)
        data["author"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "author")

    def test_rejects_bad_stars(self) -> None:
        data = sample_review(12)
        data["stars"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "stars")

    def test_rejects_bad_comment(self) -> None:
        data = sample_review(12)
        data["comment"] = "x" * 3000
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "comment")

    def test_rejects_bad_verified(self) -> None:
        data = sample_review(12)
        data["verified"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "verified")

    def test_rejects_bad_posted(self) -> None:
        data = sample_review(12)
        data["posted"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "posted")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_review(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_author(self) -> None:
        target = self.service.get(2).author
        self.assertIn(self.service.get(2), self.repo.search_author(target.upper()))
        self.assertEqual(len(self.repo.find_by_author(target)), len([i for i in self.repo.list() if i.author == target]))

    def test_adjust_stars(self) -> None:
        before = self.service.get(1).stars
        self.assertEqual(self.service.adjust_stars(1, 2).stars, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_stars(1, -(before + 100))

    def test_search_comment(self) -> None:
        target = self.service.get(2).comment
        self.assertIn(self.service.get(2), self.repo.search_comment(target.upper()))
        self.assertEqual(len(self.repo.find_by_comment(target)), len([i for i in self.repo.list() if i.comment == target]))

    def test_toggle_verified(self) -> None:
        before = self.service.get(1).verified
        self.assertEqual(self.service.toggle_verified(1).verified, not before)

    def test_posted_ranges(self) -> None:
        day = self.service.get(2).posted
        total = len(self.repo.posted_before(day)) + len(self.repo.posted_on(day)) + len(self.repo.posted_after(day))
        self.assertEqual(total, self.repo.count())

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_review(20)["author"]
        after = self.service.update(1, {"author": new_value})
        self.assertEqual(after.author, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_review(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = ReviewRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/reviews", sample_review(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/reviews/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/reviews?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/reviews/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/reviews/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/reviews/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/reviews", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/reviews?sort=nope")[0], 400)


class ContactPersonTests(unittest.TestCase):
    """ContactPerson: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.contact_persons
        self.repo = self.services.store.contact_persons

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_contact_person(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_contact_person(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_contact_person(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_contact_person(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_name(self) -> None:
        data = sample_contact_person(12)
        data["name"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "name")

    def test_rejects_bad_email(self) -> None:
        data = sample_contact_person(12)
        data["email"] = "not-an-email"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "email")

    def test_rejects_bad_phone(self) -> None:
        data = sample_contact_person(12)
        data["phone"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "phone")

    def test_rejects_bad_role(self) -> None:
        data = sample_contact_person(12)
        data["role"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "role")

    def test_rejects_bad_primary(self) -> None:
        data = sample_contact_person(12)
        data["primary"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "primary")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_contact_person(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_name(self) -> None:
        target = self.service.get(2).name
        self.assertIn(self.service.get(2), self.repo.search_name(target.upper()))
        self.assertEqual(len(self.repo.find_by_name(target)), len([i for i in self.repo.list() if i.name == target]))

    def test_search_email(self) -> None:
        target = self.service.get(2).email
        self.assertIn(self.service.get(2), self.repo.search_email(target.upper()))
        self.assertEqual(len(self.repo.find_by_email(target)), len([i for i in self.repo.list() if i.email == target]))

    def test_search_phone(self) -> None:
        target = self.service.get(2).phone
        self.assertIn(self.service.get(2), self.repo.search_phone(target.upper()))
        self.assertEqual(len(self.repo.find_by_phone(target)), len([i for i in self.repo.list() if i.phone == target]))

    def test_search_role(self) -> None:
        target = self.service.get(2).role
        self.assertIn(self.service.get(2), self.repo.search_role(target.upper()))
        self.assertEqual(len(self.repo.find_by_role(target)), len([i for i in self.repo.list() if i.role == target]))

    def test_toggle_primary(self) -> None:
        before = self.service.get(1).primary
        self.assertEqual(self.service.toggle_primary(1).primary, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_contact_person(20)["name"]
        after = self.service.update(1, {"name": new_value})
        self.assertEqual(after.name, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_contact_person(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = ContactPersonRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/contact-persons", sample_contact_person(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/contact-persons/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/contact-persons?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/contact-persons/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/contact-persons/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/contact-persons/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/contact-persons", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/contact-persons?sort=nope")[0], 400)


class DiscountTests(unittest.TestCase):
    """Discount: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.discounts
        self.repo = self.services.store.discounts

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_discount(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_discount(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_discount(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_code(self) -> None:
        data = sample_discount(12)
        data["code"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "code")

    def test_rejects_bad_percent(self) -> None:
        data = sample_discount(12)
        data["percent"] = -1.0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "percent")

    def test_rejects_bad_starts(self) -> None:
        data = sample_discount(12)
        data["starts"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "starts")

    def test_rejects_bad_ends(self) -> None:
        data = sample_discount(12)
        data["ends"] = "2026-02-30"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "ends")

    def test_rejects_bad_active(self) -> None:
        data = sample_discount(12)
        data["active"] = "yes"
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "active")

    def test_search_code(self) -> None:
        target = self.service.get(2).code
        self.assertIn(self.service.get(2), self.repo.search_code(target.upper()))
        self.assertEqual(len(self.repo.find_by_code(target)), len([i for i in self.repo.list() if i.code == target]))

    def test_adjust_percent(self) -> None:
        before = self.service.get(1).percent
        self.assertAlmostEqual(self.service.adjust_percent(1, 1.5).percent, before + 1.5, places=2)

    def test_starts_ranges(self) -> None:
        day = self.service.get(2).starts
        total = len(self.repo.starts_before(day)) + len(self.repo.starts_on(day)) + len(self.repo.starts_after(day))
        self.assertEqual(total, self.repo.count())

    def test_ends_ranges(self) -> None:
        day = self.service.get(2).ends
        total = len(self.repo.ends_before(day)) + len(self.repo.ends_on(day)) + len(self.repo.ends_after(day))
        self.assertEqual(total, self.repo.count())

    def test_toggle_active(self) -> None:
        before = self.service.get(1).active
        self.assertEqual(self.service.toggle_active(1).active, not before)

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_discount(20)["code"]
        after = self.service.update(1, {"code": new_value})
        self.assertEqual(after.code, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_discount(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = DiscountRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/discounts", sample_discount(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/discounts/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/discounts?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/discounts/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/discounts/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/discounts/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/discounts", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/discounts?sort=nope")[0], 400)


class TagTests(unittest.TestCase):
    """Tag: validation, links, operations, storage and the API."""

    def setUp(self) -> None:
        self.services = Services()
        self.services.seed()
        self.service = self.services.tags
        self.repo = self.services.store.tags

    def test_create_and_get(self) -> None:
        item = self.service.create(sample_tag(10))
        self.assertGreater(item.id, 0)
        self.assertEqual(self.service.get(item.id), item)

    def test_seeded_records_are_listed(self) -> None:
        self.assertEqual(len(self.service.list()), 3)

    def test_missing_record_raises(self) -> None:
        with self.assertRaises(NotFound):
            self.service.get(9999)

    def test_unknown_field_is_rejected(self) -> None:
        data = sample_tag(11)
        data["no_such_field"] = 1
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_id_cannot_be_chosen(self) -> None:
        data = sample_tag(11)
        data["id"] = 42
        with self.assertRaises(ValidationError):
            self.service.create(data)

    def test_rejects_bad_doctor_id(self) -> None:
        data = sample_tag(12)
        data["doctor_id"] = 0
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "doctor_id")

    def test_rejects_bad_label(self) -> None:
        data = sample_tag(12)
        data["label"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "label")

    def test_rejects_bad_color(self) -> None:
        data = sample_tag(12)
        data["color"] = ""
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "color")

    def test_rejects_bad_usage(self) -> None:
        data = sample_tag(12)
        data["usage"] = -1
        with self.assertRaises(ValidationError) as caught:
            self.service.create(data)
        self.assertEqual(caught.exception.field_name, "usage")

    def test_doctor_id_must_exist(self) -> None:
        data = sample_tag(13)
        data["doctor_id"] = 9999
        with self.assertRaises(NotFound):
            self.service.create(data)

    def test_search_label(self) -> None:
        target = self.service.get(2).label
        self.assertIn(self.service.get(2), self.repo.search_label(target.upper()))
        self.assertEqual(len(self.repo.find_by_label(target)), len([i for i in self.repo.list() if i.label == target]))

    def test_search_color(self) -> None:
        target = self.service.get(2).color
        self.assertIn(self.service.get(2), self.repo.search_color(target.upper()))
        self.assertEqual(len(self.repo.find_by_color(target)), len([i for i in self.repo.list() if i.color == target]))

    def test_adjust_usage(self) -> None:
        before = self.service.get(1).usage
        self.assertEqual(self.service.adjust_usage(1, 2).usage, before + 2)
        with self.assertRaises(ValidationError):
            self.service.adjust_usage(1, -(before + 100))

    def test_update_changes_only_given_fields(self) -> None:
        before = self.service.get(1)
        new_value = sample_tag(20)["label"]
        after = self.service.update(1, {"label": new_value})
        self.assertEqual(after.label, new_value)
        self.assertEqual(after.id, before.id)

    def test_delete_unused_record(self) -> None:
        item = self.service.create(sample_tag(14))
        self.service.delete(item.id)
        with self.assertRaises(NotFound):
            self.service.get(item.id)

    def test_stats_count(self) -> None:
        self.assertEqual(self.service.stats()["count"], self.repo.count())

    def test_json_round_trip(self) -> None:
        copy = TagRepository()
        self.assertEqual(copy.load_json(self.repo.to_json()), 3)
        self.assertEqual(copy.list(), self.repo.list())
        self.assertEqual(copy.add(copy.model()).id, 4)

    def test_csv_export(self) -> None:
        lines = self.repo.to_csv().splitlines()
        self.assertTrue(lines[0].startswith("id,"))
        self.assertEqual(len(lines), 4)

    def test_api_round_trip(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/tags", sample_tag(15))
        self.assertEqual(status, 201)
        status, fetched = api.handle("GET", f"/tags/{body['id']}")
        self.assertEqual((status, fetched), (200, body))
        status, listed = api.handle("GET", "/tags?sort=-id&size=1")
        self.assertEqual(listed[0]["id"], body["id"])
        status, _ = api.handle("GET", "/tags/stats")
        self.assertEqual(status, 200)
        status, _ = api.handle("DELETE", f"/tags/{body['id']}")
        self.assertEqual(status, 204)
        self.assertEqual(api.handle("GET", f"/tags/{body['id']}")[0], 404)

    def test_api_rejects_bad_input(self) -> None:
        api = Api(self.services)
        status, body = api.handle("POST", "/tags", {"no_such_field": 1})
        self.assertEqual(status, 400)
        self.assertEqual(api.handle("GET", "/tags?sort=nope")[0], 400)


if __name__ == "__main__":
    unittest.main()
