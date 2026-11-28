/**
 * Query layer for the Event Ticketing kit: filters, search, sorting and paging driven by
 * plain string parameters (as they arrive from a URL or a form), plus field descriptions.
 */

import {
  AUDIT_ENTRY_ACTION_VALUES,
  Address,
  Attendee,
  AuditEntry,
  CONCERT_STATUS_VALUES,
  Concert,
  ContactPerson,
  Document,
  NOTIFICATION_CHANNEL_VALUES,
  Note,
  Notification,
  REMINDER_PRIORITY_VALUES,
  Reminder,
  Review,
  SPONSOR_TIER_VALUES,
  Setting,
  Sponsor,
  TICKET_STATUS_VALUES,
  Ticket,
  TicketType,
  ValidationError,
  Venue,
  checkChoice,
  checkDate,
  compareAddressByCity,
  compareAddressByCountry,
  compareAddressByPostcode,
  compareAddressByStreet,
  compareAddressByVenueId,
  compareAttendeeByCountry,
  compareAttendeeByEmail,
  compareAttendeeByName,
  compareAttendeeByPhone,
  compareAuditEntryByAction,
  compareAuditEntryByActor,
  compareAuditEntryByAt,
  compareAuditEntryByDetails,
  compareConcertByArtist,
  compareConcertByDay,
  compareConcertByDoorsOpen,
  compareConcertByStatus,
  compareConcertByTitle,
  compareConcertByVenueId,
  compareContactPersonByEmail,
  compareContactPersonByName,
  compareContactPersonByPhone,
  compareContactPersonByRole,
  compareContactPersonByVenueId,
  compareDocumentByIssued,
  compareDocumentByPages,
  compareDocumentByTitle,
  compareDocumentByVenueId,
  compareDocumentByVersion,
  compareNoteByBody,
  compareNoteBySubject,
  compareNoteByVenueId,
  compareNoteByWritten,
  compareNotificationByChannel,
  compareNotificationByRecipient,
  compareNotificationBySent,
  compareNotificationByTitle,
  compareReminderByPriority,
  compareReminderByRemindOn,
  compareReminderByTitle,
  compareReminderByVenueId,
  compareReviewByAuthor,
  compareReviewByComment,
  compareReviewByPosted,
  compareReviewByStars,
  compareReviewByVenueId,
  compareSettingByChanged,
  compareSettingByKeyName,
  compareSettingByValue,
  compareSponsorByAmount,
  compareSponsorByCompany,
  compareSponsorByConcertId,
  compareSponsorByLogoUrl,
  compareSponsorByTier,
  compareTicketByAttendeeId,
  compareTicketByBought,
  compareTicketByCode,
  compareTicketByPricePaid,
  compareTicketByStatus,
  compareTicketByTicketTypeId,
  compareTicketTypeByConcertId,
  compareTicketTypeByName,
  compareTicketTypeByPrice,
  compareTicketTypeByQuantity,
  compareTicketTypeBySold,
  compareVenueByAddress,
  compareVenueByCapacity,
  compareVenueByCity,
  compareVenueByName,
} from "./models";
import { Store } from "./services";

export type Query = Record<string, string>;

export interface FieldInfo {
  field: string;
  kind: string;
  rule: string;
}

function numberParam(query: Query, name: string): number {
  const raw = query[name].trim();
  const value = Number(raw);
  if (raw === "" || !Number.isFinite(value)) {
    throw new ValidationError(name, "must be a number");
  }
  return value;
}

function flagParam(query: Query, name: string): boolean {
  const raw = query[name].toLowerCase();
  if (["1", "true", "yes"].includes(raw)) {
    return true;
  }
  if (["0", "false", "no"].includes(raw)) {
    return false;
  }
  throw new ValidationError(name, "must be true or false");
}

/** One page of items (?page= from 1, ?size= up to 200). */
export function paginate<T>(items: T[], query: Query): T[] {
  const page = query.page !== undefined ? Math.max(1, Math.floor(numberParam(query, "page"))) : 1;
  const size = query.size !== undefined ? Math.min(200, Math.max(1, Math.floor(numberParam(query, "size")))) : 50;
  const start = (page - 1) * size;
  return items.slice(start, start + size);
}

