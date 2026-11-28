/**
 * Business rules for the Restaurant Orders kit: validation, links between records (a record
 * can't point at something missing, or be deleted while others point at it), small
 * domain operations and statistics.
 */

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
  ValidationError,
  parseAddress,
  parseAuditEntry,
  parseBooking,
  parseContactPerson,
  parseCustomerOrder,
  parseDiningTable,
  parseDocument,
  parseMenuCategory,
  parseMenuItem,
  parseNote,
  parseNotification,
  parseOrderLine,
  parseReminder,
  parseReview,
  parseSetting,
  patchAddress,
  patchAuditEntry,
  patchBooking,
  patchContactPerson,
  patchCustomerOrder,
  patchDiningTable,
  patchDocument,
  patchMenuCategory,
  patchMenuItem,
  patchNote,
  patchNotification,
  patchOrderLine,
  patchReminder,
  patchReview,
  patchSetting,
} from "./models";
import {
  MenuCategoryStore,
  MenuItemStore,
  DiningTableStore,
  CustomerOrderStore,
  OrderLineStore,
  BookingStore,
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
  readonly menuCategories = new MenuCategoryStore();
  readonly menuItems = new MenuItemStore();
  readonly diningTables = new DiningTableStore();
  readonly customerOrders = new CustomerOrderStore();
  readonly orderLines = new OrderLineStore();
  readonly bookings = new BookingStore();
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
      menuCategories: this.menuCategories.count(),
      menuItems: this.menuItems.count(),
      diningTables: this.diningTables.count(),
      customerOrders: this.customerOrders.count(),
      orderLines: this.orderLines.count(),
      bookings: this.bookings.count(),
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

/** Create, change and remove menu categories. */
export class MenuCategoryService {
  constructor(private readonly store: Store) {}

  private get repo(): MenuCategoryStore {
    return this.store.menuCategories;
  }

  /** Validate and store a new menu category. */
  create(data: Record<string, unknown>): MenuCategory {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseMenuCategory(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): MenuCategory {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("menu category", id);
    }
    return item;
  }

  list(): MenuCategory[] {
    return this.repo.list();
  }

  /** Change some fields of a menu category. */
  update(id: number, changes: Record<string, unknown>): MenuCategory {
    const updated = patchMenuCategory(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a menu category nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const menuItems = this.store.menuItems.countForMenuCategory(id);
    if (menuItems > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${menuItems} menu items`);
    }
    const documents = this.store.documents.countForMenuCategory(id);
    if (documents > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${documents} documents`);
    }
    const addresses = this.store.addresses.countForMenuCategory(id);
    if (addresses > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${addresses} addresses`);
    }
    const reminders = this.store.reminders.countForMenuCategory(id);
    if (reminders > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${reminders} reminders`);
    }
    const notes = this.store.notes.countForMenuCategory(id);
    if (notes > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${notes} notes`);
    }
    const reviews = this.store.reviews.countForMenuCategory(id);
    if (reviews > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${reviews} reviews`);
    }
    const contactPersons = this.store.contactPersons.countForMenuCategory(id);
    if (contactPersons > 0) {
      throw new ConflictError(`menu category ${id} is still used by ${contactPersons} contact persons`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: MenuCategory): void {
    void item; // a menu category doesn't point at other records
  }

  /** Add `delta` to the position (it can't go below zero). */
  adjustPosition(id: number, delta: number): MenuCategory {
    return this.update(id, { position: this.get(id).position + delta });
  }

  toggleVisible(id: number): MenuCategory {
    return this.update(id, { visible: !this.get(id).visible });
  }

  /** Totals and breakdowns over every menu category. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalPosition: this.repo.totalPosition(),
      averagePosition: this.repo.averagePosition(),
      visible: this.repo.whereVisible(true).length,
    };
  }
}

/** Create, change and remove menu items. */
export class MenuItemService {
  constructor(private readonly store: Store) {}

  private get repo(): MenuItemStore {
    return this.store.menuItems;
  }

  /** Validate and store a new menu item. */
  create(data: Record<string, unknown>): MenuItem {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseMenuItem(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): MenuItem {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("menu item", id);
    }
    return item;
  }

  list(): MenuItem[] {
    return this.repo.list();
  }

  /** Change some fields of a menu item. */
  update(id: number, changes: Record<string, unknown>): MenuItem {
    const updated = patchMenuItem(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a menu item nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const orderLines = this.store.orderLines.countForMenuItem(id);
    if (orderLines > 0) {
      throw new ConflictError(`menu item ${id} is still used by ${orderLines} order lines`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: MenuItem): void {
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
    }
  }

  adjustPrice(id: number, delta: number): MenuItem {
    return this.update(id, { price: Math.round((this.get(id).price + delta) * 100) / 100 });
  }

  /** Add `delta` to the calories (it can't go below zero). */
  adjustCalories(id: number, delta: number): MenuItem {
    return this.update(id, { calories: this.get(id).calories + delta });
  }

  toggleSpicy(id: number): MenuItem {
    return this.update(id, { spicy: !this.get(id).spicy });
  }

  toggleVegetarian(id: number): MenuItem {
    return this.update(id, { vegetarian: !this.get(id).vegetarian });
  }

  /** Add `delta` to the prep minutes (it can't go below zero). */
  adjustPrepMinutes(id: number, delta: number): MenuItem {
    return this.update(id, { prepMinutes: this.get(id).prepMinutes + delta });
  }

  /** Totals and breakdowns over every menu item. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalPrice: this.repo.totalPrice(),
      averagePrice: this.repo.averagePrice(),
      totalCalories: this.repo.totalCalories(),
      averageCalories: this.repo.averageCalories(),
      spicy: this.repo.whereSpicy(true).length,
      vegetarian: this.repo.whereVegetarian(true).length,
      totalPrepMinutes: this.repo.totalPrepMinutes(),
      averagePrepMinutes: this.repo.averagePrepMinutes(),
    };
  }
}

/** Create, change and remove dining tables. */
export class DiningTableService {
  constructor(private readonly store: Store) {}

  private get repo(): DiningTableStore {
    return this.store.diningTables;
  }

  /** Validate and store a new dining table. */
  create(data: Record<string, unknown>): DiningTable {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseDiningTable(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): DiningTable {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("dining table", id);
    }
    return item;
  }

  list(): DiningTable[] {
    return this.repo.list();
  }

  /** Change some fields of a dining table. */
  update(id: number, changes: Record<string, unknown>): DiningTable {
    const updated = patchDiningTable(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a dining table nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const customerOrders = this.store.customerOrders.countForDiningTable(id);
    if (customerOrders > 0) {
      throw new ConflictError(`dining table ${id} is still used by ${customerOrders} customer orders`);
    }
    const bookings = this.store.bookings.countForDiningTable(id);
    if (bookings > 0) {
      throw new ConflictError(`dining table ${id} is still used by ${bookings} bookings`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: DiningTable): void {
    void item; // a dining table doesn't point at other records
  }

  /** Add `delta` to the seats (it can't go below zero). */
  adjustSeats(id: number, delta: number): DiningTable {
    return this.update(id, { seats: this.get(id).seats + delta });
  }

  setArea(id: number, value: DiningTableArea): DiningTable {
    return this.update(id, { area: value });
  }

  toggleActive(id: number): DiningTable {
    return this.update(id, { active: !this.get(id).active });
  }

  /** Totals and breakdowns over every dining table. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalSeats: this.repo.totalSeats(),
      averageSeats: this.repo.averageSeats(),
      byArea: this.repo.countByArea(),
      active: this.repo.whereActive(true).length,
    };
  }
}

/** Create, change and remove customer orders. */
export class CustomerOrderService {
  constructor(private readonly store: Store) {}

  private get repo(): CustomerOrderStore {
    return this.store.customerOrders;
  }

  /** Validate and store a new customer order. */
  create(data: Record<string, unknown>): CustomerOrder {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseCustomerOrder(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): CustomerOrder {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("customer order", id);
    }
    return item;
  }

  list(): CustomerOrder[] {
    return this.repo.list();
  }

  /** Change some fields of a customer order. */
  update(id: number, changes: Record<string, unknown>): CustomerOrder {
    const updated = patchCustomerOrder(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a customer order nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    const orderLines = this.store.orderLines.countForCustomerOrder(id);
    if (orderLines > 0) {
      throw new ConflictError(`customer order ${id} is still used by ${orderLines} order lines`);
    }
    this.repo.remove(id);
  }

  private checkLinks(item: CustomerOrder): void {
    if (!this.store.diningTables.get(item.diningTableId)) {
      throw new NotFoundError("dining table", item.diningTableId);
    }
  }

  /** Add `delta` to the guests (it can't go below zero). */
  adjustGuests(id: number, delta: number): CustomerOrder {
    return this.update(id, { guests: this.get(id).guests + delta });
  }

  adjustTotal(id: number, delta: number): CustomerOrder {
    return this.update(id, { total: Math.round((this.get(id).total + delta) * 100) / 100 });
  }

  setStatus(id: number, value: CustomerOrderStatus): CustomerOrder {
    return this.update(id, { status: value });
  }

  /** Totals and breakdowns over every customer order. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalGuests: this.repo.totalGuests(),
      averageGuests: this.repo.averageGuests(),
      totalTotal: this.repo.totalTotal(),
      averageTotal: this.repo.averageTotal(),
      byStatus: this.repo.countByStatus(),
    };
  }
}

/** Create, change and remove order lines. */
export class OrderLineService {
  constructor(private readonly store: Store) {}

  private get repo(): OrderLineStore {
    return this.store.orderLines;
  }

  /** Validate and store a new order line. */
  create(data: Record<string, unknown>): OrderLine {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseOrderLine(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): OrderLine {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("order line", id);
    }
    return item;
  }

  list(): OrderLine[] {
    return this.repo.list();
  }

  /** Change some fields of a order line. */
  update(id: number, changes: Record<string, unknown>): OrderLine {
    const updated = patchOrderLine(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a order line nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: OrderLine): void {
    if (!this.store.customerOrders.get(item.customerOrderId)) {
      throw new NotFoundError("customer order", item.customerOrderId);
    }
    if (!this.store.menuItems.get(item.menuItemId)) {
      throw new NotFoundError("menu item", item.menuItemId);
    }
  }

  /** Add `delta` to the quantity (it can't go below zero). */
  adjustQuantity(id: number, delta: number): OrderLine {
    return this.update(id, { quantity: this.get(id).quantity + delta });
  }

  adjustUnitPrice(id: number, delta: number): OrderLine {
    return this.update(id, { unitPrice: Math.round((this.get(id).unitPrice + delta) * 100) / 100 });
  }

  /** Totals and breakdowns over every order line. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalQuantity: this.repo.totalQuantity(),
      averageQuantity: this.repo.averageQuantity(),
      totalUnitPrice: this.repo.totalUnitPrice(),
      averageUnitPrice: this.repo.averageUnitPrice(),
    };
  }
}

/** Create, change and remove bookings. */
export class BookingService {
  constructor(private readonly store: Store) {}

  private get repo(): BookingStore {
    return this.store.bookings;
  }

  /** Validate and store a new booking. */
  create(data: Record<string, unknown>): Booking {
    if ("id" in data) {
      throw new ValidationError("id", "is assigned automatically");
    }
    const item = parseBooking(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }

  get(id: number): Booking {
    const item = this.repo.get(id);
    if (!item) {
      throw new NotFoundError("booking", id);
    }
    return item;
  }

  list(): Booking[] {
    return this.repo.list();
  }

  /** Change some fields of a booking. */
  update(id: number, changes: Record<string, unknown>): Booking {
    const updated = patchBooking(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }

  /** Remove a booking nothing points at any more. */
  delete(id: number): void {
    this.get(id);
    this.repo.remove(id);
  }

  private checkLinks(item: Booking): void {
    if (!this.store.diningTables.get(item.diningTableId)) {
      throw new NotFoundError("dining table", item.diningTableId);
    }
  }

  /** Add `delta` to the party size (it can't go below zero). */
  adjustPartySize(id: number, delta: number): Booking {
    return this.update(id, { partySize: this.get(id).partySize + delta });
  }

  toggleConfirmed(id: number): Booking {
    return this.update(id, { confirmed: !this.get(id).confirmed });
  }

  /** Totals and breakdowns over every booking. */
  stats(): Record<string, unknown> {
    return {
      count: this.repo.count(),
      totalPartySize: this.repo.totalPartySize(),
      averagePartySize: this.repo.averagePartySize(),
      confirmed: this.repo.whereConfirmed(true).length,
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
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
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
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
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
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
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
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
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
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
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
    if (!this.store.menuCategories.get(item.menuCategoryId)) {
      throw new NotFoundError("menu category", item.menuCategoryId);
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
  readonly menuCategories = new MenuCategoryService(this.store);
  readonly menuItems = new MenuItemService(this.store);
  readonly diningTables = new DiningTableService(this.store);
  readonly customerOrders = new CustomerOrderService(this.store);
  readonly orderLines = new OrderLineService(this.store);
  readonly bookings = new BookingService(this.store);
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
      this.menuCategories.create(sampleMenuCategory(i));
      this.menuItems.create(sampleMenuItem(i));
      this.diningTables.create(sampleDiningTable(i));
      this.customerOrders.create(sampleCustomerOrder(i));
      this.orderLines.create(sampleOrderLine(i));
      this.bookings.create(sampleBooking(i));
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
      menuCategories: this.menuCategories.stats(),
      menuItems: this.menuItems.stats(),
      diningTables: this.diningTables.stats(),
      customerOrders: this.customerOrders.stats(),
      orderLines: this.orderLines.stats(),
      bookings: this.bookings.stats(),
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

/** Valid data for a new menu category (links point at seeded records). */
export function sampleMenuCategory(i: number): Record<string, unknown> {
  return {
    name: `Menu category name ${i}`,
    position: i + 1,
    visible: i % 2 === 1,
  };
}

/** Valid data for a new menu item (links point at seeded records). */
export function sampleMenuItem(i: number): Record<string, unknown> {
  return {
    menuCategoryId: ((i - 1) % 3) + 1,
    name: `Menu item name ${i}`,
    price: Math.round((10 * i + 0.99) * 100) / 100,
    calories: i + 1,
    spicy: i % 2 === 1,
    vegetarian: i % 2 === 1,
    prepMinutes: i + 1,
  };
}

/** Valid data for a new dining table (links point at seeded records). */
export function sampleDiningTable(i: number): Record<string, unknown> {
  return {
    label: `Dining table label ${i}`,
    seats: i + 1,
    area: DINING_TABLE_AREA_VALUES[i % 4],
    active: i % 2 === 1,
  };
}

/** Valid data for a new customer order (links point at seeded records). */
export function sampleCustomerOrder(i: number): Record<string, unknown> {
  return {
    diningTableId: ((i - 1) % 3) + 1,
    opened: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    guests: i + 1,
    total: Math.round((10 * i + 0.99) * 100) / 100,
    status: CUSTOMER_ORDER_STATUS_VALUES[i % 4],
    server: `Customer order server ${i}`,
  };
}

/** Valid data for a new order line (links point at seeded records). */
export function sampleOrderLine(i: number): Record<string, unknown> {
  return {
    customerOrderId: ((i - 1) % 3) + 1,
    menuItemId: ((i - 1) % 3) + 1,
    quantity: i + 1,
    unitPrice: Math.round((10 * i + 0.99) * 100) / 100,
    note: `Notes about order line ${i}.`,
  };
}

/** Valid data for a new booking (links point at seeded records). */
export function sampleBooking(i: number): Record<string, unknown> {
  return {
    diningTableId: ((i - 1) % 3) + 1,
    name: `Booking name ${i}`,
    phone: `Booking phone ${i}`,
    day: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    partySize: i + 1,
    confirmed: i % 2 === 1,
  };
}

/** Valid data for a new document (links point at seeded records). */
export function sampleDocument(i: number): Record<string, unknown> {
  return {
    menuCategoryId: ((i - 1) % 3) + 1,
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
    menuCategoryId: ((i - 1) % 3) + 1,
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
    menuCategoryId: ((i - 1) % 3) + 1,
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
    menuCategoryId: ((i - 1) % 3) + 1,
    subject: `Note subject ${i}`,
    body: `Notes about note ${i}.`,
    pinned: i % 2 === 1,
    written: `2026-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
  };
}

/** Valid data for a new review (links point at seeded records). */
export function sampleReview(i: number): Record<string, unknown> {
  return {
    menuCategoryId: ((i - 1) % 3) + 1,
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
    menuCategoryId: ((i - 1) % 3) + 1,
    name: `Contact person name ${i}`,
    email: `contact_person${i}@example.com`,
    phone: `Contact person phone ${i}`,
    role: `Contact person role ${i}`,
    primary: i % 2 === 1,
  };
}
