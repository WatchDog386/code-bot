/**
 * Domain models for the Event Ticketing kit: record types, the allowed values of every
 * choice field, and validation that turns untrusted data into checked records.
 */

export class ValidationError extends Error {
  constructor(
    public readonly field: string,
    message: string,
  ) {
    super(`${field}: ${message}`);
    this.name = "ValidationError";
  }
}

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const MAX_INT = 1_000_000_000;

/** Trimmed text, not empty unless optional, and not too long. */
export function checkText(field: string, value: unknown, maxLength = 120, required = true): string {
  if (typeof value !== "string") {
    throw new ValidationError(field, "must be text");
  }
  const cleaned = value.trim();
  if (required && cleaned === "") {
    throw new ValidationError(field, "is required");
  }
  if (cleaned.length > maxLength) {
    throw new ValidationError(field, `must be at most ${maxLength} characters`);
  }
  return cleaned;
}

/** A plausible e-mail address, stored in lower case. */
export function checkEmail(field: string, value: unknown): string {
  const text = checkText(field, value, 254);
  if (!EMAIL_RE.test(text)) {
    throw new ValidationError(field, "must be an e-mail address");
  }
  return text.toLowerCase();
}

/** A whole number between 0 and a billion. */
export function checkInt(field: string, value: unknown): number {
  if (typeof value !== "number" || !Number.isInteger(value)) {
    throw new ValidationError(field, "must be a whole number");
  }
  if (value < 0 || value > MAX_INT) {
    throw new ValidationError(field, `must be between 0 and ${MAX_INT}`);
  }
  return value;
}

/** Any finite number that isn't negative. */
export function checkNumber(field: string, value: unknown): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new ValidationError(field, "must be a number");
  }
  if (value < 0) {
    throw new ValidationError(field, "must be at least 0");
  }
  return value;
}

/** An amount of money, rounded to cents. */
export function checkMoney(field: string, value: unknown): number {
  return Math.round(checkNumber(field, value) * 100) / 100;
}

/** A real boolean. */
export function checkFlag(field: string, value: unknown): boolean {
  if (typeof value !== "boolean") {
    throw new ValidationError(field, "must be true or false");
  }
  return value;
}

/** An ISO date (YYYY-MM-DD) that exists in the calendar. */
export function checkDate(field: string, value: unknown): string {
  const text = checkText(field, value, 10);
  const parsed = new Date(`${text}T00:00:00Z`);
  if (!DATE_RE.test(text) || Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== text) {
    throw new ValidationError(field, "must be a real date like 2026-01-31");
  }
  return text;
}

/** The id of another record (existence is checked by the services). */
export function checkRef(field: string, value: unknown): number {
  const id = checkInt(field, value);
  if (id < 1) {
    throw new ValidationError(field, "must point at a record");
  }
  return id;
}

/** One of a fixed list of values. */
export function checkChoice<T extends string>(field: string, value: unknown, allowed: readonly T[]): T {
  if (typeof value === "string" && (allowed as readonly string[]).includes(value)) {
    return value as T;
  }
  throw new ValidationError(field, `must be one of: ${allowed.join(", ")}`);
}

/** Throws if `data` has a key that isn't one of `known`. */
export function rejectUnknown(data: Record<string, unknown>, known: readonly string[]): void {
  for (const key of Object.keys(data)) {
    if (!known.includes(key)) {
      throw new ValidationError(key, "is not a known field");
    }
  }
}

/** Allowed values of Concert.status. */
export const CONCERT_STATUS_VALUES = ["planned", "on_sale", "sold_out", "cancelled", "finished"] as const;
export type ConcertStatus = (typeof CONCERT_STATUS_VALUES)[number];

export function isConcertStatus(value: unknown): value is ConcertStatus {
  return typeof value === "string" && (CONCERT_STATUS_VALUES as readonly string[]).includes(value);
}

export function labelConcertStatus(value: ConcertStatus): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Allowed values of Ticket.status. */
export const TICKET_STATUS_VALUES = ["valid", "used", "refunded", "void"] as const;
export type TicketStatus = (typeof TICKET_STATUS_VALUES)[number];

export function isTicketStatus(value: unknown): value is TicketStatus {
  return typeof value === "string" && (TICKET_STATUS_VALUES as readonly string[]).includes(value);
}

export function labelTicketStatus(value: TicketStatus): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Allowed values of Sponsor.tier. */
export const SPONSOR_TIER_VALUES = ["bronze", "silver", "gold", "platinum"] as const;
export type SponsorTier = (typeof SPONSOR_TIER_VALUES)[number];

export function isSponsorTier(value: unknown): value is SponsorTier {
  return typeof value === "string" && (SPONSOR_TIER_VALUES as readonly string[]).includes(value);
}

export function labelSponsorTier(value: SponsorTier): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Allowed values of Notification.channel. */
export const NOTIFICATION_CHANNEL_VALUES = ["email", "sms", "push"] as const;
export type NotificationChannel = (typeof NOTIFICATION_CHANNEL_VALUES)[number];

export function isNotificationChannel(value: unknown): value is NotificationChannel {
  return typeof value === "string" && (NOTIFICATION_CHANNEL_VALUES as readonly string[]).includes(value);
}

export function labelNotificationChannel(value: NotificationChannel): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Allowed values of Reminder.priority. */
export const REMINDER_PRIORITY_VALUES = ["low", "normal", "high"] as const;
export type ReminderPriority = (typeof REMINDER_PRIORITY_VALUES)[number];

export function isReminderPriority(value: unknown): value is ReminderPriority {
  return typeof value === "string" && (REMINDER_PRIORITY_VALUES as readonly string[]).includes(value);
}

export function labelReminderPriority(value: ReminderPriority): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Allowed values of AuditEntry.action. */
export const AUDIT_ENTRY_ACTION_VALUES = ["create", "update", "delete", "login", "export"] as const;
export type AuditEntryAction = (typeof AUDIT_ENTRY_ACTION_VALUES)[number];

export function isAuditEntryAction(value: unknown): value is AuditEntryAction {
  return typeof value === "string" && (AUDIT_ENTRY_ACTION_VALUES as readonly string[]).includes(value);
}

export function labelAuditEntryAction(value: AuditEntryAction): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

// ---------------------------------------------------------------------------- Venue