function sortWith<T>(items: T[], sort: string | undefined, comparers: Record<string, (a: T, b: T) => number>): T[] {
  if (!sort) {
    return items;
  }
  const descending = sort.startsWith("-");
  const key = descending ? sort.slice(1) : sort;
  const compare = comparers[key];
  if (!compare) {
    throw new ValidationError("sort", `can't sort on ${key}`);
  }
  const sorted = [...items].sort(compare);
  return descending ? sorted.reverse() : sorted;
}

const RULES: Record<string, string> = {
  str: "required, up to 120 characters",
  text: "optional, up to 2000 characters",
  email: "required e-mail address",
  int: "whole number, 0 or more",
  float: "number, 0 or more",
  money: "amount, 0 or more, rounded to cents",
  bool: "true or false",
  date: "date, YYYY-MM-DD",
  enum: "one of the listed values",
  ref: "id of an existing record",
};

const VENUE_COMPARERS: Record<string, (a: Venue, b: Venue) => number> = {
  id: (a, b) => a.id - b.id,
  name: compareVenueByName,
  city: compareVenueByCity,
  capacity: compareVenueByCapacity,
  address: compareVenueByAddress,
};

/** Venues matching the query parameters. */
export function queryVenues(store: Store, query: Query): Venue[] {
  let items = store.venues.list();
  if (query.q !== undefined) {
    const hits = new Set(store.venues.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.name !== undefined) {
    const wanted = query.name;
    items = items.filter((item) => item.name === wanted);
  }
  if (query.city !== undefined) {
    const wanted = query.city;
    items = items.filter((item) => item.city === wanted);
  }
  if (query.minCapacity !== undefined) {
    const limit = numberParam(query, "minCapacity");
    items = items.filter((item) => item.capacity >= limit);
  }
  if (query.maxCapacity !== undefined) {
    const limit = numberParam(query, "maxCapacity");
    items = items.filter((item) => item.capacity <= limit);
  }
  if (query.address !== undefined) {
    const wanted = query.address;
    items = items.filter((item) => item.address === wanted);
  }
  if (query.accessible !== undefined) {
    const wanted = flagParam(query, "accessible");
    items = items.filter((item) => item.accessible === wanted);
  }
  return paginate(sortWith(items, query.sort, VENUE_COMPARERS), query);
}

/** What each venue field holds and the rule it must follow. */
export function describeVenue(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "city", kind: "str", rule: RULES.str },
    { field: "capacity", kind: "int", rule: RULES.int },
    { field: "address", kind: "str", rule: RULES.str },
    { field: "accessible", kind: "bool", rule: RULES.bool },
  ];
}

const CONCERT_COMPARERS: Record<string, (a: Concert, b: Concert) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareConcertByVenueId,
  title: compareConcertByTitle,
  artist: compareConcertByArtist,
  day: compareConcertByDay,
  doorsOpen: compareConcertByDoorsOpen,
  status: compareConcertByStatus,
};

/** Concerts matching the query parameters. */
export function queryConcerts(store: Store, query: Query): Concert[] {
  let items = store.concerts.list();
  if (query.q !== undefined) {
    const hits = new Set(store.concerts.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.title !== undefined) {
    const wanted = query.title;
    items = items.filter((item) => item.title === wanted);
  }
  if (query.artist !== undefined) {
    const wanted = query.artist;
    items = items.filter((item) => item.artist === wanted);
  }
  if (query.dayFrom !== undefined) {
    const day = checkDate("dayFrom", query.dayFrom);
    items = items.filter((item) => item.day >= day);
  }
  if (query.dayTo !== undefined) {
    const day = checkDate("dayTo", query.dayTo);
    items = items.filter((item) => item.day <= day);
  }
  if (query.doorsOpen !== undefined) {
    const wanted = query.doorsOpen;
    items = items.filter((item) => item.doorsOpen === wanted);
  }
  if (query.status !== undefined) {
    const wanted = checkChoice("status", query.status, CONCERT_STATUS_VALUES);
    items = items.filter((item) => item.status === wanted);
  }
  return paginate(sortWith(items, query.sort, CONCERT_COMPARERS), query);
}

/** What each concert field holds and the rule it must follow. */
export function describeConcert(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "title", kind: "str", rule: RULES.str },
    { field: "artist", kind: "str", rule: RULES.str },
    { field: "day", kind: "date", rule: RULES.date },
    { field: "doorsOpen", kind: "str", rule: RULES.str },
    { field: "status", kind: "enum", rule: RULES.enum },
  ];
}

