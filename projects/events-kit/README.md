# events-kit

Event Ticketing kit in strict TypeScript (no runtime dependencies).

Records: Venue, Concert, TicketType, Attendee, Ticket, Sponsor, Document, Notification, Address, Reminder, Setting, AuditEntry, Note, Review, ContactPerson.

```bash
npm install
npx tsc -p .
node dist/selftest.js
node dist/example.js
```

The source is organized into models, stores, services, queries, CSV export helpers, and ticket
sales reports. See `docs/DEVELOPMENT.md` for the project layout and check commands.
