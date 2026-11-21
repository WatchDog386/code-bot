/**
 * Business rules for the Event Ticketing kit: validation, links between records (a record
 * can't point at something missing, or be deleted while others point at it), small
 * domain operations and statistics.
 */

import {
  AUDIT_ENTRY_ACTION_VALUES,
  Address,
  Attendee,
  AuditEntry,
  AuditEntryAction,
  CONCERT_STATUS_VALUES,
  Concert,
  ConcertStatus,
  ContactPerson,
  Document,
  NOTIFICATION_CHANNEL_VALUES,
  Note,
  Notification,
  NotificationChannel,
  REMINDER_PRIORITY_VALUES,
  Reminder,
  ReminderPriority,
  Review,
  SPONSOR_TIER_VALUES,
  Setting,
  Sponsor,
  SponsorTier,
  TICKET_STATUS_VALUES,
  Ticket,
  TicketStatus,
  TicketType,
  ValidationError,
  Venue,
  parseAddress,
  parseAttendee,
  parseAuditEntry,
  parseConcert,
  parseContactPerson,
  parseDocument,
  parseNote,
  parseNotification,
  parseReminder,
  parseReview,
  parseSetting,
  parseSponsor,
  parseTicket,
  parseTicketType,
  parseVenue,
  patchAddress,
  patchAttendee,
  patchAuditEntry,
  patchConcert,
  patchContactPerson,
  patchDocument,
  patchNote,
  patchNotification,
  patchReminder,
  patchReview,
  patchSetting,
  patchSponsor,
  patchTicket,
  patchTicketType,
  patchVenue,
} from "./models";
import {
  VenueStore,
  ConcertStore,
  TicketTypeStore,
  AttendeeStore,
  TicketStore,
  SponsorStore,
  DocumentStore,
  NotificationStore,
  AddressStore,
  ReminderStore,
  SettingStore,
  AuditEntryStore,
  NoteStore,
  ReviewStore,
  ContactPersonStore,
} from "./store";

export class NotFoundError extends Error {
  constructor(
    public readonly entity: string,
    public readonly id: number,
  ) {
    super(`${entity} ${id} not found`);
    this.name = "NotFoundError";
  }
}

export class ConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConflictError";
  }
}

/** Every store of the kit. */
export class Store {
  readonly venues = new VenueStore();
  readonly concerts = new ConcertStore();
  readonly ticketTypes = new TicketTypeStore();
  readonly attendees = new AttendeeStore();
  readonly tickets = new TicketStore();
  readonly sponsors = new SponsorStore();
  readonly documents = new DocumentStore();
  readonly notifications = new NotificationStore();
  readonly addresses = new AddressStore();
  readonly reminders = new ReminderStore();
  readonly settings = new SettingStore();
  readonly auditEntries = new AuditEntryStore();
  readonly notes = new NoteStore();
  readonly reviews = new ReviewStore();
  readonly contactPersons = new ContactPersonStore();

  counts(): Record<string, number> {
    return {
      venues: this.venues.count(),
      concerts: this.concerts.count(),
      ticketTypes: this.ticketTypes.count(),
      attendees: this.attendees.count(),
      tickets: this.tickets.count(),
      sponsors: this.sponsors.count(),
      documents: this.documents.count(),
      notifications: this.notifications.count(),
      addresses: this.addresses.count(),
      reminders: this.reminders.count(),
      settings: this.settings.count(),
      auditEntries: this.auditEntries.count(),
      notes: this.notes.count(),
      reviews: this.reviews.count(),
      contactPersons: this.contactPersons.count(),
    };
  }
}

/** Create, change and remove venues. */
export class VenueService {
  constructor(private readonly store: Store) {}

  private get repo(): VenueStore {
    return this.store.venues;
  }