const TICKET_TYPE_COMPARERS: Record<string, (a: TicketType, b: TicketType) => number> = {
  id: (a, b) => a.id - b.id,
  concertId: compareTicketTypeByConcertId,
  name: compareTicketTypeByName,
  price: compareTicketTypeByPrice,
  quantity: compareTicketTypeByQuantity,
  sold: compareTicketTypeBySold,
};

/** Ticket types matching the query parameters. */
export function queryTicketTypes(store: Store, query: Query): TicketType[] {
  let items = store.ticketTypes.list();
  if (query.q !== undefined) {
    const hits = new Set(store.ticketTypes.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.concertId !== undefined) {
    const wanted = numberParam(query, "concertId");
    items = items.filter((item) => item.concertId === wanted);
  }
  if (query.name !== undefined) {
    const wanted = query.name;
    items = items.filter((item) => item.name === wanted);
  }
  if (query.minPrice !== undefined) {
    const limit = numberParam(query, "minPrice");
    items = items.filter((item) => item.price >= limit);
  }
  if (query.maxPrice !== undefined) {
    const limit = numberParam(query, "maxPrice");
    items = items.filter((item) => item.price <= limit);
  }
  if (query.minQuantity !== undefined) {
    const limit = numberParam(query, "minQuantity");
    items = items.filter((item) => item.quantity >= limit);
  }
  if (query.maxQuantity !== undefined) {
    const limit = numberParam(query, "maxQuantity");
    items = items.filter((item) => item.quantity <= limit);
  }
  if (query.minSold !== undefined) {
    const limit = numberParam(query, "minSold");
    items = items.filter((item) => item.sold >= limit);
  }
  if (query.maxSold !== undefined) {
    const limit = numberParam(query, "maxSold");
    items = items.filter((item) => item.sold <= limit);
  }
  if (query.seated !== undefined) {
    const wanted = flagParam(query, "seated");
    items = items.filter((item) => item.seated === wanted);
  }
  return paginate(sortWith(items, query.sort, TICKET_TYPE_COMPARERS), query);
}

/** What each ticket type field holds and the rule it must follow. */
export function describeTicketType(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "concertId", kind: "ref", rule: RULES.ref },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "price", kind: "money", rule: RULES.money },
    { field: "quantity", kind: "int", rule: RULES.int },
    { field: "sold", kind: "int", rule: RULES.int },
    { field: "seated", kind: "bool", rule: RULES.bool },
  ];
}

const ATTENDEE_COMPARERS: Record<string, (a: Attendee, b: Attendee) => number> = {
  id: (a, b) => a.id - b.id,
  name: compareAttendeeByName,
  email: compareAttendeeByEmail,
  phone: compareAttendeeByPhone,
  country: compareAttendeeByCountry,
};

/** Attendees matching the query parameters. */
export function queryAttendees(store: Store, query: Query): Attendee[] {
  let items = store.attendees.list();
  if (query.q !== undefined) {
    const hits = new Set(store.attendees.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.name !== undefined) {
    const wanted = query.name;
    items = items.filter((item) => item.name === wanted);
  }
  if (query.email !== undefined) {
    const wanted = query.email;
    items = items.filter((item) => item.email === wanted);
  }
  if (query.phone !== undefined) {
    const wanted = query.phone;
    items = items.filter((item) => item.phone === wanted);
  }
  if (query.country !== undefined) {
    const wanted = query.country;
    items = items.filter((item) => item.country === wanted);
  }
  if (query.newsletter !== undefined) {
    const wanted = flagParam(query, "newsletter");
    items = items.filter((item) => item.newsletter === wanted);
  }
  return paginate(sortWith(items, query.sort, ATTENDEE_COMPARERS), query);
}

/** What each attendee field holds and the rule it must follow. */
export function describeAttendee(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "email", kind: "email", rule: RULES.email },
    { field: "phone", kind: "str", rule: RULES.str },
    { field: "country", kind: "str", rule: RULES.str },
    { field: "newsletter", kind: "bool", rule: RULES.bool },
  ];
}

