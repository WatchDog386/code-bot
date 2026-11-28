/** In-memory storage for the Restaurant Orders kit, with the lookups the services need. */

import {
  AUDIT_ENTRY_ACTION_VALUES,
  Address,
  AuditEntry,
  AuditEntryAction,
  Booking,
  CUSTOMER_ORDER_STATUS_VALUES,
  ContactPerson,
  CustomerOrder,
  CustomerOrderStatus,
  DINING_TABLE_AREA_VALUES,
  DiningTable,
  DiningTableArea,
  Document,
  MenuCategory,
  MenuItem,
  NOTIFICATION_CHANNEL_VALUES,
  Note,
  Notification,
  NotificationChannel,
  OrderLine,
  REMINDER_PRIORITY_VALUES,
  Reminder,
  ReminderPriority,
  Review,
  Setting,
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

/** Every menu category. */
export class MenuCategoryStore extends Collection<MenuCategory> {
  findByName(value: string): MenuCategory[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): MenuCategory[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  betweenPosition(low: number, high: number): MenuCategory[] {
    return this.where((item) => item.position >= low && item.position <= high);
  }

  totalPosition(): number {
    return this.list().reduce((sum, item) => sum + item.position, 0);
  }

  averagePosition(): number {
    const items = this.list();
    return items.length ? this.totalPosition() / items.length : 0;
  }

  maxPosition(): MenuCategory | undefined {
    return this.list().reduce<MenuCategory | undefined>((best, item) => (best === undefined || item.position > best.position ? item : best), undefined);
  }

  whereVisible(flag = true): MenuCategory[] {
    return this.where((item) => item.visible === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): MenuCategory[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every menu item. */
export class MenuItemStore extends Collection<MenuItem> {
  forMenuCategory(id: number): MenuItem[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
  }

  findByName(value: string): MenuItem[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): MenuItem[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  betweenPrice(low: number, high: number): MenuItem[] {
    return this.where((item) => item.price >= low && item.price <= high);
  }

  totalPrice(): number {
    return this.list().reduce((sum, item) => sum + item.price, 0);
  }

  averagePrice(): number {
    const items = this.list();
    return items.length ? this.totalPrice() / items.length : 0;
  }

  maxPrice(): MenuItem | undefined {
    return this.list().reduce<MenuItem | undefined>((best, item) => (best === undefined || item.price > best.price ? item : best), undefined);
  }

  betweenCalories(low: number, high: number): MenuItem[] {
    return this.where((item) => item.calories >= low && item.calories <= high);
  }

  totalCalories(): number {
    return this.list().reduce((sum, item) => sum + item.calories, 0);
  }

  averageCalories(): number {
    const items = this.list();
    return items.length ? this.totalCalories() / items.length : 0;
  }

  maxCalories(): MenuItem | undefined {
    return this.list().reduce<MenuItem | undefined>((best, item) => (best === undefined || item.calories > best.calories ? item : best), undefined);
  }

  whereSpicy(flag = true): MenuItem[] {
    return this.where((item) => item.spicy === flag);
  }

  whereVegetarian(flag = true): MenuItem[] {
    return this.where((item) => item.vegetarian === flag);
  }

  betweenPrepMinutes(low: number, high: number): MenuItem[] {
    return this.where((item) => item.prepMinutes >= low && item.prepMinutes <= high);
  }

  totalPrepMinutes(): number {
    return this.list().reduce((sum, item) => sum + item.prepMinutes, 0);
  }

  averagePrepMinutes(): number {
    const items = this.list();
    return items.length ? this.totalPrepMinutes() / items.length : 0;
  }

  maxPrepMinutes(): MenuItem | undefined {
    return this.list().reduce<MenuItem | undefined>((best, item) => (best === undefined || item.prepMinutes > best.prepMinutes ? item : best), undefined);
  }

  /** Records where any text field contains `text`. */
  search(text: string): MenuItem[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every dining table. */
export class DiningTableStore extends Collection<DiningTable> {
  findByLabel(value: string): DiningTable[] {
    return this.where((item) => item.label === value);
  }

  searchLabel(text: string): DiningTable[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.label.toLowerCase().includes(needle));
  }

  betweenSeats(low: number, high: number): DiningTable[] {
    return this.where((item) => item.seats >= low && item.seats <= high);
  }

  totalSeats(): number {
    return this.list().reduce((sum, item) => sum + item.seats, 0);
  }

  averageSeats(): number {
    const items = this.list();
    return items.length ? this.totalSeats() / items.length : 0;
  }

  maxSeats(): DiningTable | undefined {
    return this.list().reduce<DiningTable | undefined>((best, item) => (best === undefined || item.seats > best.seats ? item : best), undefined);
  }

  withArea(value: DiningTableArea): DiningTable[] {
    return this.where((item) => item.area === value);
  }

  countByArea(): Record<DiningTableArea, number> {
    const counts = Object.fromEntries(DINING_TABLE_AREA_VALUES.map((value) => [value, 0])) as Record<DiningTableArea, number>;
    for (const item of this.list()) {
      counts[item.area] += 1;
    }
    return counts;
  }

  whereActive(flag = true): DiningTable[] {
    return this.where((item) => item.active === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): DiningTable[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.label].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every customer order. */
export class CustomerOrderStore extends Collection<CustomerOrder> {
  forDiningTable(id: number): CustomerOrder[] {
    return this.where((item) => item.diningTableId === id);
  }

  countForDiningTable(id: number): number {
    return this.forDiningTable(id).length;
  }

  openedBefore(day: string): CustomerOrder[] {
    return this.where((item) => item.opened < day);
  }

  openedAfter(day: string): CustomerOrder[] {
    return this.where((item) => item.opened > day);
  }

  openedOn(day: string): CustomerOrder[] {
    return this.where((item) => item.opened === day);
  }

  betweenGuests(low: number, high: number): CustomerOrder[] {
    return this.where((item) => item.guests >= low && item.guests <= high);
  }

  totalGuests(): number {
    return this.list().reduce((sum, item) => sum + item.guests, 0);
  }

  averageGuests(): number {
    const items = this.list();
    return items.length ? this.totalGuests() / items.length : 0;
  }

  maxGuests(): CustomerOrder | undefined {
    return this.list().reduce<CustomerOrder | undefined>((best, item) => (best === undefined || item.guests > best.guests ? item : best), undefined);
  }

  betweenTotal(low: number, high: number): CustomerOrder[] {
    return this.where((item) => item.total >= low && item.total <= high);
  }

  totalTotal(): number {
    return this.list().reduce((sum, item) => sum + item.total, 0);
  }

  averageTotal(): number {
    const items = this.list();
    return items.length ? this.totalTotal() / items.length : 0;
  }

  maxTotal(): CustomerOrder | undefined {
    return this.list().reduce<CustomerOrder | undefined>((best, item) => (best === undefined || item.total > best.total ? item : best), undefined);
  }

  withStatus(value: CustomerOrderStatus): CustomerOrder[] {
    return this.where((item) => item.status === value);
  }

  countByStatus(): Record<CustomerOrderStatus, number> {
    const counts = Object.fromEntries(CUSTOMER_ORDER_STATUS_VALUES.map((value) => [value, 0])) as Record<CustomerOrderStatus, number>;
    for (const item of this.list()) {
      counts[item.status] += 1;
    }
    return counts;
  }

  findByServer(value: string): CustomerOrder[] {
    return this.where((item) => item.server === value);
  }

  searchServer(text: string): CustomerOrder[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.server.toLowerCase().includes(needle));
  }

  /** Records where any text field contains `text`. */
  search(text: string): CustomerOrder[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.server].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every order line. */
export class OrderLineStore extends Collection<OrderLine> {
  forCustomerOrder(id: number): OrderLine[] {
    return this.where((item) => item.customerOrderId === id);
  }

  countForCustomerOrder(id: number): number {
    return this.forCustomerOrder(id).length;
  }

  forMenuItem(id: number): OrderLine[] {
    return this.where((item) => item.menuItemId === id);
  }

  countForMenuItem(id: number): number {
    return this.forMenuItem(id).length;
  }

  betweenQuantity(low: number, high: number): OrderLine[] {
    return this.where((item) => item.quantity >= low && item.quantity <= high);
  }

  totalQuantity(): number {
    return this.list().reduce((sum, item) => sum + item.quantity, 0);
  }

  averageQuantity(): number {
    const items = this.list();
    return items.length ? this.totalQuantity() / items.length : 0;
  }

  maxQuantity(): OrderLine | undefined {
    return this.list().reduce<OrderLine | undefined>((best, item) => (best === undefined || item.quantity > best.quantity ? item : best), undefined);
  }

  betweenUnitPrice(low: number, high: number): OrderLine[] {
    return this.where((item) => item.unitPrice >= low && item.unitPrice <= high);
  }

  totalUnitPrice(): number {
    return this.list().reduce((sum, item) => sum + item.unitPrice, 0);
  }

  averageUnitPrice(): number {
    const items = this.list();
    return items.length ? this.totalUnitPrice() / items.length : 0;
  }

  maxUnitPrice(): OrderLine | undefined {
    return this.list().reduce<OrderLine | undefined>((best, item) => (best === undefined || item.unitPrice > best.unitPrice ? item : best), undefined);
  }

  findByNote(value: string): OrderLine[] {
    return this.where((item) => item.note === value);
  }

  searchNote(text: string): OrderLine[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.note.toLowerCase().includes(needle));
  }

  /** Records where any text field contains `text`. */
  search(text: string): OrderLine[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.note].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every booking. */
export class BookingStore extends Collection<Booking> {
  forDiningTable(id: number): Booking[] {
    return this.where((item) => item.diningTableId === id);
  }

  countForDiningTable(id: number): number {
    return this.forDiningTable(id).length;
  }

  findByName(value: string): Booking[] {
    return this.where((item) => item.name === value);
  }

  searchName(text: string): Booking[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.name.toLowerCase().includes(needle));
  }

  findByPhone(value: string): Booking[] {
    return this.where((item) => item.phone === value);
  }

  searchPhone(text: string): Booking[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.phone.toLowerCase().includes(needle));
  }

  dayBefore(day: string): Booking[] {
    return this.where((item) => item.day < day);
  }

  dayAfter(day: string): Booking[] {
    return this.where((item) => item.day > day);
  }

  dayOn(day: string): Booking[] {
    return this.where((item) => item.day === day);
  }

  betweenPartySize(low: number, high: number): Booking[] {
    return this.where((item) => item.partySize >= low && item.partySize <= high);
  }

  totalPartySize(): number {
    return this.list().reduce((sum, item) => sum + item.partySize, 0);
  }

  averagePartySize(): number {
    const items = this.list();
    return items.length ? this.totalPartySize() / items.length : 0;
  }

  maxPartySize(): Booking | undefined {
    return this.list().reduce<Booking | undefined>((best, item) => (best === undefined || item.partySize > best.partySize ? item : best), undefined);
  }

  whereConfirmed(flag = true): Booking[] {
    return this.where((item) => item.confirmed === flag);
  }

  /** Records where any text field contains `text`. */
  search(text: string): Booking[] {
    const needle = text.trim().toLowerCase();
    return this.where((item) => [item.name, item.phone].some((value) => value.toLowerCase().includes(needle)));
  }
}

/** Every document. */
export class DocumentStore extends Collection<Document> {
  forMenuCategory(id: number): Document[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
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
  forMenuCategory(id: number): Address[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
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
  forMenuCategory(id: number): Reminder[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
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
  forMenuCategory(id: number): Note[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
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
  forMenuCategory(id: number): Review[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
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
  forMenuCategory(id: number): ContactPerson[] {
    return this.where((item) => item.menuCategoryId === id);
  }

  countForMenuCategory(id: number): number {
    return this.forMenuCategory(id).length;
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
