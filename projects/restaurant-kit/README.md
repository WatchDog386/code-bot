# restaurant-kit

Restaurant Orders kit in strict TypeScript (no runtime dependencies).

Records: MenuCategory, MenuItem, DiningTable, CustomerOrder, OrderLine, Booking, Document, Notification, Address, Reminder, Setting, AuditEntry, Note, Review, ContactPerson.

```bash
npm install
npx tsc -p .
node dist/selftest.js
node dist/example.js
```

The source is organized into models, stores, services, queries, CSV export helpers, and daily
sales reports. See `docs/DEVELOPMENT.md` for the project layout and check commands.