const TICKET_COMPARERS: Record<string, (a: Ticket, b: Ticket) => number> = {
  id: (a, b) => a.id - b.id,
  ticketTypeId: compareTicketByTicketTypeId,
  attendeeId: compareTicketByAttendeeId,
  bought: compareTicketByBought,
  code: compareTicketByCode,
  status: compareTicketByStatus,
  pricePaid: compareTicketByPricePaid,
};

/** Tickets matching the query parameters. */
export function queryTickets(store: Store, query: Query): Ticket[] {
  let items = store.tickets.list();
  if (query.q !== undefined) {
    const hits = new Set(store.tickets.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.ticketTypeId !== undefined) {
    const wanted = numberParam(query, "ticketTypeId");
    items = items.filter((item) => item.ticketTypeId === wanted);
  }
  if (query.attendeeId !== undefined) {
    const wanted = numberParam(query, "attendeeId");
    items = items.filter((item) => item.attendeeId === wanted);
  }
  if (query.boughtFrom !== undefined) {
    const day = checkDate("boughtFrom", query.boughtFrom);
    items = items.filter((item) => item.bought >= day);
  }
  if (query.boughtTo !== undefined) {
    const day = checkDate("boughtTo", query.boughtTo);
    items = items.filter((item) => item.bought <= day);
  }
  if (query.code !== undefined) {
    const wanted = query.code;
    items = items.filter((item) => item.code === wanted);
  }
  if (query.status !== undefined) {
    const wanted = checkChoice("status", query.status, TICKET_STATUS_VALUES);
    items = items.filter((item) => item.status === wanted);
  }
  if (query.minPricePaid !== undefined) {
    const limit = numberParam(query, "minPricePaid");
    items = items.filter((item) => item.pricePaid >= limit);
  }
  if (query.maxPricePaid !== undefined) {
    const limit = numberParam(query, "maxPricePaid");
    items = items.filter((item) => item.pricePaid <= limit);
  }
  return paginate(sortWith(items, query.sort, TICKET_COMPARERS), query);
}

/** What each ticket field holds and the rule it must follow. */
export function describeTicket(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "ticketTypeId", kind: "ref", rule: RULES.ref },
    { field: "attendeeId", kind: "ref", rule: RULES.ref },
    { field: "bought", kind: "date", rule: RULES.date },
    { field: "code", kind: "str", rule: RULES.str },
    { field: "status", kind: "enum", rule: RULES.enum },
    { field: "pricePaid", kind: "money", rule: RULES.money },
  ];
}

const SPONSOR_COMPARERS: Record<string, (a: Sponsor, b: Sponsor) => number> = {
  id: (a, b) => a.id - b.id,
  concertId: compareSponsorByConcertId,
  company: compareSponsorByCompany,
  amount: compareSponsorByAmount,
  tier: compareSponsorByTier,
  logoUrl: compareSponsorByLogoUrl,
};

/** Sponsors matching the query parameters. */
export function querySponsors(store: Store, query: Query): Sponsor[] {
  let items = store.sponsors.list();
  if (query.q !== undefined) {
    const hits = new Set(store.sponsors.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.concertId !== undefined) {
    const wanted = numberParam(query, "concertId");
    items = items.filter((item) => item.concertId === wanted);
  }
  if (query.company !== undefined) {
    const wanted = query.company;
    items = items.filter((item) => item.company === wanted);
  }
  if (query.minAmount !== undefined) {
    const limit = numberParam(query, "minAmount");
    items = items.filter((item) => item.amount >= limit);
  }
  if (query.maxAmount !== undefined) {
    const limit = numberParam(query, "maxAmount");
    items = items.filter((item) => item.amount <= limit);
  }
  if (query.tier !== undefined) {
    const wanted = checkChoice("tier", query.tier, SPONSOR_TIER_VALUES);
    items = items.filter((item) => item.tier === wanted);
  }
  if (query.logoUrl !== undefined) {
    const wanted = query.logoUrl;
    items = items.filter((item) => item.logoUrl === wanted);
  }
  return paginate(sortWith(items, query.sort, SPONSOR_COMPARERS), query);
}

/** What each sponsor field holds and the rule it must follow. */
export function describeSponsor(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "concertId", kind: "ref", rule: RULES.ref },
    { field: "company", kind: "str", rule: RULES.str },
    { field: "amount", kind: "money", rule: RULES.money },
    { field: "tier", kind: "enum", rule: RULES.enum },
    { field: "logoUrl", kind: "str", rule: RULES.str },
  ];
}

