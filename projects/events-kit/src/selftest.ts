/** Self-test for the Event Ticketing kit: run `node dist/selftest.js` after `tsc -p .`. */

import { ValidationError } from "./models";
import { toCsv } from "./csv";
import { ticketSales, ticketSalesCsv } from "./reports";
import {
  ConflictError,
  NotFoundError,
  Services,
  sampleVenue,
  sampleConcert,
  sampleTicketType,
  sampleAttendee,
  sampleTicket,
  sampleSponsor,
  sampleDocument,
  sampleNotification,
  sampleAddress,
  sampleReminder,
  sampleSetting,
  sampleAuditEntry,
  sampleNote,
  sampleReview,
  sampleContactPerson,
} from "./services";
import {
  describeVenue,
  queryVenues,
  describeConcert,
  queryConcerts,
  describeTicketType,
  queryTicketTypes,
  describeAttendee,
  queryAttendees,
  describeTicket,
  queryTickets,
  describeSponsor,
  querySponsors,
  describeDocument,
  queryDocuments,
  describeNotification,
  queryNotifications,
  describeAddress,
  queryAddresses,
  describeReminder,
  queryReminders,
  describeSetting,
  querySettings,
  describeAuditEntry,
  queryAuditEntries,
  describeNote,
  queryNotes,
  describeReview,
  queryReviews,
  describeContactPerson,
  queryContactPersons,
} from "./queries";

let passed = 0;
const failures: string[] = [];

function test(name: string, body: () => void): void {
  try {
    body();
    passed += 1;
  } catch (err) {
    failures.push(`${name}: ${err instanceof Error ? err.message : String(err)}`);
  }
}

function assert(condition: boolean, message: string): void {
  if (!condition) {
    throw new Error(message);
  }
}

function throwsField(action: () => unknown, field: string): void {
  try {
    action();
  } catch (err) {
    if (err instanceof ValidationError && err.field === field) {
      return;
    }
    throw new Error(`expected a validation error on ${field}, got ${String(err)}`);
  }
  throw new Error(`expected a validation error on ${field}`);
}

function throwsKind(action: () => unknown, kind: new (...args: never[]) => Error): void {
  try {
    action();
  } catch (err) {
    if (err instanceof kind) {
      return;
    }
    throw new Error(`expected ${kind.name}, got ${String(err)}`);
  }
  throw new Error(`expected ${kind.name}`);
}

function seeded(): Services {
  const services = new Services();
  services.seed(3);
  return services;
}

// ---------------------------------------------------------------------------- Venue

test("venue: create and get", () => {
  const s = seeded();
  const item = s.venues.create(sampleVenue(10));
  assert(s.venues.get(item.id) === item, "stored record differs");
  assert(s.venues.list().length === 4, "list should have 4 records");
});

test("venue: missing record", () => {
  throwsKind(() => seeded().venues.get(9999), NotFoundError);
});

test("venue: unknown field", () => {
  const data = sampleVenue(11);
  data.noSuchField = 1;
  throwsField(() => seeded().venues.create(data), "noSuchField");
});

test("venue: id can't be chosen", () => {
  const data = sampleVenue(11);
  data.id = 42;
  throwsField(() => seeded().venues.create(data), "id");
});

test("venue: rejects a bad name", () => {
  const data = sampleVenue(12);
  data.name = "";
  throwsField(() => seeded().venues.create(data), "name");
});

test("venue: rejects a bad city", () => {
  const data = sampleVenue(12);
  data.city = "";
  throwsField(() => seeded().venues.create(data), "city");
});

test("venue: rejects a bad capacity", () => {
  const data = sampleVenue(12);
  data.capacity = -1;
  throwsField(() => seeded().venues.create(data), "capacity");
});

test("venue: rejects a bad address", () => {
  const data = sampleVenue(12);
  data.address = "";
  throwsField(() => seeded().venues.create(data), "address");
});

test("venue: rejects a bad accessible", () => {
  const data = sampleVenue(12);
  data.accessible = "yes";
  throwsField(() => seeded().venues.create(data), "accessible");
});

test("venue: search name", () => {
  const s = seeded();
  const target = s.venues.get(2);
  assert(s.store.venues.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.venues.findByName(target.name).includes(target), "find missed it");
});

test("venue: search city", () => {
  const s = seeded();
  const target = s.venues.get(2);
  assert(s.store.venues.searchCity(target.city.toUpperCase()).includes(target), "search missed it");
  assert(s.store.venues.findByCity(target.city).includes(target), "find missed it");
});

test("venue: adjust capacity", () => {
  const s = seeded();
  const before = s.venues.get(1).capacity;
  assert(s.venues.adjustCapacity(1, 2).capacity === before + 2, "not adjusted");
  throwsField(() => s.venues.adjustCapacity(1, -(before + 100)), "capacity");
});

test("venue: search address", () => {
  const s = seeded();
  const target = s.venues.get(2);
  assert(s.store.venues.searchAddress(target.address.toUpperCase()).includes(target), "search missed it");
  assert(s.store.venues.findByAddress(target.address).includes(target), "find missed it");
});

test("venue: toggle accessible", () => {
  const s = seeded();
  const before = s.venues.get(1).accessible;
  assert(s.venues.toggleAccessible(1).accessible === !before, "flag not flipped");
});

test("venue: delete an unused record", () => {
  const s = seeded();
  const item = s.venues.create(sampleVenue(14));
  s.venues.delete(item.id);
  throwsKind(() => s.venues.get(item.id), NotFoundError);
});

test("venue: delete a record in use", () => {
  throwsKind(() => seeded().venues.delete(1), ConflictError);
});