/** A venue record. */
export interface Venue {
  id: number;
  name: string;
  city: string;
  capacity: number;
  address: string;
  accessible: boolean;
}

export type VenueInput = Omit<Venue, "id">;

export const VENUE_FIELDS = ["id", "name", "city", "capacity", "address", "accessible"] as const;

/** Check Venue.name (str). */
export function checkVenueName(value: unknown): string {
  return checkText("name", value);
}

/** Check Venue.city (str). */
export function checkVenueCity(value: unknown): string {
  return checkText("city", value);
}

/** Check Venue.capacity (int). */
export function checkVenueCapacity(value: unknown): number {
  return checkInt("capacity", value);
}

/** Check Venue.address (str). */
export function checkVenueAddress(value: unknown): string {
  return checkText("address", value);
}

/** Check Venue.accessible (bool). */
export function checkVenueAccessible(value: unknown): boolean {
  return checkFlag("accessible", value);
}

/** A checked Venue from untrusted data (every field is required). */
export function parseVenue(data: Record<string, unknown>, id = 0): Venue {
  rejectUnknown(data, VENUE_FIELDS);
  return {
    id,
    name: checkVenueName(data.name),
    city: checkVenueCity(data.city),
    capacity: checkVenueCapacity(data.capacity),
    address: checkVenueAddress(data.address),
    accessible: checkVenueAccessible(data.accessible),
  };
}