const DOCUMENT_COMPARERS: Record<string, (a: Document, b: Document) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareDocumentByVenueId,
  title: compareDocumentByTitle,
  pages: compareDocumentByPages,
  version: compareDocumentByVersion,
  issued: compareDocumentByIssued,
};

/** Documents matching the query parameters. */
export function queryDocuments(store: Store, query: Query): Document[] {
  let items = store.documents.list();
  if (query.q !== undefined) {
    const hits = new Set(store.documents.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.title !== undefined) {
    const wanted = query.title;
    items = items.filter((item) => item.title === wanted);
  }
  if (query.minPages !== undefined) {
    const limit = numberParam(query, "minPages");
    items = items.filter((item) => item.pages >= limit);
  }
  if (query.maxPages !== undefined) {
    const limit = numberParam(query, "maxPages");
    items = items.filter((item) => item.pages <= limit);
  }
  if (query.signed !== undefined) {
    const wanted = flagParam(query, "signed");
    items = items.filter((item) => item.signed === wanted);
  }
  if (query.minVersion !== undefined) {
    const limit = numberParam(query, "minVersion");
    items = items.filter((item) => item.version >= limit);
  }
  if (query.maxVersion !== undefined) {
    const limit = numberParam(query, "maxVersion");
    items = items.filter((item) => item.version <= limit);
  }
  if (query.issuedFrom !== undefined) {
    const day = checkDate("issuedFrom", query.issuedFrom);
    items = items.filter((item) => item.issued >= day);
  }
  if (query.issuedTo !== undefined) {
    const day = checkDate("issuedTo", query.issuedTo);
    items = items.filter((item) => item.issued <= day);
  }
  return paginate(sortWith(items, query.sort, DOCUMENT_COMPARERS), query);
}

/** What each document field holds and the rule it must follow. */
export function describeDocument(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "title", kind: "str", rule: RULES.str },
    { field: "pages", kind: "int", rule: RULES.int },
    { field: "signed", kind: "bool", rule: RULES.bool },
    { field: "version", kind: "int", rule: RULES.int },
    { field: "issued", kind: "date", rule: RULES.date },
  ];
}

const NOTIFICATION_COMPARERS: Record<string, (a: Notification, b: Notification) => number> = {
  id: (a, b) => a.id - b.id,
  recipient: compareNotificationByRecipient,
  title: compareNotificationByTitle,
  sent: compareNotificationBySent,
  channel: compareNotificationByChannel,
};

/** Notifications matching the query parameters. */
export function queryNotifications(store: Store, query: Query): Notification[] {
  let items = store.notifications.list();
  if (query.q !== undefined) {
    const hits = new Set(store.notifications.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.recipient !== undefined) {
    const wanted = query.recipient;
    items = items.filter((item) => item.recipient === wanted);
  }
  if (query.title !== undefined) {
    const wanted = query.title;
    items = items.filter((item) => item.title === wanted);
  }
  if (query.sentFrom !== undefined) {
    const day = checkDate("sentFrom", query.sentFrom);
    items = items.filter((item) => item.sent >= day);
  }
  if (query.sentTo !== undefined) {
    const day = checkDate("sentTo", query.sentTo);
    items = items.filter((item) => item.sent <= day);
  }
  if (query.channel !== undefined) {
    const wanted = checkChoice("channel", query.channel, NOTIFICATION_CHANNEL_VALUES);
    items = items.filter((item) => item.channel === wanted);
  }
  if (query.read !== undefined) {
    const wanted = flagParam(query, "read");
    items = items.filter((item) => item.read === wanted);
  }
  return paginate(sortWith(items, query.sort, NOTIFICATION_COMPARERS), query);
}

/** What each notification field holds and the rule it must follow. */
export function describeNotification(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "recipient", kind: "email", rule: RULES.email },
    { field: "title", kind: "str", rule: RULES.str },
    { field: "sent", kind: "date", rule: RULES.date },
    { field: "channel", kind: "enum", rule: RULES.enum },
    { field: "read", kind: "bool", rule: RULES.bool },
  ];
}

