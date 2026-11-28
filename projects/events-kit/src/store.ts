/** In-memory storage for the Event Ticketing kit, with the lookups the services need. */

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
  Venue,
} from "./models";

/** Records kept in a Map, keyed by id. */
export class Collection<T extends { id: number }> {
  protected items = new Map<number, T>();
  protected nextId = 1;

  /** Store a new record under the next id. */
  add(item: T): T {
    const stored: T = { ...item, id: this.nextId };
    this.nextId += 1;
    this.items.set(stored.id, stored);
    return stored;
  }

  get(id: number): T | undefined {
    return this.items.get(id);
  }

  /** Every record, oldest first. */
  list(): T[] {
    return [...this.items.values()].sort((a, b) => a.id - b.id);
  }

  /** Replace an existing record. */
  save(item: T): T {
    if (!this.items.has(item.id)) {
      throw new Error(`no record ${item.id}`);
    }
    this.items.set(item.id, item);
    return item;
  }

  remove(id: number): boolean {
    return this.items.delete(id);
  }

  count(): number {
    return this.items.size;
  }

  clear(): void {
    this.items.clear();
    this.nextId = 1;
  }

  where(keep: (item: T) => boolean): T[] {
    return this.list().filter(keep);
  }

  first(keep: (item: T) => boolean): T | undefined {
    return this.list().find(keep);
  }

  /** One page of records (pages start at 1). */
  page(number = 1, size = 20): T[] {
    const start = Math.max(0, (number - 1) * size);
    return this.list().slice(start, start + size);
  }

  toJSON(): string {
    return JSON.stringify(this.list());
  }

  /** Load records exported with toJSON(); returns how many. */
  load(rows: T[]): number {
    for (const row of rows) {
      this.items.set(row.id, row);
      this.nextId = Math.max(this.nextId, row.id + 1);
    }
    return rows.length;
  }
}

/** Every venue. */
export class VenueStore extends Collection<Venue> {
  findByName(value: string): Venue[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): Venue[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  findByCity(value: string): Venue[] {
    return this.where((item) => item.city === value);
  }

  searchCity(text: string): Venue[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.city.toLowerCase().includes(needle));
  }

  betweenCapacity(low: number, high: number): Venue[] {
    return this.where((item) => item.capacity >= low && item.capacity <= high);
  }

  totalCapacity(): number {
    return this.list().reduce((sum, item) => sum + item.capacity, 0);
  }

  averageCapacity(): number {
    const items = this.list();
    return items.length ? this.totalCapacity() / items.length : 0;
  }

  maxCapacity(): Venue | undefined {
    return this.list().reduce<Venue | undefined>((best, item) => (best === undefined || item.capacity > best.capacity ? item : best), undefined);
  }

  findByAddress(value: string): Venue[] {
    return this.where((item) => item.address === value);
  }

