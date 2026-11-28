# clinic-service

Clinic Scheduling service in plain Python (standard library only).

Records: Doctor, Patient, Appointment, Prescription, Invoice, LabResult, Document, Notification, Address, Reminder, Setting, AuditEntry, Note, Review, ContactPerson, Discount, Tag.

```bash
python -m unittest discover -s tests -t .
python -m clinic_service         # http://127.0.0.1:8000/health
python examples/sample_data.py
```

The package also includes environment based settings, a container recipe, and API notes in
`docs/API.md`. Use `CLINIC_HOST`, `CLINIC_PORT`, and `CLINIC_SEED_SIZE` to configure startup.