const ADDRESS_COMPARERS: Record<string, (a: Address, b: Address) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareAddressByVenueId,
  street: compareAddressByStreet,
  city: compareAddressByCity,
  postcode: compareAddressByPostcode,
  country: compareAddressByCountry,
};

/** Addresses matching the query parameters. */
export function queryAddresses(store: Store, query: Query): Address[] {
  let items = store.addresses.list();
  if (query.q !== undefined) {
    const hits = new Set(store.addresses.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.street !== undefined) {
    const wanted = query.street;
    items = items.filter((item) => item.street === wanted);
  }
  if (query.city !== undefined) {
    const wanted = query.city;
    items = items.filter((item) => item.city === wanted);
  }
  if (query.postcode !== undefined) {
    const wanted = query.postcode;
    items = items.filter((item) => item.postcode === wanted);
  }
  if (query.country !== undefined) {
    const wanted = query.country;
    items = items.filter((item) => item.country === wanted);
  }
  if (query.billing !== undefined) {
    const wanted = flagParam(query, "billing");
    items = items.filter((item) => item.billing === wanted);
  }
  return paginate(sortWith(items, query.sort, ADDRESS_COMPARERS), query);
}

/** What each address field holds and the rule it must follow. */
export function describeAddress(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "street", kind: "str", rule: RULES.str },
    { field: "city", kind: "str", rule: RULES.str },
    { field: "postcode", kind: "str", rule: RULES.str },
    { field: "country", kind: "str", rule: RULES.str },
    { field: "billing", kind: "bool", rule: RULES.bool },
  ];
}

const REMINDER_COMPARERS: Record<string, (a: Reminder, b: Reminder) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareReminderByVenueId,
  title: compareReminderByTitle,
  remindOn: compareReminderByRemindOn,
  priority: compareReminderByPriority,
};

/** Reminders matching the query parameters. */
export function queryReminders(store: Store, query: Query): Reminder[] {
  let items = store.reminders.list();
  if (query.q !== undefined) {
    const hits = new Set(store.reminders.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.title !== undefined) {
    const wanted = query.title;
    items = items.filter((item) => item.title === wanted);
  }
  if (query.remindOnFrom !== undefined) {
    const day = checkDate("remindOnFrom", query.remindOnFrom);
    items = items.filter((item) => item.remindOn >= day);
  }
  if (query.remindOnTo !== undefined) {
    const day = checkDate("remindOnTo", query.remindOnTo);
    items = items.filter((item) => item.remindOn <= day);
  }
  if (query.done !== undefined) {
    const wanted = flagParam(query, "done");
    items = items.filter((item) => item.done === wanted);
  }
  if (query.priority !== undefined) {
    const wanted = checkChoice("priority", query.priority, REMINDER_PRIORITY_VALUES);
    items = items.filter((item) => item.priority === wanted);
  }
  return paginate(sortWith(items, query.sort, REMINDER_COMPARERS), query);
}

/** What each reminder field holds and the rule it must follow. */
export function describeReminder(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "title", kind: "str", rule: RULES.str },
    { field: "remindOn", kind: "date", rule: RULES.date },
    { field: "done", kind: "bool", rule: RULES.bool },
    { field: "priority", kind: "enum", rule: RULES.enum },
  ];
}

const SETTING_COMPARERS: Record<string, (a: Setting, b: Setting) => number> = {
  id: (a, b) => a.id - b.id,
  keyName: compareSettingByKeyName,
  value: compareSettingByValue,
  changed: compareSettingByChanged,
};