  searchAddress(text: string): Venue[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.address.toLowerCase().includes(needle));
  }

  whereAccessible(flag = true): Venue[] {
    return this.where((item) => item.accessible === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Venue[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name, item.city, item.address].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every concert. */
export class ConcertStore extends Collection<Concert> {
  forVenue(id: number): Concert[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findByTitle(value: string): Concert[] {
    return this.where((item) => item.title === value);
  }

  searchTitle(text: string): Concert[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.title.toLowerCase().includes(needle));
  }

  findByArtist(value: string): Concert[] {
    return this.where((item) => item.artist === value);
  }

  searchArtist(text: string): Concert[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.artist.toLowerCase().includes(needle));
  }

  dayBefore(day: string): Concert[] {
    return this.where((item) => item.day < day);
  }

  dayAfter(day: string): Concert[] {
    return this.where((item) => item.day > day);
  }

  dayOn(day: string): Concert[] {
    return this.where((item) => item.day === day);
  }

  findByDoorsOpen(value: string): Concert[] {
    return this.where((item) => item.doorsOpen === value);
  }

  searchDoorsOpen(text: string): Concert[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.doorsOpen.toLowerCase().includes(needle));
  }

  withStatus(value: ConcertStatus): Concert[] {
    return this.where((item) => item.status === value);
  }

  countByStatus(): Record<ConcertStatus, number> {
    const counts = Object.fromEntries(CONCERT_STATUS_VALUES.map((value) => [value, 0])) as Record<ConcertStatus, number>;
    for (const item of this.list()) {
      counts[item.status] += 1;
    }
    return counts;
  }

  /** Records where any text field contains `text`. */
  search(text: string): Concert[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.title, item.artist, item.doorsOpen].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every ticket type. */
export class TicketTypeStore extends Collection<TicketType> {
  forConcert(id: number): TicketType[] {
    return this.where((item) => item.concertId === id);
  }

  countForConcert(id: number): number {
    return this.forConcert(id).length;
  }

  findByName(value: string): TicketType[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): TicketType[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  betweenPrice(low: number, high: number): TicketType[] {
    return this.where((item) => item.price >= low && item.price <= high);
  }

  totalPrice(): number {
    return this.list().reduce((sum, item) => sum + item.price, 0);
  }

  averagePrice(): number {
    const items = this.list();
    return items.length ? this.totalPrice() / items.length : 0;
  }

  maxPrice(): TicketType | undefined {
    return this.list().reduce<TicketType | undefined>((best, item) => (best === undefined || item.price > best.price ? item : best), undefined);
  }

  betweenQuantity(low: number, high: number): TicketType[] {
    return this.where((item) => item.quantity >= low && item.quantity <= high);
  }

  totalQuantity(): number {
    return this.list().reduce((sum, item) => sum + item.quantity, 0);
  }

  averageQuantity(): number {
    const items = this.list();
    return items.length ? this.totalQuantity() / items.length : 0;
  }

  maxQuantity(): TicketType | undefined {
    return this.list().reduce<TicketType | undefined>((best, item) => (best === undefined || item.quantity > best.quantity ? item : best), undefined);
  }

  betweenSold(low: number, high: number): TicketType[] {
    return this.where((item) => item.sold >= low && item.sold <= high);
  }

  totalSold(): number {
    return this.list().reduce((sum, item) => sum + item.sold, 0);
  }

  averageSold(): number {
    const items = this.list();
    return items.length ? this.totalSold() / items.length : 0;
  }

  maxSold(): TicketType | undefined {
    return this.list().reduce<TicketType | undefined>((best, item) => (best === undefined || item.sold > best.sold ? item : best), undefined);
  }

  whereSeated(flag = true): TicketType[] {
    return this.where((item) => item.seated === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): TicketType[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every attendee. */
export class AttendeeStore extends Collection<Attendee> {
  findByName(value: string): Attendee[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): Attendee[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  findByEmail(value: string): Attendee[] {
    return this.where((item) => item.email === value);
  }

  searchEmail(text: string): Attendee[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.email.toLowerCase().includes(needle));
  }

  findByPhone(value: string): Attendee[] {
    return this.where((item) => item.phone === value);
  }

  searchPhone(text: string): Attendee[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.phone.toLowerCase().includes(needle));
  }

  findByCountry(value: string): Attendee[] {
    return this.where((item) => item.country === value);
  }

  searchCountry(text: string): Attendee[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.country.toLowerCase().includes(needle));
  }

  whereNewsletter(flag = true): Attendee[] {
    return this.where((item) => item.newsletter === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Attendee[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name, item.email, item.phone, item.country].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every ticket. */
export class TicketStore extends Collection<Ticket> {
  forTicketType(id: number): Ticket[] {
    return this.where((item) => item.ticketTypeId === id);
  }

  countForTicketType(id: number): number {
    return this.forTicketType(id).length;
  }

  forAttendee(id: number): Ticket[] {
    return this.where((item) => item.attendeeId === id);
  }

  countForAttendee(id: number): number {
    return this.forAttendee(id).length;
  }

  boughtBefore(day: string): Ticket[] {
    return this.where((item) => item.bought < day);
  }

  boughtAfter(day: string): Ticket[] {
    return this.where((item) => item.bought > day);
  }

  boughtOn(day: string): Ticket[] {
    return this.where((item) => item.bought === day);
  }

  findByCode(value: string): Ticket[] {
    return this.where((item) => item.code === value);
  }

  searchCode(text: string): Ticket[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.code.toLowerCase().includes(needle));
  }

  withStatus(value: TicketStatus): Ticket[] {
    return this.where((item) => item.status === value);
  }

  countByStatus(): Record<TicketStatus, number> {
    const counts = Object.fromEntries(TICKET_STATUS_VALUES.map((value) => [value, 0])) as Record<TicketStatus, number>;
    for (const item of this.list()) {
      counts[item.status] += 1;
    }
    return counts;
  }

  betweenPricePaid(low: number, high: number): Ticket[] {
    return this.where((item) => item.pricePaid >= low && item.pricePaid <= high);
  }

  totalPricePaid(): number {
    return this.list().reduce((sum, item) => sum + item.pricePaid, 0);
  }

  averagePricePaid(): number {
    const items = this.list();
    return items.length ? this.totalPricePaid() / items.length : 0;
  }

  maxPricePaid(): Ticket | undefined {
    return this.list().reduce<Ticket | undefined>((best, item) => (best === undefined || item.pricePaid > best.pricePaid ? item : best), undefined);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Ticket[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.code].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every sponsor. */
export class SponsorStore extends Collection<Sponsor> {
  forConcert(id: number): Sponsor[] {
    return this.where((item) => item.concertId === id);
  }

  countForConcert(id: number): number {
    return this.forConcert(id).length;
  }

  findByCompany(value: string): Sponsor[] {
    return this.where((item) => item.company === value);
  }

  searchCompany(text: string): Sponsor[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.company.toLowerCase().includes(needle));
  }

  betweenAmount(low: number, high: number): Sponsor[] {
    return this.where((item) => item.amount >= low && item.amount <= high);
  }

  totalAmount(): number {
    return this.list().reduce((sum, item) => sum + item.amount, 0);
  }

  averageAmount(): number {
    const items = this.list();
    return items.length ? this.totalAmount() / items.length : 0;
  }

  maxAmount(): Sponsor | undefined {
    return this.list().reduce<Sponsor | undefined>((best, item) => (best === undefined || item.amount > best.amount ? item : best), undefined);
  }

  withTier(value: SponsorTier): Sponsor[] {
    return this.where((item) => item.tier === value);
  }

  countByTier(): Record<SponsorTier, number> {
    const counts = Object.fromEntries(SPONSOR_TIER_VALUES.map((value) => [value, 0])) as Record<SponsorTier, number>;
    for (const item of this.list()) {
      counts[item.tier] += 1;
    }
    return counts;
  }

  findByLogoUrl(value: string): Sponsor[] {
    return this.where((item) => item.logoUrl === value);
  }

  searchLogoUrl(text: string): Sponsor[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.logoUrl.toLowerCase().includes(needle));
  }

  /** Records where any text field contains `text`. */
  search(text: string): Sponsor[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.company, item.logoUrl].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every document. */
export class DocumentStore extends Collection<Document> {
  forVenue(id: number): Document[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findByTitle(value: string): Document[] {
    return this.where((item) => item.title === value);
  }

  searchTitle(text: string): Document[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.title.toLowerCase().includes(needle));
  }

  betweenPages(low: number, high: number): Document[] {
    return this.where((item) => item.pages >= low && item.pages <= high);
  }

  totalPages(): number {
    return this.list().reduce((sum, item) => sum + item.pages, 0);
  }

  averagePages(): number {
    const items = this.list();
    return items.length ? this.totalPages() / items.length : 0;
  }

  maxPages(): Document | undefined {
    return this.list().reduce<Document | undefined>((best, item) => (best === undefined || item.pages > best.pages ? item : best), undefined);
  }

  whereSigned(flag = true): Document[] {
    return this.where((item) => item.signed === flag);
  }

  betweenVersion(low: number, high: number): Document[] {
    return this.where((item) => item.version >= low && item.version <= high);
  }

  totalVersion(): number {
    return this.list().reduce((sum, item) => sum + item.version, 0);
  }

  averageVersion(): number {
    const items = this.list();
    return items.length ? this.totalVersion() / items.length : 0;
  }

  maxVersion(): Document | undefined {
    return this.list().reduce<Document | undefined>((best, item) => (best === undefined || item.version > best.version ? item : best), undefined);
  }

  issuedBefore(day: string): Document[] {
    return this.where((item) => item.issued < day);
  }

  issuedAfter(day: string): Document[] {
    return this.where((item) => item.issued > day);
  }

  issuedOn(day: string): Document[] {
    return this.where((item) => item.issued === day);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Document[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.title].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every notification. */
export class NotificationStore extends Collection<Notification> {
  findByRecipient(value: string): Notification[] {
    return this.where((item) => item.recipient === value);
  }

  searchRecipient(text: string): Notification[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.recipient.toLowerCase().includes(needle));
  }

  findByTitle(value: string): Notification[] {
    return this.where((item) => item.title === value);
  }

  searchTitle(text: string): Notification[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.title.toLowerCase().includes(needle));
  }

  sentBefore(day: string): Notification[] {
    return this.where((item) => item.sent < day);
  }

  sentAfter(day: string): Notification[] {
    return this.where((item) => item.sent > day);
  }

  sentOn(day: string): Notification[] {
    return this.where((item) => item.sent === day);
  }

  withChannel(value: NotificationChannel): Notification[] {
    return this.where((item) => item.channel === value);
  }

  countByChannel(): Record<NotificationChannel, number> {
    const counts = Object.fromEntries(NOTIFICATION_CHANNEL_VALUES.map((value) => [value, 0])) as Record<NotificationChannel, number>;
    for (const item of this.list()) {
      counts[item.channel] += 1;
    }
    return counts;
  }

  whereRead(flag = true): Notification[] {
    return this.where((item) => item.read === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Notification[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.recipient, item.title].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every address. */
export class AddressStore extends Collection<Address> {
  forVenue(id: number): Address[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findByStreet(value: string): Address[] {
    return this.where((item) => item.street === value);
  }

  searchStreet(text: string): Address[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.street.toLowerCase().includes(needle));
  }

  findByCity(value: string): Address[] {
    return this.where((item) => item.city === value);
  }

  searchCity(text: string): Address[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.city.toLowerCase().includes(needle));
  }

  findByPostcode(value: string): Address[] {
    return this.where((item) => item.postcode === value);
  }

  searchPostcode(text: string): Address[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.postcode.toLowerCase().includes(needle));
  }

  findByCountry(value: string): Address[] {
    return this.where((item) => item.country === value);
  }

  searchCountry(text: string): Address[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.country.toLowerCase().includes(needle));
  }

  whereBilling(flag = true): Address[] {
    return this.where((item) => item.billing === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Address[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.street, item.city, item.postcode, item.country].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every reminder. */
export class ReminderStore extends Collection<Reminder> {
  forVenue(id: number): Reminder[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findByTitle(value: string): Reminder[] {
    return this.where((item) => item.title === value);
  }

  searchTitle(text: string): Reminder[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.title.toLowerCase().includes(needle));
  }

  remindOnBefore(day: string): Reminder[] {
    return this.where((item) => item.remindOn < day);
  }

  remindOnAfter(day: string): Reminder[] {
    return this.where((item) => item.remindOn > day);
  }

  remindOnOn(day: string): Reminder[] {
    return this.where((item) => item.remindOn === day);
  }

  whereDone(flag = true): Reminder[] {
    return this.where((item) => item.done === flag);
  }

  withPriority(value: ReminderPriority): Reminder[] {
    return this.where((item) => item.priority === value);
  }

  countByPriority(): Record<ReminderPriority, number> {
    const counts = Object.fromEntries(REMINDER_PRIORITY_VALUES.map((value) => [value, 0])) as Record<ReminderPriority, number>;
    for (const item of this.list()) {
      counts[item.priority] += 1;
    }
    return counts;
  }

  /** Records where any text field contains `text`. */
  search(text: string): Reminder[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.title].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every setting. */
export class SettingStore extends Collection<Setting> {
  findByKeyName(value: string): Setting[] {
    return this.where((item) => item.keyName === value);
  }

  searchKeyName(text: string): Setting[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.keyName.toLowerCase().includes(needle));
  }

  findByValue(value: string): Setting[] {
    return this.where((item) => item.value === value);
  }

  searchValue(text: string): Setting[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.value.toLowerCase().includes(needle));
  }

  whereEditable(flag = true): Setting[] {
    return this.where((item) => item.editable === flag);
  }

  changedBefore(day: string): Setting[] {
    return this.where((item) => item.changed < day);
  }

  changedAfter(day: string): Setting[] {
    return this.where((item) => item.changed > day);
  }

  changedOn(day: string): Setting[] {
    return this.where((item) => item.changed === day);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Setting[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.keyName, item.value].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every audit entry. */
export class AuditEntryStore extends Collection<AuditEntry> {
  findByActor(value: string): AuditEntry[] {
    return this.where((item) => item.actor === value);
  }

  searchActor(text: string): AuditEntry[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.actor.toLowerCase().includes(needle));
  }

  withAction(value: AuditEntryAction): AuditEntry[] {
    return this.where((item) => item.action === value);
  }

  countByAction(): Record<AuditEntryAction, number> {
    const counts = Object.fromEntries(AUDIT_ENTRY_ACTION_VALUES.map((value) => [value, 0])) as Record<AuditEntryAction, number>;
    for (const item of this.list()) {
      counts[item.action] += 1;
    }
    return counts;
  }

  atBefore(day: string): AuditEntry[] {
    return this.where((item) => item.at < day);
  }

  atAfter(day: string): AuditEntry[] {
    return this.where((item) => item.at > day);
  }

  atOn(day: string): AuditEntry[] {
    return this.where((item) => item.at === day);
  }

  findByDetails(value: string): AuditEntry[] {
    return this.where((item) => item.details === value);
  }

  searchDetails(text: string): AuditEntry[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.details.toLowerCase().includes(needle));
  }

  /** Records where any text field contains `text`. */
  search(text: string): AuditEntry[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.actor, item.details].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every note. */
export class NoteStore extends Collection<Note> {
  forVenue(id: number): Note[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findBySubject(value: string): Note[] {
    return this.where((item) => item.subject === value);
  }

  searchSubject(text: string): Note[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.subject.toLowerCase().includes(needle));
  }

  findByBody(value: string): Note[] {
    return this.where((item) => item.body === value);
  }

  searchBody(text: string): Note[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.body.toLowerCase().includes(needle));
  }

  wherePinned(flag = true): Note[] {
    return this.where((item) => item.pinned === flag);
  }

  writtenBefore(day: string): Note[] {
    return this.where((item) => item.written < day);
  }

  writtenAfter(day: string): Note[] {
    return this.where((item) => item.written > day);
  }

  writtenOn(day: string): Note[] {
    return this.where((item) => item.written === day);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Note[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.subject, item.body].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every review. */
export class ReviewStore extends Collection<Review> {
  forVenue(id: number): Review[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findByAuthor(value: string): Review[] {
    return this.where((item) => item.author === value);
  }

  searchAuthor(text: string): Review[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.author.toLowerCase().includes(needle));
  }

  betweenStars(low: number, high: number): Review[] {
    return this.where((item) => item.stars >= low && item.stars <= high);
  }

  totalStars(): number {
    return this.list().reduce((sum, item) => sum + item.stars, 0);
  }

  averageStars(): number {
    const items = this.list();
    return items.length ? this.totalStars() / items.length : 0;
  }

  maxStars(): Review | undefined {
    return this.list().reduce<Review | undefined>((best, item) => (best === undefined || item.stars > best.stars ? item : best), undefined);
  }

  findByComment(value: string): Review[] {
    return this.where((item) => item.comment === value);
  }

  searchComment(text: string): Review[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.comment.toLowerCase().includes(needle));
  }

  whereVerified(flag = true): Review[] {
    return this.where((item) => item.verified === flag);
  }

  postedBefore(day: string): Review[] {
    return this.where((item) => item.posted < day);
  }

  postedAfter(day: string): Review[] {
    return this.where((item) => item.posted > day);
  }

  postedOn(day: string): Review[] {
    return this.where((item) => item.posted === day);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Review[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.author, item.comment].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every contact person. */
export class ContactPersonStore extends Collection<ContactPerson> {
  forVenue(id: number): ContactPerson[] {
    return this.where((item) => item.venueId === id);
  }

  countForVenue(id: number): number {
    return this.forVenue(id).length;
  }

  findByName(value: string): ContactPerson[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): ContactPerson[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  findByEmail(value: string): ContactPerson[] {
    return this.where((item) => item.email === value);
  }

  searchEmail(text: string): ContactPerson[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.email.toLowerCase().includes(needle));
  }

  findByPhone(value: string): ContactPerson[] {
    return this.where((item) => item.phone === value);
  }

  searchPhone(text: string): ContactPerson[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.phone.toLowerCase().includes(needle));
  }

  findByRole(value: string): ContactPerson[] {
    return this.where((item) => item.role === value);
  }

  searchRole(text: string): ContactPerson[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.role.toLowerCase().includes(needle));
  }

  wherePrimary(flag = true): ContactPerson[] {
    return this.where((item) => item.primary === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): ContactPerson[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name, item.email, item.phone, item.role].some((value) => value.toLowerCase().includes(needle)));
  }
}