/** The fields of a Venue without its id. */
export function venueInput(item: Venue): VenueInput {
  return {
    name: item.name,
    city: item.city,
    capacity: item.capacity,
    address: item.address,
    accessible: item.accessible,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchVenue(item: Venue, changes: Record<string, unknown>): Venue {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, VENUE_FIELDS);
  return parseVenue({ ...venueInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeVenue(item: Venue): string {
  return `Venue #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as VENUE_FIELDS). */
export function venueRow(item: Venue): Array<string | number | boolean> {
  return [item.id, item.name, item.city, item.capacity, item.address, item.accessible];
}

export function compareVenueByName(a: Venue, b: Venue): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareVenueByCity(a: Venue, b: Venue): number {
  return a.city < b.city ? -1 : a.city > b.city ? 1 : 0;
}

export function compareVenueByCapacity(a: Venue, b: Venue): number {
  return a.capacity - b.capacity;
}

export function compareVenueByAddress(a: Venue, b: Venue): number {
  return a.address < b.address ? -1 : a.address > b.address ? 1 : 0;
}

// ---------------------------------------------------------------------------- Concert

/** A concert record. */
export interface Concert {
  id: number;
  venueId: number;
  title: string;
  artist: string;
  day: string;
  doorsOpen: string;
  status: ConcertStatus;
}

export type ConcertInput = Omit<Concert, "id">;

export const CONCERT_FIELDS = ["id", "venueId", "title", "artist", "day", "doorsOpen", "status"] as const;

/** Check Concert.venueId (ref). */
export function checkConcertVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check Concert.title (str). */
export function checkConcertTitle(value: unknown): string {
  return checkText("title", value);
}

/** Check Concert.artist (str). */
export function checkConcertArtist(value: unknown): string {
  return checkText("artist", value);
}

/** Check Concert.day (date). */
export function checkConcertDay(value: unknown): string {
  return checkDate("day", value);
}

/** Check Concert.doorsOpen (str). */
export function checkConcertDoorsOpen(value: unknown): string {
  return checkText("doorsOpen", value);
}

/** Check Concert.status (enum). */
export function checkConcertStatus(value: unknown): ConcertStatus {
  return checkChoice("status", value, CONCERT_STATUS_VALUES);
}

/** A checked Concert from untrusted data (every field is required). */
export function parseConcert(data: Record<string, unknown>, id = 0): Concert {
  rejectUnknown(data, CONCERT_FIELDS);
  return {
    id,
    venueId: checkConcertVenueId(data.venueId),
    title: checkConcertTitle(data.title),
    artist: checkConcertArtist(data.artist),
    day: checkConcertDay(data.day),
    doorsOpen: checkConcertDoorsOpen(data.doorsOpen),
    status: checkConcertStatus(data.status),
  };
}

/** The fields of a Concert without its id. */
export function concertInput(item: Concert): ConcertInput {
  return {
    venueId: item.venueId,
    title: item.title,
    artist: item.artist,
    day: item.day,
    doorsOpen: item.doorsOpen,
    status: item.status,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchConcert(item: Concert, changes: Record<string, unknown>): Concert {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, CONCERT_FIELDS);
  return parseConcert({ ...concertInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeConcert(item: Concert): string {
  return `Concert #${item.id}: ${item.title}`;
}

/** The record as one CSV-ready row (same order as CONCERT_FIELDS). */
export function concertRow(item: Concert): Array<string | number | boolean> {
  return [item.id, item.venueId, item.title, item.artist, item.day, item.doorsOpen, item.status];
}

export function compareConcertByVenueId(a: Concert, b: Concert): number {
  return a.venueId - b.venueId;
}

export function compareConcertByTitle(a: Concert, b: Concert): number {
  return a.title < b.title ? -1 : a.title > b.title ? 1 : 0;
}

export function compareConcertByArtist(a: Concert, b: Concert): number {
  return a.artist < b.artist ? -1 : a.artist > b.artist ? 1 : 0;
}

export function compareConcertByDay(a: Concert, b: Concert): number {
  return a.day < b.day ? -1 : a.day > b.day ? 1 : 0;
}

export function compareConcertByDoorsOpen(a: Concert, b: Concert): number {
  return a.doorsOpen < b.doorsOpen ? -1 : a.doorsOpen > b.doorsOpen ? 1 : 0;
}

export function compareConcertByStatus(a: Concert, b: Concert): number {
  return a.status < b.status ? -1 : a.status > b.status ? 1 : 0;
}

// ---------------------------------------------------------------------------- TicketType

/** A ticket type record. */
export interface TicketType {
  id: number;
  concertId: number;
  name: string;
  price: number;
  quantity: number;
  sold: number;
  seated: boolean;
}

export type TicketTypeInput = Omit<TicketType, "id">;

export const TICKET_TYPE_FIELDS = ["id", "concertId", "name", "price", "quantity", "sold", "seated"] as const;

/** Check TicketType.concertId (ref). */
export function checkTicketTypeConcertId(value: unknown): number {
  return checkRef("concertId", value);
}

/** Check TicketType.name (str). */
export function checkTicketTypeName(value: unknown): string {
  return checkText("name", value);
}

/** Check TicketType.price (money). */
export function checkTicketTypePrice(value: unknown): number {
  return checkMoney("price", value);
}

/** Check TicketType.quantity (int). */
export function checkTicketTypeQuantity(value: unknown): number {
  return checkInt("quantity", value);
}

/** Check TicketType.sold (int). */
export function checkTicketTypeSold(value: unknown): number {
  return checkInt("sold", value);
}

/** Check TicketType.seated (bool). */
export function checkTicketTypeSeated(value: unknown): boolean {
  return checkFlag("seated", value);
}

/** A checked TicketType from untrusted data (every field is required). */
export function parseTicketType(data: Record<string, unknown>, id = 0): TicketType {
  rejectUnknown(data, TICKET_TYPE_FIELDS);
  return {
    id,
    concertId: checkTicketTypeConcertId(data.concertId),
    name: checkTicketTypeName(data.name),
    price: checkTicketTypePrice(data.price),
    quantity: checkTicketTypeQuantity(data.quantity),
    sold: checkTicketTypeSold(data.sold),
    seated: checkTicketTypeSeated(data.seated),
  };
}

/** The fields of a TicketType without its id. */
export function ticketTypeInput(item: TicketType): TicketTypeInput {
  return {
    concertId: item.concertId,
    name: item.name,
    price: item.price,
    quantity: item.quantity,
    sold: item.sold,
    seated: item.seated,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchTicketType(item: TicketType, changes: Record<string, unknown>): TicketType {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, TICKET_TYPE_FIELDS);
  return parseTicketType({ ...ticketTypeInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeTicketType(item: TicketType): string {
  return `TicketType #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as TICKET_TYPE_FIELDS). */
export function ticketTypeRow(item: TicketType): Array<string | number | boolean> {
  return [item.id, item.concertId, item.name, item.price, item.quantity, item.sold, item.seated];
}

export function compareTicketTypeByConcertId(a: TicketType, b: TicketType): number {
  return a.concertId - b.concertId;
}

export function compareTicketTypeByName(a: TicketType, b: TicketType): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareTicketTypeByPrice(a: TicketType, b: TicketType): number {
  return a.price - b.price;
}

export function compareTicketTypeByQuantity(a: TicketType, b: TicketType): number {
  return a.quantity - b.quantity;
}

export function compareTicketTypeBySold(a: TicketType, b: TicketType): number {
  return a.sold - b.sold;
}

// ---------------------------------------------------------------------------- Attendee

/** A attendee record. */
export interface Attendee {
  id: number;
  name: string;
  email: string;
  phone: string;
  country: string;
  newsletter: boolean;
}

export type AttendeeInput = Omit<Attendee, "id">;

export const ATTENDEE_FIELDS = ["id", "name", "email", "phone", "country", "newsletter"] as const;

/** Check Attendee.name (str). */
export function checkAttendeeName(value: unknown): string {
  return checkText("name", value);
}

/** Check Attendee.email (email). */
export function checkAttendeeEmail(value: unknown): string {
  return checkEmail("email", value);
}

/** Check Attendee.phone (str). */
export function checkAttendeePhone(value: unknown): string {
  return checkText("phone", value);
}

/** Check Attendee.country (str). */
export function checkAttendeeCountry(value: unknown): string {
  return checkText("country", value);
}

/** Check Attendee.newsletter (bool). */
export function checkAttendeeNewsletter(value: unknown): boolean {
  return checkFlag("newsletter", value);
}

/** A checked Attendee from untrusted data (every field is required). */
export function parseAttendee(data: Record<string, unknown>, id = 0): Attendee {
  rejectUnknown(data, ATTENDEE_FIELDS);
  return {
    id,
    name: checkAttendeeName(data.name),
    email: checkAttendeeEmail(data.email),
    phone: checkAttendeePhone(data.phone),
    country: checkAttendeeCountry(data.country),
    newsletter: checkAttendeeNewsletter(data.newsletter),
  };
}

/** The fields of a Attendee without its id. */
export function attendeeInput(item: Attendee): AttendeeInput {
  return {
    name: item.name,
    email: item.email,
    phone: item.phone,
    country: item.country,
    newsletter: item.newsletter,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchAttendee(item: Attendee, changes: Record<string, unknown>): Attendee {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, ATTENDEE_FIELDS);
  return parseAttendee({ ...attendeeInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeAttendee(item: Attendee): string {
  return `Attendee #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as ATTENDEE_FIELDS). */
export function attendeeRow(item: Attendee): Array<string | number | boolean> {
  return [item.id, item.name, item.email, item.phone, item.country, item.newsletter];
}

export function compareAttendeeByName(a: Attendee, b: Attendee): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareAttendeeByEmail(a: Attendee, b: Attendee): number {
  return a.email < b.email ? -1 : a.email > b.email ? 1 : 0;
}

export function compareAttendeeByPhone(a: Attendee, b: Attendee): number {
  return a.phone < b.phone ? -1 : a.phone > b.phone ? 1 : 0;
}

export function compareAttendeeByCountry(a: Attendee, b: Attendee): number {
  return a.country < b.country ? -1 : a.country > b.country ? 1 : 0;
}

// ---------------------------------------------------------------------------- Ticket

/** A ticket record. */
export interface Ticket {
  id: number;
  ticketTypeId: number;
  attendeeId: number;
  bought: string;
  code: string;
  status: TicketStatus;
  pricePaid: number;
}

export type TicketInput = Omit<Ticket, "id">;

export const TICKET_FIELDS = ["id", "ticketTypeId", "attendeeId", "bought", "code", "status", "pricePaid"] as const;

/** Check Ticket.ticketTypeId (ref). */
export function checkTicketTicketTypeId(value: unknown): number {
  return checkRef("ticketTypeId", value);
}

/** Check Ticket.attendeeId (ref). */
export function checkTicketAttendeeId(value: unknown): number {
  return checkRef("attendeeId", value);
}

/** Check Ticket.bought (date). */
export function checkTicketBought(value: unknown): string {
  return checkDate("bought", value);
}

/** Check Ticket.code (str). */
export function checkTicketCode(value: unknown): string {
  return checkText("code", value);
}

/** Check Ticket.status (enum). */
export function checkTicketStatus(value: unknown): TicketStatus {
  return checkChoice("status", value, TICKET_STATUS_VALUES);
}

/** Check Ticket.pricePaid (money). */
export function checkTicketPricePaid(value: unknown): number {
  return checkMoney("pricePaid", value);
}

/** A checked Ticket from untrusted data (every field is required). */
export function parseTicket(data: Record<string, unknown>, id = 0): Ticket {
  rejectUnknown(data, TICKET_FIELDS);
  return {
    id,
    ticketTypeId: checkTicketTicketTypeId(data.ticketTypeId),
    attendeeId: checkTicketAttendeeId(data.attendeeId),
    bought: checkTicketBought(data.bought),
    code: checkTicketCode(data.code),
    status: checkTicketStatus(data.status),
    pricePaid: checkTicketPricePaid(data.pricePaid),
  };
}

/** The fields of a Ticket without its id. */
export function ticketInput(item: Ticket): TicketInput {
  return {
    ticketTypeId: item.ticketTypeId,
    attendeeId: item.attendeeId,
    bought: item.bought,
    code: item.code,
    status: item.status,
    pricePaid: item.pricePaid,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchTicket(item: Ticket, changes: Record<string, unknown>): Ticket {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, TICKET_FIELDS);
  return parseTicket({ ...ticketInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeTicket(item: Ticket): string {
  return `Ticket #${item.id}: ${item.code}`;
}

/** The record as one CSV-ready row (same order as TICKET_FIELDS). */
export function ticketRow(item: Ticket): Array<string | number | boolean> {
  return [item.id, item.ticketTypeId, item.attendeeId, item.bought, item.code, item.status, item.pricePaid];
}

export function compareTicketByTicketTypeId(a: Ticket, b: Ticket): number {
  return a.ticketTypeId - b.ticketTypeId;
}

export function compareTicketByAttendeeId(a: Ticket, b: Ticket): number {
  return a.attendeeId - b.attendeeId;
}

export function compareTicketByBought(a: Ticket, b: Ticket): number {
  return a.bought < b.bought ? -1 : a.bought > b.bought ? 1 : 0;
}

export function compareTicketByCode(a: Ticket, b: Ticket): number {
  return a.code < b.code ? -1 : a.code > b.code ? 1 : 0;
}

export function compareTicketByStatus(a: Ticket, b: Ticket): number {
  return a.status < b.status ? -1 : a.status > b.status ? 1 : 0;
}

export function compareTicketByPricePaid(a: Ticket, b: Ticket): number {
  return a.pricePaid - b.pricePaid;
}

// ---------------------------------------------------------------------------- Sponsor

/** A sponsor record. */
export interface Sponsor {
  id: number;
  concertId: number;
  company: string;
  amount: number;
  tier: SponsorTier;
  logoUrl: string;
}

export type SponsorInput = Omit<Sponsor, "id">;

export const SPONSOR_FIELDS = ["id", "concertId", "company", "amount", "tier", "logoUrl"] as const;

/** Check Sponsor.concertId (ref). */
export function checkSponsorConcertId(value: unknown): number {
  return checkRef("concertId", value);
}

/** Check Sponsor.company (str). */
export function checkSponsorCompany(value: unknown): string {
  return checkText("company", value);
}

/** Check Sponsor.amount (money). */
export function checkSponsorAmount(value: unknown): number {
  return checkMoney("amount", value);
}

/** Check Sponsor.tier (enum). */
export function checkSponsorTier(value: unknown): SponsorTier {
  return checkChoice("tier", value, SPONSOR_TIER_VALUES);
}

/** Check Sponsor.logoUrl (str). */
export function checkSponsorLogoUrl(value: unknown): string {
  return checkText("logoUrl", value);
}

/** A checked Sponsor from untrusted data (every field is required). */
export function parseSponsor(data: Record<string, unknown>, id = 0): Sponsor {
  rejectUnknown(data, SPONSOR_FIELDS);
  return {
    id,
    concertId: checkSponsorConcertId(data.concertId),
    company: checkSponsorCompany(data.company),
    amount: checkSponsorAmount(data.amount),
    tier: checkSponsorTier(data.tier),
    logoUrl: checkSponsorLogoUrl(data.logoUrl),
  };
}

/** The fields of a Sponsor without its id. */
export function sponsorInput(item: Sponsor): SponsorInput {
  return {
    concertId: item.concertId,
    company: item.company,
    amount: item.amount,
    tier: item.tier,
    logoUrl: item.logoUrl,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchSponsor(item: Sponsor, changes: Record<string, unknown>): Sponsor {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, SPONSOR_FIELDS);
  return parseSponsor({ ...sponsorInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeSponsor(item: Sponsor): string {
  return `Sponsor #${item.id}: ${item.company}`;
}

/** The record as one CSV-ready row (same order as SPONSOR_FIELDS). */
export function sponsorRow(item: Sponsor): Array<string | number | boolean> {
  return [item.id, item.concertId, item.company, item.amount, item.tier, item.logoUrl];
}

export function compareSponsorByConcertId(a: Sponsor, b: Sponsor): number {
  return a.concertId - b.concertId;
}

export function compareSponsorByCompany(a: Sponsor, b: Sponsor): number {
  return a.company < b.company ? -1 : a.company > b.company ? 1 : 0;
}

export function compareSponsorByAmount(a: Sponsor, b: Sponsor): number {
  return a.amount - b.amount;
}

export function compareSponsorByTier(a: Sponsor, b: Sponsor): number {
  return a.tier < b.tier ? -1 : a.tier > b.tier ? 1 : 0;
}

export function compareSponsorByLogoUrl(a: Sponsor, b: Sponsor): number {
  return a.logoUrl < b.logoUrl ? -1 : a.logoUrl > b.logoUrl ? 1 : 0;
}

// ---------------------------------------------------------------------------- Document

/** A document record. */
export interface Document {
  id: number;
  venueId: number;
  title: string;
  pages: number;
  signed: boolean;
  version: number;
  issued: string;
}

export type DocumentInput = Omit<Document, "id">;

export const DOCUMENT_FIELDS = ["id", "venueId", "title", "pages", "signed", "version", "issued"] as const;

/** Check Document.venueId (ref). */
export function checkDocumentVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check Document.title (str). */
export function checkDocumentTitle(value: unknown): string {
  return checkText("title", value);
}

/** Check Document.pages (int). */
export function checkDocumentPages(value: unknown): number {
  return checkInt("pages", value);
}

/** Check Document.signed (bool). */
export function checkDocumentSigned(value: unknown): boolean {
  return checkFlag("signed", value);
}

/** Check Document.version (int). */
export function checkDocumentVersion(value: unknown): number {
  return checkInt("version", value);
}

/** Check Document.issued (date). */
export function checkDocumentIssued(value: unknown): string {
  return checkDate("issued", value);
}

/** A checked Document from untrusted data (every field is required). */
export function parseDocument(data: Record<string, unknown>, id = 0): Document {
  rejectUnknown(data, DOCUMENT_FIELDS);
  return {
    id,
    venueId: checkDocumentVenueId(data.venueId),
    title: checkDocumentTitle(data.title),
    pages: checkDocumentPages(data.pages),
    signed: checkDocumentSigned(data.signed),
    version: checkDocumentVersion(data.version),
    issued: checkDocumentIssued(data.issued),
  };
}

/** The fields of a Document without its id. */
export function documentInput(item: Document): DocumentInput {
  return {
    venueId: item.venueId,
    title: item.title,
    pages: item.pages,
    signed: item.signed,
    version: item.version,
    issued: item.issued,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchDocument(item: Document, changes: Record<string, unknown>): Document {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, DOCUMENT_FIELDS);
  return parseDocument({ ...documentInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeDocument(item: Document): string {
  return `Document #${item.id}: ${item.title}`;
}

/** The record as one CSV-ready row (same order as DOCUMENT_FIELDS). */
export function documentRow(item: Document): Array<string | number | boolean> {
  return [item.id, item.venueId, item.title, item.pages, item.signed, item.version, item.issued];
}

export function compareDocumentByVenueId(a: Document, b: Document): number {
  return a.venueId - b.venueId;
}

export function compareDocumentByTitle(a: Document, b: Document): number {
  return a.title < b.title ? -1 : a.title > b.title ? 1 : 0;
}

export function compareDocumentByPages(a: Document, b: Document): number {
  return a.pages - b.pages;
}

export function compareDocumentByVersion(a: Document, b: Document): number {
  return a.version - b.version;
}

export function compareDocumentByIssued(a: Document, b: Document): number {
  return a.issued < b.issued ? -1 : a.issued > b.issued ? 1 : 0;
}

// ---------------------------------------------------------------------------- Notification

/** A notification record. */
export interface Notification {
  id: number;
  recipient: string;
  title: string;
  sent: string;
  channel: NotificationChannel;
  read: boolean;
}

export type NotificationInput = Omit<Notification, "id">;

export const NOTIFICATION_FIELDS = ["id", "recipient", "title", "sent", "channel", "read"] as const;

/** Check Notification.recipient (email). */
export function checkNotificationRecipient(value: unknown): string {
  return checkEmail("recipient", value);
}

/** Check Notification.title (str). */
export function checkNotificationTitle(value: unknown): string {
  return checkText("title", value);
}

/** Check Notification.sent (date). */
export function checkNotificationSent(value: unknown): string {
  return checkDate("sent", value);
}

/** Check Notification.channel (enum). */
export function checkNotificationChannel(value: unknown): NotificationChannel {
  return checkChoice("channel", value, NOTIFICATION_CHANNEL_VALUES);
}

/** Check Notification.read (bool). */
export function checkNotificationRead(value: unknown): boolean {
  return checkFlag("read", value);
}

/** A checked Notification from untrusted data (every field is required). */
export function parseNotification(data: Record<string, unknown>, id = 0): Notification {
  rejectUnknown(data, NOTIFICATION_FIELDS);
  return {
    id,
    recipient: checkNotificationRecipient(data.recipient),
    title: checkNotificationTitle(data.title),
    sent: checkNotificationSent(data.sent),
    channel: checkNotificationChannel(data.channel),
    read: checkNotificationRead(data.read),
  };
}

/** The fields of a Notification without its id. */
export function notificationInput(item: Notification): NotificationInput {
  return {
    recipient: item.recipient,
    title: item.title,
    sent: item.sent,
    channel: item.channel,
    read: item.read,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchNotification(item: Notification, changes: Record<string, unknown>): Notification {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, NOTIFICATION_FIELDS);
  return parseNotification({ ...notificationInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeNotification(item: Notification): string {
  return `Notification #${item.id}: ${item.recipient}`;
}

/** The record as one CSV-ready row (same order as NOTIFICATION_FIELDS). */
export function notificationRow(item: Notification): Array<string | number | boolean> {
  return [item.id, item.recipient, item.title, item.sent, item.channel, item.read];
}

export function compareNotificationByRecipient(a: Notification, b: Notification): number {
  return a.recipient < b.recipient ? -1 : a.recipient > b.recipient ? 1 : 0;
}

export function compareNotificationByTitle(a: Notification, b: Notification): number {
  return a.title < b.title ? -1 : a.title > b.title ? 1 : 0;
}

export function compareNotificationBySent(a: Notification, b: Notification): number {
  return a.sent < b.sent ? -1 : a.sent > b.sent ? 1 : 0;
}

export function compareNotificationByChannel(a: Notification, b: Notification): number {
  return a.channel < b.channel ? -1 : a.channel > b.channel ? 1 : 0;
}

// ---------------------------------------------------------------------------- Address

/** A address record. */
export interface Address {
  id: number;
  venueId: number;
  street: string;
  city: string;
  postcode: string;
  country: string;
  billing: boolean;
}

export type AddressInput = Omit<Address, "id">;

export const ADDRESS_FIELDS = ["id", "venueId", "street", "city", "postcode", "country", "billing"] as const;

/** Check Address.venueId (ref). */
export function checkAddressVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check Address.street (str). */
export function checkAddressStreet(value: unknown): string {
  return checkText("street", value);
}

/** Check Address.city (str). */
export function checkAddressCity(value: unknown): string {
  return checkText("city", value);
}

/** Check Address.postcode (str). */
export function checkAddressPostcode(value: unknown): string {
  return checkText("postcode", value);
}

/** Check Address.country (str). */
export function checkAddressCountry(value: unknown): string {
  return checkText("country", value);
}

/** Check Address.billing (bool). */
export function checkAddressBilling(value: unknown): boolean {
  return checkFlag("billing", value);
}

/** A checked Address from untrusted data (every field is required). */
export function parseAddress(data: Record<string, unknown>, id = 0): Address {
  rejectUnknown(data, ADDRESS_FIELDS);
  return {
    id,
    venueId: checkAddressVenueId(data.venueId),
    street: checkAddressStreet(data.street),
    city: checkAddressCity(data.city),
    postcode: checkAddressPostcode(data.postcode),
    country: checkAddressCountry(data.country),
    billing: checkAddressBilling(data.billing),
  };
}

/** The fields of a Address without its id. */
export function addressInput(item: Address): AddressInput {
  return {
    venueId: item.venueId,
    street: item.street,
    city: item.city,
    postcode: item.postcode,
    country: item.country,
    billing: item.billing,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchAddress(item: Address, changes: Record<string, unknown>): Address {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, ADDRESS_FIELDS);
  return parseAddress({ ...addressInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeAddress(item: Address): string {
  return `Address #${item.id}: ${item.street}`;
}

/** The record as one CSV-ready row (same order as ADDRESS_FIELDS). */
export function addressRow(item: Address): Array<string | number | boolean> {
  return [item.id, item.venueId, item.street, item.city, item.postcode, item.country, item.billing];
}

export function compareAddressByVenueId(a: Address, b: Address): number {
  return a.venueId - b.venueId;
}

export function compareAddressByStreet(a: Address, b: Address): number {
  return a.street < b.street ? -1 : a.street > b.street ? 1 : 0;
}

export function compareAddressByCity(a: Address, b: Address): number {
  return a.city < b.city ? -1 : a.city > b.city ? 1 : 0;
}

export function compareAddressByPostcode(a: Address, b: Address): number {
  return a.postcode < b.postcode ? -1 : a.postcode > b.postcode ? 1 : 0;
}

export function compareAddressByCountry(a: Address, b: Address): number {
  return a.country < b.country ? -1 : a.country > b.country ? 1 : 0;
}

// ---------------------------------------------------------------------------- Reminder

/** A reminder record. */
export interface Reminder {
  id: number;
  venueId: number;
  title: string;
  remindOn: string;
  done: boolean;
  priority: ReminderPriority;
}

export type ReminderInput = Omit<Reminder, "id">;

export const REMINDER_FIELDS = ["id", "venueId", "title", "remindOn", "done", "priority"] as const;

/** Check Reminder.venueId (ref). */
export function checkReminderVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check Reminder.title (str). */
export function checkReminderTitle(value: unknown): string {
  return checkText("title", value);
}

/** Check Reminder.remindOn (date). */
export function checkReminderRemindOn(value: unknown): string {
  return checkDate("remindOn", value);
}

/** Check Reminder.done (bool). */
export function checkReminderDone(value: unknown): boolean {
  return checkFlag("done", value);
}

/** Check Reminder.priority (enum). */
export function checkReminderPriority(value: unknown): ReminderPriority {
  return checkChoice("priority", value, REMINDER_PRIORITY_VALUES);
}

/** A checked Reminder from untrusted data (every field is required). */
export function parseReminder(data: Record<string, unknown>, id = 0): Reminder {
  rejectUnknown(data, REMINDER_FIELDS);
  return {
    id,
    venueId: checkReminderVenueId(data.venueId),
    title: checkReminderTitle(data.title),
    remindOn: checkReminderRemindOn(data.remindOn),
    done: checkReminderDone(data.done),
    priority: checkReminderPriority(data.priority),
  };
}

/** The fields of a Reminder without its id. */
export function reminderInput(item: Reminder): ReminderInput {
  return {
    venueId: item.venueId,
    title: item.title,
    remindOn: item.remindOn,
    done: item.done,
    priority: item.priority,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchReminder(item: Reminder, changes: Record<string, unknown>): Reminder {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, REMINDER_FIELDS);
  return parseReminder({ ...reminderInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeReminder(item: Reminder): string {
  return `Reminder #${item.id}: ${item.title}`;
}

/** The record as one CSV-ready row (same order as REMINDER_FIELDS). */
export function reminderRow(item: Reminder): Array<string | number | boolean> {
  return [item.id, item.venueId, item.title, item.remindOn, item.done, item.priority];
}

export function compareReminderByVenueId(a: Reminder, b: Reminder): number {
  return a.venueId - b.venueId;
}

export function compareReminderByTitle(a: Reminder, b: Reminder): number {
  return a.title < b.title ? -1 : a.title > b.title ? 1 : 0;
}

export function compareReminderByRemindOn(a: Reminder, b: Reminder): number {
  return a.remindOn < b.remindOn ? -1 : a.remindOn > b.remindOn ? 1 : 0;
}

export function compareReminderByPriority(a: Reminder, b: Reminder): number {
  return a.priority < b.priority ? -1 : a.priority > b.priority ? 1 : 0;
}

// ---------------------------------------------------------------------------- Setting

/** A setting record. */
export interface Setting {
  id: number;
  keyName: string;
  value: string;
  editable: boolean;
  changed: string;
}

export type SettingInput = Omit<Setting, "id">;

export const SETTING_FIELDS = ["id", "keyName", "value", "editable", "changed"] as const;

/** Check Setting.keyName (str). */
export function checkSettingKeyName(value: unknown): string {
  return checkText("keyName", value);
}

/** Check Setting.value (str). */
export function checkSettingValue(value: unknown): string {
  return checkText("value", value);
}

/** Check Setting.editable (bool). */
export function checkSettingEditable(value: unknown): boolean {
  return checkFlag("editable", value);
}

/** Check Setting.changed (date). */
export function checkSettingChanged(value: unknown): string {
  return checkDate("changed", value);
}

/** A checked Setting from untrusted data (every field is required). */
export function parseSetting(data: Record<string, unknown>, id = 0): Setting {
  rejectUnknown(data, SETTING_FIELDS);
  return {
    id,
    keyName: checkSettingKeyName(data.keyName),
    value: checkSettingValue(data.value),
    editable: checkSettingEditable(data.editable),
    changed: checkSettingChanged(data.changed),
  };
}

/** The fields of a Setting without its id. */
export function settingInput(item: Setting): SettingInput {
  return {
    keyName: item.keyName,
    value: item.value,
    editable: item.editable,
    changed: item.changed,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchSetting(item: Setting, changes: Record<string, unknown>): Setting {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, SETTING_FIELDS);
  return parseSetting({ ...settingInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeSetting(item: Setting): string {
  return `Setting #${item.id}: ${item.keyName}`;
}

/** The record as one CSV-ready row (same order as SETTING_FIELDS). */
export function settingRow(item: Setting): Array<string | number | boolean> {
  return [item.id, item.keyName, item.value, item.editable, item.changed];
}

export function compareSettingByKeyName(a: Setting, b: Setting): number {
  return a.keyName < b.keyName ? -1 : a.keyName > b.keyName ? 1 : 0;
}

export function compareSettingByValue(a: Setting, b: Setting): number {
  return a.value < b.value ? -1 : a.value > b.value ? 1 : 0;
}

export function compareSettingByChanged(a: Setting, b: Setting): number {
  return a.changed < b.changed ? -1 : a.changed > b.changed ? 1 : 0;
}

// ---------------------------------------------------------------------------- AuditEntry

/** A audit entry record. */
export interface AuditEntry {
  id: number;
  actor: string;
  action: AuditEntryAction;
  at: string;
  details: string;
}

export type AuditEntryInput = Omit<AuditEntry, "id">;

export const AUDIT_ENTRY_FIELDS = ["id", "actor", "action", "at", "details"] as const;

/** Check AuditEntry.actor (str). */
export function checkAuditEntryActor(value: unknown): string {
  return checkText("actor", value);
}

/** Check AuditEntry.action (enum). */
export function checkAuditEntryAction(value: unknown): AuditEntryAction {
  return checkChoice("action", value, AUDIT_ENTRY_ACTION_VALUES);
}

/** Check AuditEntry.at (date). */
export function checkAuditEntryAt(value: unknown): string {
  return checkDate("at", value);
}

/** Check AuditEntry.details (text). */
export function checkAuditEntryDetails(value: unknown): string {
  return checkText("details", value, 2000, false);
}

/** A checked AuditEntry from untrusted data (every field is required). */
export function parseAuditEntry(data: Record<string, unknown>, id = 0): AuditEntry {
  rejectUnknown(data, AUDIT_ENTRY_FIELDS);
  return {
    id,
    actor: checkAuditEntryActor(data.actor),
    action: checkAuditEntryAction(data.action),
    at: checkAuditEntryAt(data.at),
    details: checkAuditEntryDetails(data.details),
  };
}

/** The fields of a AuditEntry without its id. */
export function auditEntryInput(item: AuditEntry): AuditEntryInput {
  return {
    actor: item.actor,
    action: item.action,
    at: item.at,
    details: item.details,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchAuditEntry(item: AuditEntry, changes: Record<string, unknown>): AuditEntry {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, AUDIT_ENTRY_FIELDS);
  return parseAuditEntry({ ...auditEntryInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeAuditEntry(item: AuditEntry): string {
  return `AuditEntry #${item.id}: ${item.actor}`;
}

/** The record as one CSV-ready row (same order as AUDIT_ENTRY_FIELDS). */
export function auditEntryRow(item: AuditEntry): Array<string | number | boolean> {
  return [item.id, item.actor, item.action, item.at, item.details];
}

export function compareAuditEntryByActor(a: AuditEntry, b: AuditEntry): number {
  return a.actor < b.actor ? -1 : a.actor > b.actor ? 1 : 0;
}

export function compareAuditEntryByAction(a: AuditEntry, b: AuditEntry): number {
  return a.action < b.action ? -1 : a.action > b.action ? 1 : 0;
}

export function compareAuditEntryByAt(a: AuditEntry, b: AuditEntry): number {
  return a.at < b.at ? -1 : a.at > b.at ? 1 : 0;
}

export function compareAuditEntryByDetails(a: AuditEntry, b: AuditEntry): number {
  return a.details < b.details ? -1 : a.details > b.details ? 1 : 0;
}

// ---------------------------------------------------------------------------- Note

/** A note record. */
export interface Note {
  id: number;
  venueId: number;
  subject: string;
  body: string;
  pinned: boolean;
  written: string;
}

export type NoteInput = Omit<Note, "id">;

export const NOTE_FIELDS = ["id", "venueId", "subject", "body", "pinned", "written"] as const;

/** Check Note.venueId (ref). */
export function checkNoteVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check Note.subject (str). */
export function checkNoteSubject(value: unknown): string {
  return checkText("subject", value);
}

/** Check Note.body (text). */
export function checkNoteBody(value: unknown): string {
  return checkText("body", value, 2000, false);
}

/** Check Note.pinned (bool). */
export function checkNotePinned(value: unknown): boolean {
  return checkFlag("pinned", value);
}

/** Check Note.written (date). */
export function checkNoteWritten(value: unknown): string {
  return checkDate("written", value);
}

/** A checked Note from untrusted data (every field is required). */
export function parseNote(data: Record<string, unknown>, id = 0): Note {
  rejectUnknown(data, NOTE_FIELDS);
  return {
    id,
    venueId: checkNoteVenueId(data.venueId),
    subject: checkNoteSubject(data.subject),
    body: checkNoteBody(data.body),
    pinned: checkNotePinned(data.pinned),
    written: checkNoteWritten(data.written),
  };
}

/** The fields of a Note without its id. */
export function noteInput(item: Note): NoteInput {
  return {
    venueId: item.venueId,
    subject: item.subject,
    body: item.body,
    pinned: item.pinned,
    written: item.written,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchNote(item: Note, changes: Record<string, unknown>): Note {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, NOTE_FIELDS);
  return parseNote({ ...noteInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeNote(item: Note): string {
  return `Note #${item.id}: ${item.subject}`;
}

/** The record as one CSV-ready row (same order as NOTE_FIELDS). */
export function noteRow(item: Note): Array<string | number | boolean> {
  return [item.id, item.venueId, item.subject, item.body, item.pinned, item.written];
}

export function compareNoteByVenueId(a: Note, b: Note): number {
  return a.venueId - b.venueId;
}

export function compareNoteBySubject(a: Note, b: Note): number {
  return a.subject < b.subject ? -1 : a.subject > b.subject ? 1 : 0;
}

export function compareNoteByBody(a: Note, b: Note): number {
  return a.body < b.body ? -1 : a.body > b.body ? 1 : 0;
}

export function compareNoteByWritten(a: Note, b: Note): number {
  return a.written < b.written ? -1 : a.written > b.written ? 1 : 0;
}

// ---------------------------------------------------------------------------- Review

/** A review record. */
export interface Review {
  id: number;
  venueId: number;
  author: string;
  stars: number;
  comment: string;
  verified: boolean;
  posted: string;
}

export type ReviewInput = Omit<Review, "id">;

export const REVIEW_FIELDS = ["id", "venueId", "author", "stars", "comment", "verified", "posted"] as const;

/** Check Review.venueId (ref). */
export function checkReviewVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check Review.author (str). */
export function checkReviewAuthor(value: unknown): string {
  return checkText("author", value);
}

/** Check Review.stars (int). */
export function checkReviewStars(value: unknown): number {
  return checkInt("stars", value);
}

/** Check Review.comment (text). */
export function checkReviewComment(value: unknown): string {
  return checkText("comment", value, 2000, false);
}

/** Check Review.verified (bool). */
export function checkReviewVerified(value: unknown): boolean {
  return checkFlag("verified", value);
}

/** Check Review.posted (date). */
export function checkReviewPosted(value: unknown): string {
  return checkDate("posted", value);
}

/** A checked Review from untrusted data (every field is required). */
export function parseReview(data: Record<string, unknown>, id = 0): Review {
  rejectUnknown(data, REVIEW_FIELDS);
  return {
    id,
    venueId: checkReviewVenueId(data.venueId),
    author: checkReviewAuthor(data.author),
    stars: checkReviewStars(data.stars),
    comment: checkReviewComment(data.comment),
    verified: checkReviewVerified(data.verified),
    posted: checkReviewPosted(data.posted),
  };
}

/** The fields of a Review without its id. */
export function reviewInput(item: Review): ReviewInput {
  return {
    venueId: item.venueId,
    author: item.author,
    stars: item.stars,
    comment: item.comment,
    verified: item.verified,
    posted: item.posted,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchReview(item: Review, changes: Record<string, unknown>): Review {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, REVIEW_FIELDS);
  return parseReview({ ...reviewInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeReview(item: Review): string {
  return `Review #${item.id}: ${item.author}`;
}

/** The record as one CSV-ready row (same order as REVIEW_FIELDS). */
export function reviewRow(item: Review): Array<string | number | boolean> {
  return [item.id, item.venueId, item.author, item.stars, item.comment, item.verified, item.posted];
}

export function compareReviewByVenueId(a: Review, b: Review): number {
  return a.venueId - b.venueId;
}

export function compareReviewByAuthor(a: Review, b: Review): number {
  return a.author < b.author ? -1 : a.author > b.author ? 1 : 0;
}

export function compareReviewByStars(a: Review, b: Review): number {
  return a.stars - b.stars;
}

export function compareReviewByComment(a: Review, b: Review): number {
  return a.comment < b.comment ? -1 : a.comment > b.comment ? 1 : 0;
}

export function compareReviewByPosted(a: Review, b: Review): number {
  return a.posted < b.posted ? -1 : a.posted > b.posted ? 1 : 0;
}

// ---------------------------------------------------------------------------- ContactPerson

/** A contact person record. */
export interface ContactPerson {
  id: number;
  venueId: number;
  name: string;
  email: string;
  phone: string;
  role: string;
  primary: boolean;
}

export type ContactPersonInput = Omit<ContactPerson, "id">;

export const CONTACT_PERSON_FIELDS = ["id", "venueId", "name", "email", "phone", "role", "primary"] as const;

/** Check ContactPerson.venueId (ref). */
export function checkContactPersonVenueId(value: unknown): number {
  return checkRef("venueId", value);
}

/** Check ContactPerson.name (str). */
export function checkContactPersonName(value: unknown): string {
  return checkText("name", value);
}

/** Check ContactPerson.email (email). */
export function checkContactPersonEmail(value: unknown): string {
  return checkEmail("email", value);
}

/** Check ContactPerson.phone (str). */
export function checkContactPersonPhone(value: unknown): string {
  return checkText("phone", value);
}

/** Check ContactPerson.role (str). */
export function checkContactPersonRole(value: unknown): string {
  return checkText("role", value);
}

/** Check ContactPerson.primary (bool). */
export function checkContactPersonPrimary(value: unknown): boolean {
  return checkFlag("primary", value);
}

/** A checked ContactPerson from untrusted data (every field is required). */
export function parseContactPerson(data: Record<string, unknown>, id = 0): ContactPerson {
  rejectUnknown(data, CONTACT_PERSON_FIELDS);
  return {
    id,
    venueId: checkContactPersonVenueId(data.venueId),
    name: checkContactPersonName(data.name),
    email: checkContactPersonEmail(data.email),
    phone: checkContactPersonPhone(data.phone),
    role: checkContactPersonRole(data.role),
    primary: checkContactPersonPrimary(data.primary),
  };
}

/** The fields of a ContactPerson without its id. */
export function contactPersonInput(item: ContactPerson): ContactPersonInput {
  return {
    venueId: item.venueId,
    name: item.name,
    email: item.email,
    phone: item.phone,
    role: item.role,
    primary: item.primary,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchContactPerson(item: ContactPerson, changes: Record<string, unknown>): ContactPerson {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, CONTACT_PERSON_FIELDS);
  return parseContactPerson({ ...contactPersonInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeContactPerson(item: ContactPerson): string {
  return `ContactPerson #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as CONTACT_PERSON_FIELDS). */
export function contactPersonRow(item: ContactPerson): Array<string | number | boolean> {
  return [item.id, item.venueId, item.name, item.email, item.phone, item.role, item.primary];
}

export function compareContactPersonByVenueId(a: ContactPerson, b: ContactPerson): number {
  return a.venueId - b.venueId;
}

export function compareContactPersonByName(a: ContactPerson, b: ContactPerson): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareContactPersonByEmail(a: ContactPerson, b: ContactPerson): number {
  return a.email < b.email ? -1 : a.email > b.email ? 1 : 0;
}

export function compareContactPersonByPhone(a: ContactPerson, b: ContactPerson): number {
  return a.phone < b.phone ? -1 : a.phone > b.phone ? 1 : 0;
}

export function compareContactPersonByRole(a: ContactPerson, b: ContactPerson): number {
  return a.role < b.role ? -1 : a.role > b.role ? 1 : 0;
}