/** Settings matching the query parameters. */
export function querySettings(store: Store, query: Query): Setting[] {
  let items = store.settings.list();
  if (query.q !== undefined) {
    const hits = new Set(store.settings.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.keyName !== undefined) {
    const wanted = query.keyName;
    items = items.filter((item) => item.keyName === wanted);
  }
  if (query.value !== undefined) {
    const wanted = query.value;
    items = items.filter((item) => item.value === wanted);
  }
  if (query.editable !== undefined) {
    const wanted = flagParam(query, "editable");
    items = items.filter((item) => item.editable === wanted);
  }
  if (query.changedFrom !== undefined) {
    const day = checkDate("changedFrom", query.changedFrom);
    items = items.filter((item) => item.changed >= day);
  }
  if (query.changedTo !== undefined) {
    const day = checkDate("changedTo", query.changedTo);
    items = items.filter((item) => item.changed <= day);
  }
  return paginate(sortWith(items, query.sort, SETTING_COMPARERS), query);
}

/** What each setting field holds and the rule it must follow. */
export function describeSetting(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "keyName", kind: "str", rule: RULES.str },
    { field: "value", kind: "str", rule: RULES.str },
    { field: "editable", kind: "bool", rule: RULES.bool },
    { field: "changed", kind: "date", rule: RULES.date },
  ];
}

const AUDIT_ENTRY_COMPARERS: Record<string, (a: AuditEntry, b: AuditEntry) => number> = {
  id: (a, b) => a.id - b.id,
  actor: compareAuditEntryByActor,
  action: compareAuditEntryByAction,
  at: compareAuditEntryByAt,
  details: compareAuditEntryByDetails,
};

/** Audit entries matching the query parameters. */
export function queryAuditEntries(store: Store, query: Query): AuditEntry[] {
  let items = store.auditEntries.list();
  if (query.q !== undefined) {
    const hits = new Set(store.auditEntries.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.actor !== undefined) {
    const wanted = query.actor;
    items = items.filter((item) => item.actor === wanted);
  }
  if (query.action !== undefined) {
    const wanted = checkChoice("action", query.action, AUDIT_ENTRY_ACTION_VALUES);
    items = items.filter((item) => item.action === wanted);
  }
  if (query.atFrom !== undefined) {
    const day = checkDate("atFrom", query.atFrom);
    items = items.filter((item) => item.at >= day);
  }
  if (query.atTo !== undefined) {
    const day = checkDate("atTo", query.atTo);
    items = items.filter((item) => item.at <= day);
  }
  if (query.details !== undefined) {
    const wanted = query.details;
    items = items.filter((item) => item.details === wanted);
  }
  return paginate(sortWith(items, query.sort, AUDIT_ENTRY_COMPARERS), query);
}

/** What each audit entry field holds and the rule it must follow. */
export function describeAuditEntry(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "actor", kind: "str", rule: RULES.str },
    { field: "action", kind: "enum", rule: RULES.enum },
    { field: "at", kind: "date", rule: RULES.date },
    { field: "details", kind: "text", rule: RULES.text },
  ];
}

const NOTE_COMPARERS: Record<string, (a: Note, b: Note) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareNoteByVenueId,
  subject: compareNoteBySubject,
  body: compareNoteByBody,
  written: compareNoteByWritten,
};

/** Notes matching the query parameters. */
export function queryNotes(store: Store, query: Query): Note[] {
  let items = store.notes.list();
  if (query.q !== undefined) {
    const hits = new Set(store.notes.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.subject !== undefined) {
    const wanted = query.subject;
    items = items.filter((item) => item.subject === wanted);
  }
  if (query.body !== undefined) {
    const wanted = query.body;
    items = items.filter((item) => item.body === wanted);
  }
  if (query.pinned !== undefined) {
    const wanted = flagParam(query, "pinned");
    items = items.filter((item) => item.pinned === wanted);
  }
  if (query.writtenFrom !== undefined) {
    const day = checkDate("writtenFrom", query.writtenFrom);
    items = items.filter((item) => item.written >= day);
  }
  if (query.writtenTo !== undefined) {
    const day = checkDate("writtenTo", query.writtenTo);
    items = items.filter((item) => item.written <= day);
  }
  return paginate(sortWith(items, query.sort, NOTE_COMPARERS), query);
}

/** What each note field holds and the rule it must follow. */
export function describeNote(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "subject", kind: "str", rule: RULES.str },
    { field: "body", kind: "text", rule: RULES.text },
    { field: "pinned", kind: "bool", rule: RULES.bool },
    { field: "written", kind: "date", rule: RULES.date },
  ];
}