  /** Validate and store a new venue. */
  create(data: Record<string, unknown>): Venue {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseVenue(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Venue {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("venue", id);
    }
    return item;
  }

  list(): Venue[] {
    return this.repo.list();
  }

  /** Change some fields of a venue. */
  update(id: number, changes: Record<string, unknown>): Venue {
    const updated = patchVenue(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a venue nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const concerts = this.store.concerts.countForVenue(id);
    if (concerts > 0) {
      throw new ConflictError(`venue ${id} is still used by ${concerts} concerts`);
    }
    const documents = this.store.documents.countForVenue(id);
    if (documents > 0) {
      throw new ConflictError(`venue ${id} is still used by ${documents} documents`);
    }
    const addresses = this.store.addresses.countForVenue(id);
    if (addresses > 0) {
      throw new ConflictError(`venue ${id} is still used by ${addresses} addresses`);
    }
    const reminders = this.store.reminders.countForVenue(id);
    if (reminders > 0) {
      throw new ConflictError(`venue ${id} is still used by ${reminders} reminders`);
    }
    const notes = this.store.notes.countForVenue(id);
    if (notes > 0) {
      throw new ConflictError(`venue ${id} is still used by ${notes} notes`);
    }
    const reviews = this.store.reviews.countForVenue(id);
    if (reviews > 0) {
      throw new ConflictError(`venue ${id} is still used by ${reviews} reviews`);
    }
    const contactPersons = this.store.contactPersons.countForVenue(id);
    if (contactPersons > 0) {
      throw new ConflictError(`venue ${id} is still used by ${contactPersons} contact persons`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: Venue): void {
    void item; // a venue doesn't point at other records
  }

  /** Add `delta` to the capacity (it can't go below zero). */
  adjustCapacity(id: number, delta: number): Venue {
    return this.update(id, { capacity: this.get(id).capacity + delta });
  }

  toggleAccessible(id: number): Venue {
    return this.update(id, { accessible: !this.get(id).accessible });
  }

  /** Totals and breakdowns over every venue. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalCapacity: this.repo.totalCapacity(),
      averageCapacity: this.repo.averageCapacity(),
      accessible: this.repo.whereAccessible(true).length,
    };
  }
}

/** Create, change and remove concerts. */
export class ConcertService {
  constructor(private readonly store: Store) {}

  private get repo(): ConcertStore {
    return this.store.concerts;
  }

  /** Validate and store a new concert. */
  create(data: Record<string, unknown>): Concert {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseConcert(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Concert {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("concert", id);
    }
    return item;
  }

  list(): Concert[] {
    return this.repo.list();
  }

  /** Change some fields of a concert. */
  update(id: number, changes: Record<string, unknown>): Concert {
    const updated = patchConcert(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a concert nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const ticketTypes = this.store.ticketTypes.countForConcert(id);
    if (ticketTypes > 0) {
      throw new ConflictError(`concert ${id} is still used by ${ticketTypes} ticket types`);
    }
    const sponsors = this.store.sponsors.countForConcert(id);
    if (sponsors > 0) {
      throw new ConflictError(`concert ${id} is still used by ${sponsors} sponsors`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: Concert): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  setStatus(id: number, value: ConcertStatus): Concert {
    return this.update(id, { status: value });
  }

  /** Totals and breakdowns over every concert. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      byStatus: this.repo.countByStatus(),
    };
  }
}

/** Create, change and remove ticket types. */
export class TicketTypeService {
  constructor(private readonly store: Store) {}

  private get repo(): TicketTypeStore {
    return this.store.ticketTypes;
  }

  /** Validate and store a new ticket type. */
  create(data: Record<string, unknown>): TicketType {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseTicketType(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): TicketType {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("ticket type", id);
    }
    return item;
  }

  list(): TicketType[] {
    return this.repo.list();
  }

  /** Change some fields of a ticket type. */
  update(id: number, changes: Record<string, unknown>): TicketType {
    const updated = patchTicketType(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a ticket type nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const tickets = this.store.tickets.countForTicketType(id);
    if (tickets > 0) {
      throw new ConflictError(`ticket type ${id} is still used by ${tickets} tickets`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: TicketType): void {
    if (!this.store.concerts.get(item.concertId)) {
      throw new NotFoundError("concert", item.concertId);
    }
  }

  adjustPrice(id: number, delta: number): TicketType {
    return this.update(id, { price: Math.round((this.get(id).price + delta) * 100) / 100 });
  }

  /** Add `delta` to the quantity (it can't go below zero). */
  adjustQuantity(id: number, delta: number): TicketType {
    return this.update(id, { quantity: this.get(id).quantity + delta });
  }

  /** Add `delta` to the sold (it can't go below zero). */
  adjustSold(id: number, delta: number): TicketType {
    return this.update(id, { sold: this.get(id).sold + delta });
  }

  toggleSeated(id: number): TicketType {
    return this.update(id, { seated: !this.get(id).seated });
  }

  /** Totals and breakdowns over every ticket type. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalPrice: this.repo.totalPrice(),
      averagePrice: this.repo.averagePrice(),
      totalQuantity: this.repo.totalQuantity(),
      averageQuantity: this.repo.averageQuantity(),
      totalSold: this.repo.totalSold(),
      averageSold: this.repo.averageSold(),
      seated: this.repo.whereSeated(true).length,
    };
  }
}

/** Create, change and remove attendees. */
export class AttendeeService {
  constructor(private readonly store: Store) {}

  private get repo(): AttendeeStore {
    return this.store.attendees;
  }

  /** Validate and store a new attendee. */
  create(data: Record<string, unknown>): Attendee {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseAttendee(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Attendee {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("attendee", id);
    }
    return item;
  }

  list(): Attendee[] {
    return this.repo.list();
  }

  /** Change some fields of a attendee. */
  update(id: number, changes: Record<string, unknown>): Attendee {
    const updated = patchAttendee(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a attendee nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const tickets = this.store.tickets.countForAttendee(id);
    if (tickets > 0) {
      throw new ConflictError(`attendee ${id} is still used by ${tickets} tickets`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: Attendee): void {
    void item; // a attendee doesn't point at other records
  }

  toggleNewsletter(id: number): Attendee {
    return this.update(id, { newsletter: !this.get(id).newsletter });
  }

  /** Totals and breakdowns over every attendee. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      newsletter: this.repo.whereNewsletter(true).length,
    };
  }
}

/** Create, change and remove tickets. */
export class TicketService {
  constructor(private readonly store: Store) {}

  private get repo(): TicketStore {
    return this.store.tickets;
  }

  /** Validate and store a new ticket. */
  create(data: Record<string, unknown>): Ticket {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseTicket(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Ticket {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("ticket", id);
    }
    return item;
  }

  list(): Ticket[] {
    return this.repo.list();
  }

  /** Change some fields of a ticket. */
  update(id: number, changes: Record<string, unknown>): Ticket {
    const updated = patchTicket(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a ticket nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Ticket): void {
    if (!this.store.ticketTypes.get(item.ticketTypeId)) {
      throw new NotFoundError("ticket type", item.ticketTypeId);
    }
    if (!this.store.attendees.get(item.attendeeId)) {
      throw new NotFoundError("attendee", item.attendeeId);
    }
  }

  setStatus(id: number, value: TicketStatus): Ticket {
    return this.update(id, { status: value });
  }

  adjustPricePaid(id: number, delta: number): Ticket {
    return this.update(id, { pricePaid: Math.round((this.get(id).pricePaid + delta) * 100) / 100 });
  }

  /** Totals and breakdowns over every ticket. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      byStatus: this.repo.countByStatus(),
      totalPricePaid: this.repo.totalPricePaid(),
      averagePricePaid: this.repo.averagePricePaid(),
    };
  }
}

/** Create, change and remove sponsors. */
export class SponsorService {
  constructor(private readonly store: Store) {}

  private get repo(): SponsorStore {
    return this.store.sponsors;
  }

  /** Validate and store a new sponsor. */
  create(data: Record<string, unknown>): Sponsor {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseSponsor(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Sponsor {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("sponsor", id);
    }
    return item;
  }

  list(): Sponsor[] {
    return this.repo.list();
  }

  /** Change some fields of a sponsor. */
  update(id: number, changes: Record<string, unknown>): Sponsor {
    const updated = patchSponsor(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a sponsor nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Sponsor): void {
    if (!this.store.concerts.get(item.concertId)) {
      throw new NotFoundError("concert", item.concertId);
    }
  }

  adjustAmount(id: number, delta: number): Sponsor {
    return this.update(id, { amount: Math.round((this.get(id).amount + delta) * 100) / 100 });
  }

  setTier(id: number, value: SponsorTier): Sponsor {
    return this.update(id, { tier: value });
  }

  /** Totals and breakdowns over every sponsor. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalAmount: this.repo.totalAmount(),
      averageAmount: this.repo.averageAmount(),
      byTier: this.repo.countByTier(),
    };
  }
}

/** Create, change and remove documents. */
export class DocumentService {
  constructor(private readonly store: Store) {}

  private get repo(): DocumentStore {
    return this.store.documents;
  }

  /** Validate and store a new document. */
  create(data: Record<string, unknown>): Document {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseDocument(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Document {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("document", id);
    }
    return item;
  }

  list(): Document[] {
    return this.repo.list();
  }

  /** Change some fields of a document. */
  update(id: number, changes: Record<string, unknown>): Document {
    const updated = patchDocument(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a document nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Document): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  /** Add `delta` to the pages (it can't go below zero). */
  adjustPages(id: number, delta: number): Document {
    return this.update(id, { pages: this.get(id).pages + delta });
  }

  toggleSigned(id: number): Document {
    return this.update(id, { signed: !this.get(id).signed });
  }

  /** Add `delta` to the version (it can't go below zero). */
  adjustVersion(id: number, delta: number): Document {
    return this.update(id, { version: this.get(id).version + delta });
  }

  /** Totals and breakdowns over every document. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalPages: this.repo.totalPages(),
      averagePages: this.repo.averagePages(),
      signed: this.repo.whereSigned(true).length,
      totalVersion: this.repo.totalVersion(),
      averageVersion: this.repo.averageVersion(),
    };
  }
}

/** Create, change and remove notifications. */
export class NotificationService {
  constructor(private readonly store: Store) {}

  private get repo(): NotificationStore {
    return this.store.notifications;
  }

  /** Validate and store a new notification. */
  create(data: Record<string, unknown>): Notification {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseNotification(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Notification {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("notification", id);
    }
    return item;
  }

  list(): Notification[] {
    return this.repo.list();
  }

  /** Change some fields of a notification. */
  update(id: number, changes: Record<string, unknown>): Notification {
    const updated = patchNotification(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a notification nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Notification): void {
    void item; // a notification doesn't point at other records
  }

  setChannel(id: number, value: NotificationChannel): Notification {
    return this.update(id, { channel: value });
  }

  toggleRead(id: number): Notification {
    return this.update(id, { read: !this.get(id).read });
  }

  /** Totals and breakdowns over every notification. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      byChannel: this.repo.countByChannel(),
      read: this.repo.whereRead(true).length,
    };
  }
}

/** Create, change and remove addresses. */
export class AddressService {
  constructor(private readonly store: Store) {}

  private get repo(): AddressStore {
    return this.store.addresses;
  }

  /** Validate and store a new address. */
  create(data: Record<string, unknown>): Address {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseAddress(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Address {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("address", id);
    }
    return item;
  }

  list(): Address[] {
    return this.repo.list();
  }

  /** Change some fields of a address. */
  update(id: number, changes: Record<string, unknown>): Address {
    const updated = patchAddress(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a address nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Address): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  toggleBilling(id: number): Address {
    return this.update(id, { billing: !this.get(id).billing });
  }

  /** Totals and breakdowns over every address. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      billing: this.repo.whereBilling(true).length,
    };
  }
}

/** Create, change and remove reminders. */
export class ReminderService {
  constructor(private readonly store: Store) {}

  private get repo(): ReminderStore {
    return this.store.reminders;
  }

  /** Validate and store a new reminder. */
  create(data: Record<string, unknown>): Reminder {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseReminder(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Reminder {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("reminder", id);
    }
    return item;
  }

  list(): Reminder[] {
    return this.repo.list();
  }

  /** Change some fields of a reminder. */
  update(id: number, changes: Record<string, unknown>): Reminder {
    const updated = patchReminder(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a reminder nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Reminder): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  toggleDone(id: number): Reminder {
    return this.update(id, { done: !this.get(id).done });
  }

  setPriority(id: number, value: ReminderPriority): Reminder {
    return this.update(id, { priority: value });
  }

  /** Totals and breakdowns over every reminder. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      done: this.repo.whereDone(true).length,
      byPriority: this.repo.countByPriority(),
    };
  }
}

/** Create, change and remove settings. */
export class SettingService {
  constructor(private readonly store: Store) {}

  private get repo(): SettingStore {
    return this.store.settings;
  }

  /** Validate and store a new setting. */
  create(data: Record<string, unknown>): Setting {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseSetting(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Setting {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("setting", id);
    }
    return item;
  }

  list(): Setting[] {
    return this.repo.list();
  }

  /** Change some fields of a setting. */
  update(id: number, changes: Record<string, unknown>): Setting {
    const updated = patchSetting(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a setting nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Setting): void {
    void item; // a setting doesn't point at other records
  }

  toggleEditable(id: number): Setting {
    return this.update(id, { editable: !this.get(id).editable });
  }

  /** Totals and breakdowns over every setting. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      editable: this.repo.whereEditable(true).length,
    };
  }
}

/** Create, change and remove audit entries. */
export class AuditEntryService {
  constructor(private readonly store: Store) {}

  private get repo(): AuditEntryStore {
    return this.store.auditEntries;
  }

  /** Validate and store a new audit entry. */
  create(data: Record<string, unknown>): AuditEntry {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseAuditEntry(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): AuditEntry {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("audit entry", id);
    }
    return item;
  }

  list(): AuditEntry[] {
    return this.repo.list();
  }

  /** Change some fields of a audit entry. */
  update(id: number, changes: Record<string, unknown>): AuditEntry {
    const updated = patchAuditEntry(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a audit entry nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: AuditEntry): void {
    void item; // a audit entry doesn't point at other records
  }

  setAction(id: number, value: AuditEntryAction): AuditEntry {
    return this.update(id, { action: value });
  }

  /** Totals and breakdowns over every audit entry. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      byAction: this.repo.countByAction(),
    };
  }
}

/** Create, change and remove notes. */
export class NoteService {
  constructor(private readonly store: Store) {}

  private get repo(): NoteStore {
    return this.store.notes;
  }

  /** Validate and store a new note. */
  create(data: Record<string, unknown>): Note {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseNote(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Note {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("note", id);
    }
    return item;
  }

  list(): Note[] {
    return this.repo.list();
  }

  /** Change some fields of a note. */
  update(id: number, changes: Record<string, unknown>): Note {
    const updated = patchNote(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a note nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Note): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  togglePinned(id: number): Note {
    return this.update(id, { pinned: !this.get(id).pinned });
  }

  /** Totals and breakdowns over every note. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      pinned: this.repo.wherePinned(true).length,
    };
  }
}

/** Create, change and remove reviews. */
export class ReviewService {
  constructor(private readonly store: Store) {}

  private get repo(): ReviewStore {
    return this.store.reviews;
  }

  /** Validate and store a new review. */
  create(data: Record<string, unknown>): Review {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseReview(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Review {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("review", id);
    }
    return item;
  }

  list(): Review[] {
    return this.repo.list();
  }

  /** Change some fields of a review. */
  update(id: number, changes: Record<string, unknown>): Review {
    const updated = patchReview(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a review nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Review): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  /** Add `delta` to the stars (it can't go below zero). */
  adjustStars(id: number, delta: number): Review {
    return this.update(id, { stars: this.get(id).stars + delta });
  }

  toggleVerified(id: number): Review {
    return this.update(id, { verified: !this.get(id).verified });
  }

  /** Totals and breakdowns over every review. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalStars: this.repo.totalStars(),
      averageStars: this.repo.averageStars(),
      verified: this.repo.whereVerified(true).length,
    };
  }
}

/** Create, change and remove contact persons. */
export class ContactPersonService {
  constructor(private readonly store: Store) {}

  private get repo(): ContactPersonStore {
    return this.store.contactPersons;
  }

  /** Validate and store a new contact person. */
  create(data: Record<string, unknown>): ContactPerson {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseContactPerson(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): ContactPerson {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("contact person", id);
    }
    return item;
  }

  list(): ContactPerson[] {
    return this.repo.list();
  }

  /** Change some fields of a contact person. */
  update(id: number, changes: Record<string, unknown>): ContactPerson {
    const updated = patchContactPerson(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a contact person nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: ContactPerson): void {
    if (!this.store.venues.get(item.venueId)) {
      throw new NotFoundError("venue", item.venueId);
    }
  }

  togglePrimary(id: number): ContactPerson {
    return this.update(id, { primary: !this.get(id).primary });
  }

  /** Totals and breakdowns over every contact person. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      primary: this.repo.wherePrimary(true).length,
    };
  }
}

/** The whole kit: storage plus one service per record type. */
export class Services {
  readonly store = new Store();
  readonly venues = new VenueService(this.store);
  readonly concerts = new ConcertService(this.store);
  readonly ticketTypes = new TicketTypeService(this.store);
  readonly attendees = new AttendeeService(this.store);
  readonly tickets = new TicketService(this.store);
  readonly sponsors = new SponsorService(this.store);
  readonly documents = new DocumentService(this.store);
  readonly notifications = new NotificationService(this.store);
  readonly addresses = new AddressService(this.store);
  readonly reminders = new ReminderService(this.store);
  readonly settings = new SettingService(this.store);
  readonly auditEntries = new AuditEntryService(this.store);
  readonly notes = new NoteService(this.store);
  readonly reviews = new ReviewService(this.store);
  readonly contactPersons = new ContactPersonService(this.store);

  /** Fill every store with `count` sample records. */
  seed(count = 3): void {
    for (let i = 1; i <= count; i += 1) {
      this.venues.create(sampleVenue(i));
      this.concerts.create(sampleConcert(i));
      this.ticketTypes.create(sampleTicketType(i));
      this.attendees.create(sampleAttendee(i));
      this.tickets.create(sampleTicket(i));
      this.sponsors.create(sampleSponsor(i));
      this.documents.create(sampleDocument(i));
      this.notifications.create(sampleNotification(i));
      this.addresses.create(sampleAddress(i));
      this.reminders.create(sampleReminder(i));
      this.settings.create(sampleSetting(i));
      this.auditEntries.create(sampleAuditEntry(i));
      this.notes.create(sampleNote(i));
      this.reviews.create(sampleReview(i));
      this.contactPersons.create(sampleContactPerson(i));
    }
  }

  summary(): Record<string, unknown> {
    return {
      venues: this.venues.stats(),
      concerts: this.concerts.stats(),
      ticketTypes: this.ticketTypes.stats(),
      attendees: this.attendees.stats(),
      tickets: this.tickets.stats(),
      sponsors: this.sponsors.stats(),
      documents: this.documents.stats(),
      notifications: this.notifications.stats(),
      addresses: this.addresses.stats(),
      reminders: this.reminders.stats(),
      settings: this.settings.stats(),
      auditEntries: this.auditEntries.stats(),
      notes: this.notes.stats(),
      reviews: this.reviews.stats(),
      contactPersons: this.contactPersons.stats(),
    };
  }
}

/** Valid data for a new venue (links point at seeded records). */
export function sampleVenue(i: number): Record<string, unknown> {
  return {
    name: `Venue name ${i}`,
    city: `Venue city ${i}`,
    capacity: i + 1,
    address: `Venue address ${i}`,
    accessible: i % 2 === 1,
  };
}

/** Valid data for a new concert (links point at seeded records). */
export function sampleConcert(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    title: `Concert title ${i}`,
    artist: `Concert artist ${i}`,
    day: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    doorsOpen: `Concert doors open ${i}`,
    status: CONCERT_STATUS_VALUES[i % 5],
  };
}

/** Valid data for a new ticket type (links point at seeded records). */
export function sampleTicketType(i: number): Record<string, unknown> {
  return {
    concertId: ((i - 1) % 3) + 1,
    name: `Ticket type name ${i}`,
    price: Math.round((10 * i + 0.99) * 100) / 100,
    quantity: i + 1,
    sold: i + 1,
    seated: i % 2 === 1,
  };
}

/** Valid data for a new attendee (links point at seeded records). */
export function sampleAttendee(i: number): Record<string, unknown> {
  return {
    name: `Attendee name ${i}`,
    email: `attendee${i}@example.com`,
    phone: `Attendee phone ${i}`,
    country: `Attendee country ${i}`,
    newsletter: i % 2 === 1,
  };
}

/** Valid data for a new ticket (links point at seeded records). */
export function sampleTicket(i: number): Record<string, unknown> {
  return {
    ticketTypeId: ((i - 1) % 3) + 1,
    attendeeId: ((i - 1) % 3) + 1,
    bought: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    code: `Ticket code ${i}`,
    status: TICKET_STATUS_VALUES[i % 4],
    pricePaid: Math.round((10 * i + 0.99) * 100) / 100,
  };
}

/** Valid data for a new sponsor (links point at seeded records). */
export function sampleSponsor(i: number): Record<string, unknown> {
  return {
    concertId: ((i - 1) % 3) + 1,
    company: `Sponsor company ${i}`,
    amount: Math.round((10 * i + 0.99) * 100) / 100,
    tier: SPONSOR_TIER_VALUES[i % 4],
    logoUrl: `Sponsor logo url ${i}`,
  };
}

/** Valid data for a new document (links point at seeded records). */
export function sampleDocument(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    title: `Document title ${i}`,
    pages: i + 1,
    signed: i % 2 === 1,
    version: i + 1,
    issued: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
  };
}

/** Valid data for a new notification (links point at seeded records). */
export function sampleNotification(i: number): Record<string, unknown> {
  return {
    recipient: `notification${i}@example.com`,
    title: `Notification title ${i}`,
    sent: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    channel: NOTIFICATION_CHANNEL_VALUES[i % 3],
    read: i % 2 === 1,
  };
}

/** Valid data for a new address (links point at seeded records). */
export function sampleAddress(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    street: `Address street ${i}`,
    city: `Address city ${i}`,
    postcode: `Address postcode ${i}`,
    country: `Address country ${i}`,
    billing: i % 2 === 1,
  };
}

/** Valid data for a new reminder (links point at seeded records). */
export function sampleReminder(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    title: `Reminder title ${i}`,
    remindOn: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    done: i % 2 === 1,
    priority: REMINDER_PRIORITY_VALUES[i % 3],
  };
}

/** Valid data for a new setting (links point at seeded records). */
export function sampleSetting(i: number): Record<string, unknown> {
  return {
    keyName: `Setting key name ${i}`,
    value: `Setting value ${i}`,
    editable: i % 2 === 1,
    changed: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
  };
}

/** Valid data for a new audit entry (links point at seeded records). */
export function sampleAuditEntry(i: number): Record<string, unknown> {
  return {
    actor: `Audit entry actor ${i}`,
    action: AUDIT_ENTRY_ACTION_VALUES[i % 5],
    at: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    details: `Notes about audit entry ${i}.`,
  };
}

/** Valid data for a new note (links point at seeded records). */
export function sampleNote(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    subject: `Note subject ${i}`,
    body: `Notes about note ${i}.`,
    pinned: i % 2 === 1,
    written: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
  };
}

/** Valid data for a new review (links point at seeded records). */
export function sampleReview(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    author: `Review author ${i}`,
    stars: i + 1,
    comment: `Notes about review ${i}.`,
    verified: i % 2 === 1,
    posted: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
  };
}

/** Valid data for a new contact person (links point at seeded records). */
export function sampleContactPerson(i: number): Record<string, unknown> {
  return {
    venueId: ((i - 1) % 3) + 1,
    name: `Contact person name ${i}`,
    email: `contact_person${i}@example.com`,
    phone: `Contact person phone ${i}`,
    role: `Contact person role ${i}`,
    primary: i % 2 === 1,
  };
}