test("venue: stats and queries", () => {
  const s = seeded();
  assert(s.venues.stats().count === 3, "wrong count");
  const newest = queryVenues(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryVenues(s.store, { sort: "nope" }), "sort");
  assert(describeVenue().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Concert

test("concert: create and get", () => {
  const s = seeded();
  const item = s.concerts.create(sampleConcert(10));
  assert(s.concerts.get(item.id) === item, "stored record differs");
  assert(s.concerts.list().length === 4, "list should have 4 records");
});

test("concert: missing record", () => {
  throwsKind(() => seeded().concerts.get(9999), NotFoundError);
});

test("concert: unknown field", () => {
  const data = sampleConcert(11);
  data.noSuchField = 1;
  throwsField(() => seeded().concerts.create(data), "noSuchField");
});

test("concert: id can't be chosen", () => {
  const data = sampleConcert(11);
  data.id = 42;
  throwsField(() => seeded().concerts.create(data), "id");
});

test("concert: rejects a bad venue id", () => {
  const data = sampleConcert(12);
  data.venueId = 0;
  throwsField(() => seeded().concerts.create(data), "venueId");
});

test("concert: rejects a bad title", () => {
  const data = sampleConcert(12);
  data.title = "";
  throwsField(() => seeded().concerts.create(data), "title");
});

test("concert: rejects a bad artist", () => {
  const data = sampleConcert(12);
  data.artist = "";
  throwsField(() => seeded().concerts.create(data), "artist");
});

test("concert: rejects a bad day", () => {
  const data = sampleConcert(12);
  data.day = "2026-02-30";
  throwsField(() => seeded().concerts.create(data), "day");
});

test("concert: rejects a bad doors open", () => {
  const data = sampleConcert(12);
  data.doorsOpen = "";
  throwsField(() => seeded().concerts.create(data), "doorsOpen");
});

test("concert: rejects a bad status", () => {
  const data = sampleConcert(12);
  data.status = "nope";
  throwsField(() => seeded().concerts.create(data), "status");
});

test("concert: venue id must exist", () => {
  const data = sampleConcert(13);
  data.venueId = 9999;
  throwsKind(() => seeded().concerts.create(data), NotFoundError);
});

test("concert: search title", () => {
  const s = seeded();
  const target = s.concerts.get(2);
  assert(s.store.concerts.searchTitle(target.title.toUpperCase()).includes(target), "search missed it");
  assert(s.store.concerts.findByTitle(target.title).includes(target), "find missed it");
});

test("concert: search artist", () => {
  const s = seeded();
  const target = s.concerts.get(2);
  assert(s.store.concerts.searchArtist(target.artist.toUpperCase()).includes(target), "search missed it");
  assert(s.store.concerts.findByArtist(target.artist).includes(target), "find missed it");
});

test("concert: day ranges", () => {
  const s = seeded();
  const day = s.concerts.get(2).day;
  const total = s.store.concerts.dayBefore(day).length + s.store.concerts.dayOn(day).length + s.store.concerts.dayAfter(day).length;
  assert(total === s.store.concerts.count(), "ranges don't cover every record");
});

test("concert: search doors open", () => {
  const s = seeded();
  const target = s.concerts.get(2);
  assert(s.store.concerts.searchDoorsOpen(target.doorsOpen.toUpperCase()).includes(target), "search missed it");
  assert(s.store.concerts.findByDoorsOpen(target.doorsOpen).includes(target), "find missed it");
});

test("concert: set status", () => {
  const s = seeded();
  assert(s.concerts.setStatus(1, "finished").status === "finished", "value not changed");
  assert(s.store.concerts.countByStatus()["finished"] === s.store.concerts.withStatus("finished").length, "counts differ");
});

test("concert: delete an unused record", () => {
  const s = seeded();
  const item = s.concerts.create(sampleConcert(14));
  s.concerts.delete(item.id);
  throwsKind(() => s.concerts.get(item.id), NotFoundError);
});

test("concert: delete a record in use", () => {
  throwsKind(() => seeded().concerts.delete(1), ConflictError);
});

test("concert: stats and queries", () => {
  const s = seeded();
  assert(s.concerts.stats().count === 3, "wrong count");
  const newest = queryConcerts(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryConcerts(s.store, { sort: "nope" }), "sort");
  assert(describeConcert().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- TicketType

test("ticket type: create and get", () => {
  const s = seeded();
  const item = s.ticketTypes.create(sampleTicketType(10));
  assert(s.ticketTypes.get(item.id) === item, "stored record differs");
  assert(s.ticketTypes.list().length === 4, "list should have 4 records");
});

test("ticket type: missing record", () => {
  throwsKind(() => seeded().ticketTypes.get(9999), NotFoundError);
});

test("ticket type: unknown field", () => {
  const data = sampleTicketType(11);
  data.noSuchField = 1;
  throwsField(() => seeded().ticketTypes.create(data), "noSuchField");
});

test("ticket type: id can't be chosen", () => {
  const data = sampleTicketType(11);
  data.id = 42;
  throwsField(() => seeded().ticketTypes.create(data), "id");
});

test("ticket type: rejects a bad concert id", () => {
  const data = sampleTicketType(12);
  data.concertId = 0;
  throwsField(() => seeded().ticketTypes.create(data), "concertId");
});

test("ticket type: rejects a bad name", () => {
  const data = sampleTicketType(12);
  data.name = "";
  throwsField(() => seeded().ticketTypes.create(data), "name");
});

test("ticket type: rejects a bad price", () => {
  const data = sampleTicketType(12);
  data.price = -5;
  throwsField(() => seeded().ticketTypes.create(data), "price");
});

test("ticket type: rejects a bad quantity", () => {
  const data = sampleTicketType(12);
  data.quantity = -1;
  throwsField(() => seeded().ticketTypes.create(data), "quantity");
});

test("ticket type: rejects a bad sold", () => {
  const data = sampleTicketType(12);
  data.sold = -1;
  throwsField(() => seeded().ticketTypes.create(data), "sold");
});

test("ticket type: rejects a bad seated", () => {
  const data = sampleTicketType(12);
  data.seated = "yes";
  throwsField(() => seeded().ticketTypes.create(data), "seated");
});

test("ticket type: concert id must exist", () => {
  const data = sampleTicketType(13);
  data.concertId = 9999;
  throwsKind(() => seeded().ticketTypes.create(data), NotFoundError);
});

test("ticket type: search name", () => {
  const s = seeded();
  const target = s.ticketTypes.get(2);
  assert(s.store.ticketTypes.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.ticketTypes.findByName(target.name).includes(target), "find missed it");
});

test("ticket type: adjust price", () => {
  const s = seeded();
  const before = s.ticketTypes.get(1).price;
  assert(Math.abs(s.ticketTypes.adjustPrice(1, 1.5).price - (before + 1.5)) < 0.01, "not adjusted");
});

test("ticket type: adjust quantity", () => {
  const s = seeded();
  const before = s.ticketTypes.get(1).quantity;
  assert(s.ticketTypes.adjustQuantity(1, 2).quantity === before + 2, "not adjusted");
  throwsField(() => s.ticketTypes.adjustQuantity(1, -(before + 100)), "quantity");
});

test("ticket type: adjust sold", () => {
  const s = seeded();
  const before = s.ticketTypes.get(1).sold;
  assert(s.ticketTypes.adjustSold(1, 2).sold === before + 2, "not adjusted");
  throwsField(() => s.ticketTypes.adjustSold(1, -(before + 100)), "sold");
});

test("ticket type: toggle seated", () => {
  const s = seeded();
  const before = s.ticketTypes.get(1).seated;
  assert(s.ticketTypes.toggleSeated(1).seated === !before, "flag not flipped");
});

test("ticket type: delete an unused record", () => {
  const s = seeded();
  const item = s.ticketTypes.create(sampleTicketType(14));
  s.ticketTypes.delete(item.id);
  throwsKind(() => s.ticketTypes.get(item.id), NotFoundError);
});

test("ticket type: delete a record in use", () => {
  throwsKind(() => seeded().ticketTypes.delete(1), ConflictError);
});

test("ticket type: stats and queries", () => {
  const s = seeded();
  assert(s.ticketTypes.stats().count === 3, "wrong count");
  const newest = queryTicketTypes(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryTicketTypes(s.store, { sort: "nope" }), "sort");
  assert(describeTicketType().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- Attendee

test("attendee: create and get", () => {
  const s = seeded();
  const item = s.attendees.create(sampleAttendee(10));
  assert(s.attendees.get(item.id) === item, "stored record differs");
  assert(s.attendees.list().length === 4, "list should have 4 records");
});

test("attendee: missing record", () => {
  throwsKind(() => seeded().attendees.get(9999), NotFoundError);
});

test("attendee: unknown field", () => {
  const data = sampleAttendee(11);
  data.noSuchField = 1;
  throwsField(() => seeded().attendees.create(data), "noSuchField");
});

test("attendee: id can't be chosen", () => {
  const data = sampleAttendee(11);
  data.id = 42;
  throwsField(() => seeded().attendees.create(data), "id");
});

test("attendee: rejects a bad name", () => {
  const data = sampleAttendee(12);
  data.name = "";
  throwsField(() => seeded().attendees.create(data), "name");
});

test("attendee: rejects a bad email", () => {
  const data = sampleAttendee(12);
  data.email = "not-an-email";
  throwsField(() => seeded().attendees.create(data), "email");
});

test("attendee: rejects a bad phone", () => {
  const data = sampleAttendee(12);
  data.phone = "";
  throwsField(() => seeded().attendees.create(data), "phone");
});

test("attendee: rejects a bad country", () => {
  const data = sampleAttendee(12);
  data.country = "";
  throwsField(() => seeded().attendees.create(data), "country");
});

test("attendee: rejects a bad newsletter", () => {
  const data = sampleAttendee(12);
  data.newsletter = "yes";
  throwsField(() => seeded().attendees.create(data), "newsletter");
});

test("attendee: search name", () => {
  const s = seeded();
  const target = s.attendees.get(2);
  assert(s.store.attendees.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.attendees.findByName(target.name).includes(target), "find missed it");
});

test("attendee: search email", () => {
  const s = seeded();
  const target = s.attendees.get(2);
  assert(s.store.attendees.searchEmail(target.email.toUpperCase()).includes(target), "search missed it");
  assert(s.store.attendees.findByEmail(target.email).includes(target), "find missed it");
});

test("attendee: search phone", () => {
  const s = seeded();
  const target = s.attendees.get(2);
  assert(s.store.attendees.searchPhone(target.phone.toUpperCase()).includes(target), "search missed it");
  assert(s.store.attendees.findByPhone(target.phone).includes(target), "find missed it");
});

test("attendee: search country", () => {
  const s = seeded();
  const target = s.attendees.get(2);
  assert(s.store.attendees.searchCountry(target.country.toUpperCase()).includes(target), "search missed it");
  assert(s.store.attendees.findByCountry(target.country).includes(target), "find missed it");
});

test("attendee: toggle newsletter", () => {
  const s = seeded();
  const before = s.attendees.get(1).newsletter;
  assert(s.attendees.toggleNewsletter(1).newsletter === !before, "flag not flipped");
});

test("attendee: delete an unused record", () => {
  const s = seeded();
  const item = s.attendees.create(sampleAttendee(14));
  s.attendees.delete(item.id);
  throwsKind(() => s.attendees.get(item.id), NotFoundError);
});

test("attendee: delete a record in use", () => {
  throwsKind(() => seeded().attendees.delete(1), ConflictError);
});

test("attendee: stats and queries", () => {
  const s = seeded();
  assert(s.attendees.stats().count === 3, "wrong count");
  const newest = queryAttendees(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryAttendees(s.store, { sort: "nope" }), "sort");
  assert(describeAttendee().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Ticket

test("ticket: create and get", () => {
  const s = seeded();
  const item = s.tickets.create(sampleTicket(10));
  assert(s.tickets.get(item.id) === item, "stored record differs");
  assert(s.tickets.list().length === 4, "list should have 4 records");
});

test("ticket: missing record", () => {
  throwsKind(() => seeded().tickets.get(9999), NotFoundError);
});

test("ticket: unknown field", () => {
  const data = sampleTicket(11);
  data.noSuchField = 1;
  throwsField(() => seeded().tickets.create(data), "noSuchField");
});

test("ticket: id can't be chosen", () => {
  const data = sampleTicket(11);
  data.id = 42;
  throwsField(() => seeded().tickets.create(data), "id");
});

test("ticket: rejects a bad ticket type id", () => {
  const data = sampleTicket(12);
  data.ticketTypeId = 0;
  throwsField(() => seeded().tickets.create(data), "ticketTypeId");
});

test("ticket: rejects a bad attendee id", () => {
  const data = sampleTicket(12);
  data.attendeeId = 0;
  throwsField(() => seeded().tickets.create(data), "attendeeId");
});

test("ticket: rejects a bad bought", () => {
  const data = sampleTicket(12);
  data.bought = "2026-02-30";
  throwsField(() => seeded().tickets.create(data), "bought");
});

test("ticket: rejects a bad code", () => {
  const data = sampleTicket(12);
  data.code = "";
  throwsField(() => seeded().tickets.create(data), "code");
});

test("ticket: rejects a bad status", () => {
  const data = sampleTicket(12);
  data.status = "nope";
  throwsField(() => seeded().tickets.create(data), "status");
});

test("ticket: rejects a bad price paid", () => {
  const data = sampleTicket(12);
  data.pricePaid = -5;
  throwsField(() => seeded().tickets.create(data), "pricePaid");
});

test("ticket: ticket type id must exist", () => {
  const data = sampleTicket(13);
  data.ticketTypeId = 9999;
  throwsKind(() => seeded().tickets.create(data), NotFoundError);
});

test("ticket: attendee id must exist", () => {
  const data = sampleTicket(13);
  data.attendeeId = 9999;
  throwsKind(() => seeded().tickets.create(data), NotFoundError);
});

test("ticket: bought ranges", () => {
  const s = seeded();
  const day = s.tickets.get(2).bought;
  const total = s.store.tickets.boughtBefore(day).length + s.store.tickets.boughtOn(day).length + s.store.tickets.boughtAfter(day).length;
  assert(total === s.store.tickets.count(), "ranges don't cover every record");
});

test("ticket: search code", () => {
  const s = seeded();
  const target = s.tickets.get(2);
  assert(s.store.tickets.searchCode(target.code.toUpperCase()).includes(target), "search missed it");
  assert(s.store.tickets.findByCode(target.code).includes(target), "find missed it");
});

test("ticket: set status", () => {
  const s = seeded();
  assert(s.tickets.setStatus(1, "void").status === "void", "value not changed");
  assert(s.store.tickets.countByStatus()["void"] === s.store.tickets.withStatus("void").length, "counts differ");
});

test("ticket: adjust price paid", () => {
  const s = seeded();
  const before = s.tickets.get(1).pricePaid;
  assert(Math.abs(s.tickets.adjustPricePaid(1, 1.5).pricePaid - (before + 1.5)) < 0.01, "not adjusted");
});

test("ticket: delete an unused record", () => {
  const s = seeded();
  const item = s.tickets.create(sampleTicket(14));
  s.tickets.delete(item.id);
  throwsKind(() => s.tickets.get(item.id), NotFoundError);
});

test("ticket: stats and queries", () => {
  const s = seeded();
  assert(s.tickets.stats().count === 3, "wrong count");
  const newest = queryTickets(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryTickets(s.store, { sort: "nope" }), "sort");
  assert(describeTicket().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- Sponsor

test("sponsor: create and get", () => {
  const s = seeded();
  const item = s.sponsors.create(sampleSponsor(10));
  assert(s.sponsors.get(item.id) === item, "stored record differs");
  assert(s.sponsors.list().length === 4, "list should have 4 records");
});

test("sponsor: missing record", () => {
  throwsKind(() => seeded().sponsors.get(9999), NotFoundError);
});

test("sponsor: unknown field", () => {
  const data = sampleSponsor(11);
  data.noSuchField = 1;
  throwsField(() => seeded().sponsors.create(data), "noSuchField");
});

test("sponsor: id can't be chosen", () => {
  const data = sampleSponsor(11);
  data.id = 42;
  throwsField(() => seeded().sponsors.create(data), "id");
});

test("sponsor: rejects a bad concert id", () => {
  const data = sampleSponsor(12);
  data.concertId = 0;
  throwsField(() => seeded().sponsors.create(data), "concertId");
});

test("sponsor: rejects a bad company", () => {
  const data = sampleSponsor(12);
  data.company = "";
  throwsField(() => seeded().sponsors.create(data), "company");
});

test("sponsor: rejects a bad amount", () => {
  const data = sampleSponsor(12);
  data.amount = -5;
  throwsField(() => seeded().sponsors.create(data), "amount");
});

test("sponsor: rejects a bad tier", () => {
  const data = sampleSponsor(12);
  data.tier = "nope";
  throwsField(() => seeded().sponsors.create(data), "tier");
});

test("sponsor: rejects a bad logo url", () => {
  const data = sampleSponsor(12);
  data.logoUrl = "";
  throwsField(() => seeded().sponsors.create(data), "logoUrl");
});

test("sponsor: concert id must exist", () => {
  const data = sampleSponsor(13);
  data.concertId = 9999;
  throwsKind(() => seeded().sponsors.create(data), NotFoundError);
});

test("sponsor: search company", () => {
  const s = seeded();
  const target = s.sponsors.get(2);
  assert(s.store.sponsors.searchCompany(target.company.toUpperCase()).includes(target), "search missed it");
  assert(s.store.sponsors.findByCompany(target.company).includes(target), "find missed it");
});

test("sponsor: adjust amount", () => {
  const s = seeded();
  const before = s.sponsors.get(1).amount;
  assert(Math.abs(s.sponsors.adjustAmount(1, 1.5).amount - (before + 1.5)) < 0.01, "not adjusted");
});

test("sponsor: set tier", () => {
  const s = seeded();
  assert(s.sponsors.setTier(1, "platinum").tier === "platinum", "value not changed");
  assert(s.store.sponsors.countByTier()["platinum"] === s.store.sponsors.withTier("platinum").length, "counts differ");
});

test("sponsor: search logo url", () => {
  const s = seeded();
  const target = s.sponsors.get(2);
  assert(s.store.sponsors.searchLogoUrl(target.logoUrl.toUpperCase()).includes(target), "search missed it");
  assert(s.store.sponsors.findByLogoUrl(target.logoUrl).includes(target), "find missed it");
});

test("sponsor: delete an unused record", () => {
  const s = seeded();
  const item = s.sponsors.create(sampleSponsor(14));
  s.sponsors.delete(item.id);
  throwsKind(() => s.sponsors.get(item.id), NotFoundError);
});

test("sponsor: stats and queries", () => {
  const s = seeded();
  assert(s.sponsors.stats().count === 3, "wrong count");
  const newest = querySponsors(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => querySponsors(s.store, { sort: "nope" }), "sort");
  assert(describeSponsor().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Document

test("document: create and get", () => {
  const s = seeded();
  const item = s.documents.create(sampleDocument(10));
  assert(s.documents.get(item.id) === item, "stored record differs");
  assert(s.documents.list().length === 4, "list should have 4 records");
});

test("document: missing record", () => {
  throwsKind(() => seeded().documents.get(9999), NotFoundError);
});

test("document: unknown field", () => {
  const data = sampleDocument(11);
  data.noSuchField = 1;
  throwsField(() => seeded().documents.create(data), "noSuchField");
});

test("document: id can't be chosen", () => {
  const data = sampleDocument(11);
  data.id = 42;
  throwsField(() => seeded().documents.create(data), "id");
});

test("document: rejects a bad venue id", () => {
  const data = sampleDocument(12);
  data.venueId = 0;
  throwsField(() => seeded().documents.create(data), "venueId");
});

test("document: rejects a bad title", () => {
  const data = sampleDocument(12);
  data.title = "";
  throwsField(() => seeded().documents.create(data), "title");
});

test("document: rejects a bad pages", () => {
  const data = sampleDocument(12);
  data.pages = -1;
  throwsField(() => seeded().documents.create(data), "pages");
});

test("document: rejects a bad signed", () => {
  const data = sampleDocument(12);
  data.signed = "yes";
  throwsField(() => seeded().documents.create(data), "signed");
});

test("document: rejects a bad version", () => {
  const data = sampleDocument(12);
  data.version = -1;
  throwsField(() => seeded().documents.create(data), "version");
});

test("document: rejects a bad issued", () => {
  const data = sampleDocument(12);
  data.issued = "2026-02-30";
  throwsField(() => seeded().documents.create(data), "issued");
});

test("document: venue id must exist", () => {
  const data = sampleDocument(13);
  data.venueId = 9999;
  throwsKind(() => seeded().documents.create(data), NotFoundError);
});

test("document: search title", () => {
  const s = seeded();
  const target = s.documents.get(2);
  assert(s.store.documents.searchTitle(target.title.toUpperCase()).includes(target), "search missed it");
  assert(s.store.documents.findByTitle(target.title).includes(target), "find missed it");
});

test("document: adjust pages", () => {
  const s = seeded();
  const before = s.documents.get(1).pages;
  assert(s.documents.adjustPages(1, 2).pages === before + 2, "not adjusted");
  throwsField(() => s.documents.adjustPages(1, -(before + 100)), "pages");
});

test("document: toggle signed", () => {
  const s = seeded();
  const before = s.documents.get(1).signed;
  assert(s.documents.toggleSigned(1).signed === !before, "flag not flipped");
});

test("document: adjust version", () => {
  const s = seeded();
  const before = s.documents.get(1).version;
  assert(s.documents.adjustVersion(1, 2).version === before + 2, "not adjusted");
  throwsField(() => s.documents.adjustVersion(1, -(before + 100)), "version");
});

test("document: issued ranges", () => {
  const s = seeded();
  const day = s.documents.get(2).issued;
  const total = s.store.documents.issuedBefore(day).length + s.store.documents.issuedOn(day).length + s.store.documents.issuedAfter(day).length;
  assert(total === s.store.documents.count(), "ranges don't cover every record");
});

test("document: delete an unused record", () => {
  const s = seeded();
  const item = s.documents.create(sampleDocument(14));
  s.documents.delete(item.id);
  throwsKind(() => s.documents.get(item.id), NotFoundError);
});

test("document: stats and queries", () => {
  const s = seeded();
  assert(s.documents.stats().count === 3, "wrong count");
  const newest = queryDocuments(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryDocuments(s.store, { sort: "nope" }), "sort");
  assert(describeDocument().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- Notification

test("notification: create and get", () => {
  const s = seeded();
  const item = s.notifications.create(sampleNotification(10));
  assert(s.notifications.get(item.id) === item, "stored record differs");
  assert(s.notifications.list().length === 4, "list should have 4 records");
});

test("notification: missing record", () => {
  throwsKind(() => seeded().notifications.get(9999), NotFoundError);
});

test("notification: unknown field", () => {
  const data = sampleNotification(11);
  data.noSuchField = 1;
  throwsField(() => seeded().notifications.create(data), "noSuchField");
});

test("notification: id can't be chosen", () => {
  const data = sampleNotification(11);
  data.id = 42;
  throwsField(() => seeded().notifications.create(data), "id");
});

test("notification: rejects a bad recipient", () => {
  const data = sampleNotification(12);
  data.recipient = "not-an-email";
  throwsField(() => seeded().notifications.create(data), "recipient");
});

test("notification: rejects a bad title", () => {
  const data = sampleNotification(12);
  data.title = "";
  throwsField(() => seeded().notifications.create(data), "title");
});

test("notification: rejects a bad sent", () => {
  const data = sampleNotification(12);
  data.sent = "2026-02-30";
  throwsField(() => seeded().notifications.create(data), "sent");
});

test("notification: rejects a bad channel", () => {
  const data = sampleNotification(12);
  data.channel = "nope";
  throwsField(() => seeded().notifications.create(data), "channel");
});

test("notification: rejects a bad read", () => {
  const data = sampleNotification(12);
  data.read = "yes";
  throwsField(() => seeded().notifications.create(data), "read");
});

test("notification: search recipient", () => {
  const s = seeded();
  const target = s.notifications.get(2);
  assert(s.store.notifications.searchRecipient(target.recipient.toUpperCase()).includes(target), "search missed it");
  assert(s.store.notifications.findByRecipient(target.recipient).includes(target), "find missed it");
});

test("notification: search title", () => {
  const s = seeded();
  const target = s.notifications.get(2);
  assert(s.store.notifications.searchTitle(target.title.toUpperCase()).includes(target), "search missed it");
  assert(s.store.notifications.findByTitle(target.title).includes(target), "find missed it");
});

test("notification: sent ranges", () => {
  const s = seeded();
  const day = s.notifications.get(2).sent;
  const total = s.store.notifications.sentBefore(day).length + s.store.notifications.sentOn(day).length + s.store.notifications.sentAfter(day).length;
  assert(total === s.store.notifications.count(), "ranges don't cover every record");
});

test("notification: set channel", () => {
  const s = seeded();
  assert(s.notifications.setChannel(1, "push").channel === "push", "value not changed");
  assert(s.store.notifications.countByChannel()["push"] === s.store.notifications.withChannel("push").length, "counts differ");
});

test("notification: toggle read", () => {
  const s = seeded();
  const before = s.notifications.get(1).read;
  assert(s.notifications.toggleRead(1).read === !before, "flag not flipped");
});

test("notification: delete an unused record", () => {
  const s = seeded();
  const item = s.notifications.create(sampleNotification(14));
  s.notifications.delete(item.id);
  throwsKind(() => s.notifications.get(item.id), NotFoundError);
});

test("notification: stats and queries", () => {
  const s = seeded();
  assert(s.notifications.stats().count === 3, "wrong count");
  const newest = queryNotifications(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryNotifications(s.store, { sort: "nope" }), "sort");
  assert(describeNotification().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Address

test("address: create and get", () => {
  const s = seeded();
  const item = s.addresses.create(sampleAddress(10));
  assert(s.addresses.get(item.id) === item, "stored record differs");
  assert(s.addresses.list().length === 4, "list should have 4 records");
});

test("address: missing record", () => {
  throwsKind(() => seeded().addresses.get(9999), NotFoundError);
});

test("address: unknown field", () => {
  const data = sampleAddress(11);
  data.noSuchField = 1;
  throwsField(() => seeded().addresses.create(data), "noSuchField");
});

test("address: id can't be chosen", () => {
  const data = sampleAddress(11);
  data.id = 42;
  throwsField(() => seeded().addresses.create(data), "id");
});

test("address: rejects a bad venue id", () => {
  const data = sampleAddress(12);
  data.venueId = 0;
  throwsField(() => seeded().addresses.create(data), "venueId");
});

test("address: rejects a bad street", () => {
  const data = sampleAddress(12);
  data.street = "";
  throwsField(() => seeded().addresses.create(data), "street");
});

test("address: rejects a bad city", () => {
  const data = sampleAddress(12);
  data.city = "";
  throwsField(() => seeded().addresses.create(data), "city");
});

test("address: rejects a bad postcode", () => {
  const data = sampleAddress(12);
  data.postcode = "";
  throwsField(() => seeded().addresses.create(data), "postcode");
});

test("address: rejects a bad country", () => {
  const data = sampleAddress(12);
  data.country = "";
  throwsField(() => seeded().addresses.create(data), "country");
});

test("address: rejects a bad billing", () => {
  const data = sampleAddress(12);
  data.billing = "yes";
  throwsField(() => seeded().addresses.create(data), "billing");
});

test("address: venue id must exist", () => {
  const data = sampleAddress(13);
  data.venueId = 9999;
  throwsKind(() => seeded().addresses.create(data), NotFoundError);
});

test("address: search street", () => {
  const s = seeded();
  const target = s.addresses.get(2);
  assert(s.store.addresses.searchStreet(target.street.toUpperCase()).includes(target), "search missed it");
  assert(s.store.addresses.findByStreet(target.street).includes(target), "find missed it");
});

test("address: search city", () => {
  const s = seeded();
  const target = s.addresses.get(2);
  assert(s.store.addresses.searchCity(target.city.toUpperCase()).includes(target), "search missed it");
  assert(s.store.addresses.findByCity(target.city).includes(target), "find missed it");
});

test("address: search postcode", () => {
  const s = seeded();
  const target = s.addresses.get(2);
  assert(s.store.addresses.searchPostcode(target.postcode.toUpperCase()).includes(target), "search missed it");
  assert(s.store.addresses.findByPostcode(target.postcode).includes(target), "find missed it");
});

test("address: search country", () => {
  const s = seeded();
  const target = s.addresses.get(2);
  assert(s.store.addresses.searchCountry(target.country.toUpperCase()).includes(target), "search missed it");
  assert(s.store.addresses.findByCountry(target.country).includes(target), "find missed it");
});

test("address: toggle billing", () => {
  const s = seeded();
  const before = s.addresses.get(1).billing;
  assert(s.addresses.toggleBilling(1).billing === !before, "flag not flipped");
});

test("address: delete an unused record", () => {
  const s = seeded();
  const item = s.addresses.create(sampleAddress(14));
  s.addresses.delete(item.id);
  throwsKind(() => s.addresses.get(item.id), NotFoundError);
});

test("address: stats and queries", () => {
  const s = seeded();
  assert(s.addresses.stats().count === 3, "wrong count");
  const newest = queryAddresses(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryAddresses(s.store, { sort: "nope" }), "sort");
  assert(describeAddress().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- Reminder

test("reminder: create and get", () => {
  const s = seeded();
  const item = s.reminders.create(sampleReminder(10));
  assert(s.reminders.get(item.id) === item, "stored record differs");
  assert(s.reminders.list().length === 4, "list should have 4 records");
});

test("reminder: missing record", () => {
  throwsKind(() => seeded().reminders.get(9999), NotFoundError);
});

test("reminder: unknown field", () => {
  const data = sampleReminder(11);
  data.noSuchField = 1;
  throwsField(() => seeded().reminders.create(data), "noSuchField");
});

test("reminder: id can't be chosen", () => {
  const data = sampleReminder(11);
  data.id = 42;
  throwsField(() => seeded().reminders.create(data), "id");
});

test("reminder: rejects a bad venue id", () => {
  const data = sampleReminder(12);
  data.venueId = 0;
  throwsField(() => seeded().reminders.create(data), "venueId");
});

test("reminder: rejects a bad title", () => {
  const data = sampleReminder(12);
  data.title = "";
  throwsField(() => seeded().reminders.create(data), "title");
});

test("reminder: rejects a bad remind on", () => {
  const data = sampleReminder(12);
  data.remindOn = "2026-02-30";
  throwsField(() => seeded().reminders.create(data), "remindOn");
});

test("reminder: rejects a bad done", () => {
  const data = sampleReminder(12);
  data.done = "yes";
  throwsField(() => seeded().reminders.create(data), "done");
});

test("reminder: rejects a bad priority", () => {
  const data = sampleReminder(12);
  data.priority = "nope";
  throwsField(() => seeded().reminders.create(data), "priority");
});

test("reminder: venue id must exist", () => {
  const data = sampleReminder(13);
  data.venueId = 9999;
  throwsKind(() => seeded().reminders.create(data), NotFoundError);
});

test("reminder: search title", () => {
  const s = seeded();
  const target = s.reminders.get(2);
  assert(s.store.reminders.searchTitle(target.title.toUpperCase()).includes(target), "search missed it");
  assert(s.store.reminders.findByTitle(target.title).includes(target), "find missed it");
});

test("reminder: remind on ranges", () => {
  const s = seeded();
  const day = s.reminders.get(2).remindOn;
  const total = s.store.reminders.remindOnBefore(day).length + s.store.reminders.remindOnOn(day).length + s.store.reminders.remindOnAfter(day).length;
  assert(total === s.store.reminders.count(), "ranges don't cover every record");
});

test("reminder: toggle done", () => {
  const s = seeded();
  const before = s.reminders.get(1).done;
  assert(s.reminders.toggleDone(1).done === !before, "flag not flipped");
});

test("reminder: set priority", () => {
  const s = seeded();
  assert(s.reminders.setPriority(1, "high").priority === "high", "value not changed");
  assert(s.store.reminders.countByPriority()["high"] === s.store.reminders.withPriority("high").length, "counts differ");
});

test("reminder: delete an unused record", () => {
  const s = seeded();
  const item = s.reminders.create(sampleReminder(14));
  s.reminders.delete(item.id);
  throwsKind(() => s.reminders.get(item.id), NotFoundError);
});

test("reminder: stats and queries", () => {
  const s = seeded();
  assert(s.reminders.stats().count === 3, "wrong count");
  const newest = queryReminders(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryReminders(s.store, { sort: "nope" }), "sort");
  assert(describeReminder().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Setting

test("setting: create and get", () => {
  const s = seeded();
  const item = s.settings.create(sampleSetting(10));
  assert(s.settings.get(item.id) === item, "stored record differs");
  assert(s.settings.list().length === 4, "list should have 4 records");
});

test("setting: missing record", () => {
  throwsKind(() => seeded().settings.get(9999), NotFoundError);
});

test("setting: unknown field", () => {
  const data = sampleSetting(11);
  data.noSuchField = 1;
  throwsField(() => seeded().settings.create(data), "noSuchField");
});

test("setting: id can't be chosen", () => {
  const data = sampleSetting(11);
  data.id = 42;
  throwsField(() => seeded().settings.create(data), "id");
});

test("setting: rejects a bad key name", () => {
  const data = sampleSetting(12);
  data.keyName = "";
  throwsField(() => seeded().settings.create(data), "keyName");
});

test("setting: rejects a bad value", () => {
  const data = sampleSetting(12);
  data.value = "";
  throwsField(() => seeded().settings.create(data), "value");
});

test("setting: rejects a bad editable", () => {
  const data = sampleSetting(12);
  data.editable = "yes";
  throwsField(() => seeded().settings.create(data), "editable");
});

test("setting: rejects a bad changed", () => {
  const data = sampleSetting(12);
  data.changed = "2026-02-30";
  throwsField(() => seeded().settings.create(data), "changed");
});

test("setting: search key name", () => {
  const s = seeded();
  const target = s.settings.get(2);
  assert(s.store.settings.searchKeyName(target.keyName.toUpperCase()).includes(target), "search missed it");
  assert(s.store.settings.findByKeyName(target.keyName).includes(target), "find missed it");
});

test("setting: search value", () => {
  const s = seeded();
  const target = s.settings.get(2);
  assert(s.store.settings.searchValue(target.value.toUpperCase()).includes(target), "search missed it");
  assert(s.store.settings.findByValue(target.value).includes(target), "find missed it");
});

test("setting: toggle editable", () => {
  const s = seeded();
  const before = s.settings.get(1).editable;
  assert(s.settings.toggleEditable(1).editable === !before, "flag not flipped");
});

test("setting: changed ranges", () => {
  const s = seeded();
  const day = s.settings.get(2).changed;
  const total = s.store.settings.changedBefore(day).length + s.store.settings.changedOn(day).length + s.store.settings.changedAfter(day).length;
  assert(total === s.store.settings.count(), "ranges don't cover every record");
});

test("setting: delete an unused record", () => {
  const s = seeded();
  const item = s.settings.create(sampleSetting(14));
  s.settings.delete(item.id);
  throwsKind(() => s.settings.get(item.id), NotFoundError);
});

test("setting: stats and queries", () => {
  const s = seeded();
  assert(s.settings.stats().count === 3, "wrong count");
  const newest = querySettings(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => querySettings(s.store, { sort: "nope" }), "sort");
  assert(describeSetting().length === 5, "field list incomplete");
});

// ---------------------------------------------------------------------------- AuditEntry

test("audit entry: create and get", () => {
  const s = seeded();
  const item = s.auditEntries.create(sampleAuditEntry(10));
  assert(s.auditEntries.get(item.id) === item, "stored record differs");
  assert(s.auditEntries.list().length === 4, "list should have 4 records");
});

test("audit entry: missing record", () => {
  throwsKind(() => seeded().auditEntries.get(9999), NotFoundError);
});

test("audit entry: unknown field", () => {
  const data = sampleAuditEntry(11);
  data.noSuchField = 1;
  throwsField(() => seeded().auditEntries.create(data), "noSuchField");
});

test("audit entry: id can't be chosen", () => {
  const data = sampleAuditEntry(11);
  data.id = 42;
  throwsField(() => seeded().auditEntries.create(data), "id");
});

test("audit entry: rejects a bad actor", () => {
  const data = sampleAuditEntry(12);
  data.actor = "";
  throwsField(() => seeded().auditEntries.create(data), "actor");
});

test("audit entry: rejects a bad action", () => {
  const data = sampleAuditEntry(12);
  data.action = "nope";
  throwsField(() => seeded().auditEntries.create(data), "action");
});

test("audit entry: rejects a bad at", () => {
  const data = sampleAuditEntry(12);
  data.at = "2026-02-30";
  throwsField(() => seeded().auditEntries.create(data), "at");
});

test("audit entry: rejects a bad details", () => {
  const data = sampleAuditEntry(12);
  data.details = "x".repeat(3000);
  throwsField(() => seeded().auditEntries.create(data), "details");
});

test("audit entry: search actor", () => {
  const s = seeded();
  const target = s.auditEntries.get(2);
  assert(s.store.auditEntries.searchActor(target.actor.toUpperCase()).includes(target), "search missed it");
  assert(s.store.auditEntries.findByActor(target.actor).includes(target), "find missed it");
});

test("audit entry: set action", () => {
  const s = seeded();
  assert(s.auditEntries.setAction(1, "export").action === "export", "value not changed");
  assert(s.store.auditEntries.countByAction()["export"] === s.store.auditEntries.withAction("export").length, "counts differ");
});

test("audit entry: at ranges", () => {
  const s = seeded();
  const day = s.auditEntries.get(2).at;
  const total = s.store.auditEntries.atBefore(day).length + s.store.auditEntries.atOn(day).length + s.store.auditEntries.atAfter(day).length;
  assert(total === s.store.auditEntries.count(), "ranges don't cover every record");
});

test("audit entry: search details", () => {
  const s = seeded();
  const target = s.auditEntries.get(2);
  assert(s.store.auditEntries.searchDetails(target.details.toUpperCase()).includes(target), "search missed it");
  assert(s.store.auditEntries.findByDetails(target.details).includes(target), "find missed it");
});

test("audit entry: delete an unused record", () => {
  const s = seeded();
  const item = s.auditEntries.create(sampleAuditEntry(14));
  s.auditEntries.delete(item.id);
  throwsKind(() => s.auditEntries.get(item.id), NotFoundError);
});

test("audit entry: stats and queries", () => {
  const s = seeded();
  assert(s.auditEntries.stats().count === 3, "wrong count");
  const newest = queryAuditEntries(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryAuditEntries(s.store, { sort: "nope" }), "sort");
  assert(describeAuditEntry().length === 5, "field list incomplete");
});

// ---------------------------------------------------------------------------- Note

test("note: create and get", () => {
  const s = seeded();
  const item = s.notes.create(sampleNote(10));
  assert(s.notes.get(item.id) === item, "stored record differs");
  assert(s.notes.list().length === 4, "list should have 4 records");
});

test("note: missing record", () => {
  throwsKind(() => seeded().notes.get(9999), NotFoundError);
});

test("note: unknown field", () => {
  const data = sampleNote(11);
  data.noSuchField = 1;
  throwsField(() => seeded().notes.create(data), "noSuchField");
});

test("note: id can't be chosen", () => {
  const data = sampleNote(11);
  data.id = 42;
  throwsField(() => seeded().notes.create(data), "id");
});

test("note: rejects a bad venue id", () => {
  const data = sampleNote(12);
  data.venueId = 0;
  throwsField(() => seeded().notes.create(data), "venueId");
});

test("note: rejects a bad subject", () => {
  const data = sampleNote(12);
  data.subject = "";
  throwsField(() => seeded().notes.create(data), "subject");
});

test("note: rejects a bad body", () => {
  const data = sampleNote(12);
  data.body = "x".repeat(3000);
  throwsField(() => seeded().notes.create(data), "body");
});

test("note: rejects a bad pinned", () => {
  const data = sampleNote(12);
  data.pinned = "yes";
  throwsField(() => seeded().notes.create(data), "pinned");
});

test("note: rejects a bad written", () => {
  const data = sampleNote(12);
  data.written = "2026-02-30";
  throwsField(() => seeded().notes.create(data), "written");
});

test("note: venue id must exist", () => {
  const data = sampleNote(13);
  data.venueId = 9999;
  throwsKind(() => seeded().notes.create(data), NotFoundError);
});

test("note: search subject", () => {
  const s = seeded();
  const target = s.notes.get(2);
  assert(s.store.notes.searchSubject(target.subject.toUpperCase()).includes(target), "search missed it");
  assert(s.store.notes.findBySubject(target.subject).includes(target), "find missed it");
});

test("note: search body", () => {
  const s = seeded();
  const target = s.notes.get(2);
  assert(s.store.notes.searchBody(target.body.toUpperCase()).includes(target), "search missed it");
  assert(s.store.notes.findByBody(target.body).includes(target), "find missed it");
});

test("note: toggle pinned", () => {
  const s = seeded();
  const before = s.notes.get(1).pinned;
  assert(s.notes.togglePinned(1).pinned === !before, "flag not flipped");
});

test("note: written ranges", () => {
  const s = seeded();
  const day = s.notes.get(2).written;
  const total = s.store.notes.writtenBefore(day).length + s.store.notes.writtenOn(day).length + s.store.notes.writtenAfter(day).length;
  assert(total === s.store.notes.count(), "ranges don't cover every record");
});

test("note: delete an unused record", () => {
  const s = seeded();
  const item = s.notes.create(sampleNote(14));
  s.notes.delete(item.id);
  throwsKind(() => s.notes.get(item.id), NotFoundError);
});

test("note: stats and queries", () => {
  const s = seeded();
  assert(s.notes.stats().count === 3, "wrong count");
  const newest = queryNotes(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryNotes(s.store, { sort: "nope" }), "sort");
  assert(describeNote().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Review

test("review: create and get", () => {
  const s = seeded();
  const item = s.reviews.create(sampleReview(10));
  assert(s.reviews.get(item.id) === item, "stored record differs");
  assert(s.reviews.list().length === 4, "list should have 4 records");
});

test("review: missing record", () => {
  throwsKind(() => seeded().reviews.get(9999), NotFoundError);
});

test("review: unknown field", () => {
  const data = sampleReview(11);
  data.noSuchField = 1;
  throwsField(() => seeded().reviews.create(data), "noSuchField");
});

test("review: id can't be chosen", () => {
  const data = sampleReview(11);
  data.id = 42;
  throwsField(() => seeded().reviews.create(data), "id");
});

test("review: rejects a bad venue id", () => {
  const data = sampleReview(12);
  data.venueId = 0;
  throwsField(() => seeded().reviews.create(data), "venueId");
});

test("review: rejects a bad author", () => {
  const data = sampleReview(12);
  data.author = "";
  throwsField(() => seeded().reviews.create(data), "author");
});

test("review: rejects a bad stars", () => {
  const data = sampleReview(12);
  data.stars = -1;
  throwsField(() => seeded().reviews.create(data), "stars");
});

test("review: rejects a bad comment", () => {
  const data = sampleReview(12);
  data.comment = "x".repeat(3000);
  throwsField(() => seeded().reviews.create(data), "comment");
});

test("review: rejects a bad verified", () => {
  const data = sampleReview(12);
  data.verified = "yes";
  throwsField(() => seeded().reviews.create(data), "verified");
});

test("review: rejects a bad posted", () => {
  const data = sampleReview(12);
  data.posted = "2026-02-30";
  throwsField(() => seeded().reviews.create(data), "posted");
});

test("review: venue id must exist", () => {
  const data = sampleReview(13);
  data.venueId = 9999;
  throwsKind(() => seeded().reviews.create(data), NotFoundError);
});

test("review: search author", () => {
  const s = seeded();
  const target = s.reviews.get(2);
  assert(s.store.reviews.searchAuthor(target.author.toUpperCase()).includes(target), "search missed it");
  assert(s.store.reviews.findByAuthor(target.author).includes(target), "find missed it");
});

test("review: adjust stars", () => {
  const s = seeded();
  const before = s.reviews.get(1).stars;
  assert(s.reviews.adjustStars(1, 2).stars === before + 2, "not adjusted");
  throwsField(() => s.reviews.adjustStars(1, -(before + 100)), "stars");
});

test("review: search comment", () => {
  const s = seeded();
  const target = s.reviews.get(2);
  assert(s.store.reviews.searchComment(target.comment.toUpperCase()).includes(target), "search missed it");
  assert(s.store.reviews.findByComment(target.comment).includes(target), "find missed it");
});

test("review: toggle verified", () => {
  const s = seeded();
  const before = s.reviews.get(1).verified;
  assert(s.reviews.toggleVerified(1).verified === !before, "flag not flipped");
});

test("review: posted ranges", () => {
  const s = seeded();
  const day = s.reviews.get(2).posted;
  const total = s.store.reviews.postedBefore(day).length + s.store.reviews.postedOn(day).length + s.store.reviews.postedAfter(day).length;
  assert(total === s.store.reviews.count(), "ranges don't cover every record");
});

test("review: delete an unused record", () => {
  const s = seeded();
  const item = s.reviews.create(sampleReview(14));
  s.reviews.delete(item.id);
  throwsKind(() => s.reviews.get(item.id), NotFoundError);
});

test("review: stats and queries", () => {
  const s = seeded();
  assert(s.reviews.stats().count === 3, "wrong count");
  const newest = queryReviews(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryReviews(s.store, { sort: "nope" }), "sort");
  assert(describeReview().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- ContactPerson

test("contact person: create and get", () => {
  const s = seeded();
  const item = s.contactPersons.create(sampleContactPerson(10));
  assert(s.contactPersons.get(item.id) === item, "stored record differs");
  assert(s.contactPersons.list().length === 4, "list should have 4 records");
});

test("contact person: missing record", () => {
  throwsKind(() => seeded().contactPersons.get(9999), NotFoundError);
});

test("contact person: unknown field", () => {
  const data = sampleContactPerson(11);
  data.noSuchField = 1;
  throwsField(() => seeded().contactPersons.create(data), "noSuchField");
});

test("contact person: id can't be chosen", () => {
  const data = sampleContactPerson(11);
  data.id = 42;
  throwsField(() => seeded().contactPersons.create(data), "id");
});

test("contact person: rejects a bad venue id", () => {
  const data = sampleContactPerson(12);
  data.venueId = 0;
  throwsField(() => seeded().contactPersons.create(data), "venueId");
});

test("contact person: rejects a bad name", () => {
  const data = sampleContactPerson(12);
  data.name = "";
  throwsField(() => seeded().contactPersons.create(data), "name");
});

test("contact person: rejects a bad email", () => {
  const data = sampleContactPerson(12);
  data.email = "not-an-email";
  throwsField(() => seeded().contactPersons.create(data), "email");
});

test("contact person: rejects a bad phone", () => {
  const data = sampleContactPerson(12);
  data.phone = "";
  throwsField(() => seeded().contactPersons.create(data), "phone");
});

test("contact person: rejects a bad role", () => {
  const data = sampleContactPerson(12);
  data.role = "";
  throwsField(() => seeded().contactPersons.create(data), "role");
});

test("contact person: rejects a bad primary", () => {
  const data = sampleContactPerson(12);
  data.primary = "yes";
  throwsField(() => seeded().contactPersons.create(data), "primary");
});

test("contact person: venue id must exist", () => {
  const data = sampleContactPerson(13);
  data.venueId = 9999;
  throwsKind(() => seeded().contactPersons.create(data), NotFoundError);
});

test("contact person: search name", () => {
  const s = seeded();
  const target = s.contactPersons.get(2);
  assert(s.store.contactPersons.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.contactPersons.findByName(target.name).includes(target), "find missed it");
});

test("contact person: search email", () => {
  const s = seeded();
  const target = s.contactPersons.get(2);
  assert(s.store.contactPersons.searchEmail(target.email.toUpperCase()).includes(target), "search missed it");
  assert(s.store.contactPersons.findByEmail(target.email).includes(target), "find missed it");
});

test("contact person: search phone", () => {
  const s = seeded();
  const target = s.contactPersons.get(2);
  assert(s.store.contactPersons.searchPhone(target.phone.toUpperCase()).includes(target), "search missed it");
  assert(s.store.contactPersons.findByPhone(target.phone).includes(target), "find missed it");
});

test("contact person: search role", () => {
  const s = seeded();
  const target = s.contactPersons.get(2);
  assert(s.store.contactPersons.searchRole(target.role.toUpperCase()).includes(target), "search missed it");
  assert(s.store.contactPersons.findByRole(target.role).includes(target), "find missed it");
});

test("contact person: toggle primary", () => {
  const s = seeded();
  const before = s.contactPersons.get(1).primary;
  assert(s.contactPersons.togglePrimary(1).primary === !before, "flag not flipped");
});

test("contact person: delete an unused record", () => {
  const s = seeded();
  const item = s.contactPersons.create(sampleContactPerson(14));
  s.contactPersons.delete(item.id);
  throwsKind(() => s.contactPersons.get(item.id), NotFoundError);
});

test("contact person: stats and queries", () => {
  const s = seeded();
  assert(s.contactPersons.stats().count === 3, "wrong count");
  const newest = queryContactPersons(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryContactPersons(s.store, { sort: "nope" }), "sort");
  assert(describeContactPerson().length === 7, "field list incomplete");
});

test("CSV: quotes delimiters and line breaks", () => {
  const output = toCsv(["name", "note"], [["Ticket", "early, bird"]]);
  assert(output === "name,note\r\nTicket,\"early, bird\"\r\n", "CSV quoting was incorrect");
});

test("reports: summarize ticket sales and remaining capacity", () => {
  const rows = ticketSales([
    { id: 2, concertId: 2, name: "Balcony", price: 40, quantity: 20, sold: 5, seated: true },
    { id: 1, concertId: 1, name: "General", price: 25, quantity: 100, sold: 12, seated: false },
  ]);
  assert(rows[0].concertId === 1 && rows[0].remaining === 88 && rows[0].gross === 300,
    "ticket sales summary was incorrect");
  assert(ticketSalesCsv([]) === "ticketTypeId,concertId,name,sold,remaining,gross\r\n",
    "empty report header was incorrect");
});

console.log(`${passed} passed, ${failures.length} failed`);
for (const failure of failures) {
  console.log(`FAIL ${failure}`);
}
if (failures.length > 0) {
  throw new Error(`${failures.length} test(s) failed`);
}