const REVIEW_COMPARERS: Record<string, (a: Review, b: Review) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareReviewByVenueId,
  author: compareReviewByAuthor,
  stars: compareReviewByStars,
  comment: compareReviewByComment,
  posted: compareReviewByPosted,
};

/** Reviews matching the query parameters. */
export function queryReviews(store: Store, query: Query): Review[] {
  let items = store.reviews.list();
  if (query.q !== undefined) {
    const hits = new Set(store.reviews.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.author !== undefined) {
    const wanted = query.author;
    items = items.filter((item) => item.author === wanted);
  }
  if (query.minStars !== undefined) {
    const limit = numberParam(query, "minStars");
    items = items.filter((item) => item.stars >= limit);
  }
  if (query.maxStars !== undefined) {
    const limit = numberParam(query, "maxStars");
    items = items.filter((item) => item.stars <= limit);
  }
  if (query.comment !== undefined) {
    const wanted = query.comment;
    items = items.filter((item) => item.comment === wanted);
  }
  if (query.verified !== undefined) {
    const wanted = flagParam(query, "verified");
    items = items.filter((item) => item.verified === wanted);
  }
  if (query.postedFrom !== undefined) {
    const day = checkDate("postedFrom", query.postedFrom);
    items = items.filter((item) => item.posted >= day);
  }
  if (query.postedTo !== undefined) {
    const day = checkDate("postedTo", query.postedTo);
    items = items.filter((item) => item.posted <= day);
  }
  return paginate(sortWith(items, query.sort, REVIEW_COMPARERS), query);
}

/** What each review field holds and the rule it must follow. */
export function describeReview(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "author", kind: "str", rule: RULES.str },
    { field: "stars", kind: "int", rule: RULES.int },
    { field: "comment", kind: "text", rule: RULES.text },
    { field: "verified", kind: "bool", rule: RULES.bool },
    { field: "posted", kind: "date", rule: RULES.date },
  ];
}

const CONTACT_PERSON_COMPARERS: Record<string, (a: ContactPerson, b: ContactPerson) => number> = {
  id: (a, b) => a.id - b.id,
  venueId: compareContactPersonByVenueId,
  name: compareContactPersonByName,
  email: compareContactPersonByEmail,
  phone: compareContactPersonByPhone,
  role: compareContactPersonByRole,
};

/** Contact persons matching the query parameters. */
export function queryContactPersons(store: Store, query: Query): ContactPerson[] {
  let items = store.contactPersons.list();
  if (query.q !== undefined) {
    const hits = new Set(store.contactPersons.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.venueId !== undefined) {
    const wanted = numberParam(query, "venueId");
    items = items.filter((item) => item.venueId === wanted);
  }
  if (query.name !== undefined) {
    const wanted = query.name;
    items = items.filter((item) => item.name === wanted);
  }
  if (query.email !== undefined) {
    const wanted = query.email;
    items = items.filter((item) => item.email === wanted);
  }
  if (query.phone !== undefined) {
    const wanted = query.phone;
    items = items.filter((item) => item.phone === wanted);
  }
  if (query.role !== undefined) {
    const wanted = query.role;
    items = items.filter((item) => item.role === wanted);
  }
  if (query.primary !== undefined) {
    const wanted = flagParam(query, "primary");
    items = items.filter((item) => item.primary === wanted);
  }
  return paginate(sortWith(items, query.sort, CONTACT_PERSON_COMPARERS), query);
}

/** What each contact person field holds and the rule it must follow. */
export function describeContactPerson(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "venueId", kind: "ref", rule: RULES.ref },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "email", kind: "email", rule: RULES.email },
    { field: "phone", kind: "str", rule: RULES.str },
    { field: "role", kind: "str", rule: RULES.str },
    { field: "primary", kind: "bool", rule: RULES.bool },
  ];
}
