# school-service

School Records service in plain Python (standard library only).

Records: Teacher, Student, Course, Enrollment, Assignment, Attendance, Document, Notification, Address, Reminder, Setting, AuditEntry, Note, Review, ContactPerson, Discount, Tag.

```bash
python -m unittest discover -s tests -t .
python -m school_service          # http://127.0.0.1:8000/health
python examples/sample_data.py
```

The package also includes environment based settings, a container recipe, and API notes in
`docs/API.md`. Use `SCHOOL_HOST`, `SCHOOL_PORT`, and `SCHOOL_SEED_SIZE` to configure startup.
