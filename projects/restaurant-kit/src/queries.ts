/**
 * Query layer for the Restaurant Orders kit: filters, search, sorting and paging driven by
 * plain string parameters (as they arrive from a URL or a form), plus field descriptions.
 */

import {
  AUDIT_ENTRY_ACTION_VALUES,
  Address,
  AuditEntry,
  Booking,
  CUSTOMER_ORDER_STATUS_VALUES,
  ContactPerson,
  CustomerOrder,
  DINING_TABLE_AREA_VALUES,
  DiningTable,
  Document,
  MenuCategory,
  MenuItem,
  NOTIFICATION_CHANNEL_VALUES,
  Note,
  Notification,
  OrderLine,
  REMINDER_PRIORITY_VALUES,
  Reminder,
  Review,
  Setting,
  ValidationError,
  checkChoice,
  checkDate,
  compareAddressByCity,
  compareAddressByCountry,
  compareAddressByMenuCategoryId,
  compareAddressByPostcode,
  compareAddressByStreet,
  compareAuditEntryByAction,
  compareAuditEntryByActor,
  compareAuditEntryByAt,
  compareAuditEntryByDetails,
  compareBookingByDay,
  compareBookingByDiningTableId,
  compareBookingByName,
  compareBookingByPartySize,
  compareBookingByPhone,
  compareContactPersonByEmail,
  compareContactPersonByMenuCategoryId,
  compareContactPersonByName,
  compareContactPersonByPhone,
  compareContactPersonByRole,
  compareCustomerOrderByDiningTableId,
  compareCustomerOrderByGuests,
  compareCustomerOrderByOpened,
  compareCustomerOrderByServer,
  compareCustomerOrderByStatus,
  compareCustomerOrderByTotal,
  compareDiningTableByArea,
  compareDiningTableByLabel,
  compareDiningTableBySeats,
  compareDocumentByIssued,
  compareDocumentByMenuCategoryId,
  compareDocumentByPages,
  compareDocumentByTitle,
  compareDocumentByVersion,
  compareMenuCategoryByName,
  compareMenuCategoryByPosition,
  compareMenuItemByCalories,
  compareMenuItemByMenuCategoryId,
  compareMenuItemByName,
  compareMenuItemByPrepMinutes,
  compareMenuItemByPrice,
  compareNoteByBody,
  compareNoteByMenuCategoryId,
  compareNoteBySubject,
  compareNoteByWritten,
  compareNotificationByChannel,
  compareNotificationByRecipient,
  compareNotificationBySent,
  compareNotificationByTitle,
  compareOrderLineByCustomerOrderId,
  compareOrderLineByMenuItemId,
  compareOrderLineByNote,
  compareOrderLineByQuantity,
  compareOrderLineByUnitPrice,
  compareReminderByMenuCategoryId,
  compareReminderByPriority,
  compareReminderByRemindOn,
  compareReminderByTitle,
  compareReviewByAuthor,
  compareReviewByComment,
  compareReviewByMenuCategoryId,
  compareReviewByPosted,
  compareReviewByStars,
  compareSettingByChanged,
  compareSettingByKeyName,
  compareSettingByValue,
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

const MENU_CATEGORY_COMPARERS: Record<string, (a: MenuCategory, b: MenuCategory) => number> = {
  id: (a, b) => a.id - b.id,
  name: compareMenuCategoryByName,
  position: compareMenuCategoryByPosition,
};

/** Menu categories matching the query parameters. */
export function queryMenuCategories(store: Store, query: Query): MenuCategory[] {
  let items = store.menuCategories.list();
  if (query.q !== undefined) {
    const hits = new Set(store.menuCategories.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.name !== undefined) {
    const wanted = query.name;
    items = items.filter((item) => item.name === wanted);
  }
  if (query.minPosition !== undefined) {
    const limit = numberParam(query, "minPosition");
    items = items.filter((item) => item.position >= limit);
  }
  if (query.maxPosition !== undefined) {
    const limit = numberParam(query, "maxPosition");
    items = items.filter((item) => item.position <= limit);
  }
  if (query.visible !== undefined) {
    const wanted = flagParam(query, "visible");
    items = items.filter((item) => item.visible === wanted);
  }
  return paginate(sortWith(items, query.sort, MENU_CATEGORY_COMPARERS), query);
}

/** What each menu category field holds and the rule it must follow. */
export function describeMenuCategory(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "position", kind: "int", rule: RULES.int },
    { field: "visible", kind: "bool", rule: RULES.bool },
  ];
}

const MENU_ITEM_COMPARERS: Record<string, (a: MenuItem, b: MenuItem) => number> = {
  id: (a, b) => a.id - b.id,
  menuCategoryId: compareMenuItemByMenuCategoryId,
  name: compareMenuItemByName,
  price: compareMenuItemByPrice,
  calories: compareMenuItemByCalories,
  prepMinutes: compareMenuItemByPrepMinutes,
};

/** Menu items matching the query parameters. */
export function queryMenuItems(store: Store, query: Query): MenuItem[] {
  let items = store.menuItems.list();
  if (query.q !== undefined) {
    const hits = new Set(store.menuItems.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
  if (query.minCalories !== undefined) {
    const limit = numberParam(query, "minCalories");
    items = items.filter((item) => item.calories >= limit);
  }
  if (query.maxCalories !== undefined) {
    const limit = numberParam(query, "maxCalories");
    items = items.filter((item) => item.calories <= limit);
  }
  if (query.spicy !== undefined) {
    const wanted = flagParam(query, "spicy");
    items = items.filter((item) => item.spicy === wanted);
  }
  if (query.vegetarian !== undefined) {
    const wanted = flagParam(query, "vegetarian");
    items = items.filter((item) => item.vegetarian === wanted);
  }
  if (query.minPrepMinutes !== undefined) {
    const limit = numberParam(query, "minPrepMinutes");
    items = items.filter((item) => item.prepMinutes >= limit);
  }
  if (query.maxPrepMinutes !== undefined) {
    const limit = numberParam(query, "maxPrepMinutes");
    items = items.filter((item) => item.prepMinutes <= limit);
  }
  return paginate(sortWith(items, query.sort, MENU_ITEM_COMPARERS), query);
}

/** What each menu item field holds and the rule it must follow. */
export function describeMenuItem(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "price", kind: "money", rule: RULES.money },
    { field: "calories", kind: "int", rule: RULES.int },
    { field: "spicy", kind: "bool", rule: RULES.bool },
    { field: "vegetarian", kind: "bool", rule: RULES.bool },
    { field: "prepMinutes", kind: "int", rule: RULES.int },
  ];
}

const DINING_TABLE_COMPARERS: Record<string, (a: DiningTable, b: DiningTable) => number> = {
  id: (a, b) => a.id - b.id,
  label: compareDiningTableByLabel,
  seats: compareDiningTableBySeats,
  area: compareDiningTableByArea,
};

/** Dining tables matching the query parameters. */
export function queryDiningTables(store: Store, query: Query): DiningTable[] {
  let items = store.diningTables.list();
  if (query.q !== undefined) {
    const hits = new Set(store.diningTables.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.label !== undefined) {
    const wanted = query.label;
    items = items.filter((item) => item.label === wanted);
  }
  if (query.minSeats !== undefined) {
    const limit = numberParam(query, "minSeats");
    items = items.filter((item) => item.seats >= limit);
  }
  if (query.maxSeats !== undefined) {
    const limit = numberParam(query, "maxSeats");
    items = items.filter((item) => item.seats <= limit);
  }
  if (query.area !== undefined) {
    const wanted = checkChoice("area", query.area, DINING_TABLE_AREA_VALUES);
    items = items.filter((item) => item.area === wanted);
  }
  if (query.active !== undefined) {
    const wanted = flagParam(query, "active");
    items = items.filter((item) => item.active === wanted);
  }
  return paginate(sortWith(items, query.sort, DINING_TABLE_COMPARERS), query);
}

/** What each dining table field holds and the rule it must follow. */
export function describeDiningTable(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "label", kind: "str", rule: RULES.str },
    { field: "seats", kind: "int", rule: RULES.int },
    { field: "area", kind: "enum", rule: RULES.enum },
    { field: "active", kind: "bool", rule: RULES.bool },
  ];
}

const CUSTOMER_ORDER_COMPARERS: Record<string, (a: CustomerOrder, b: CustomerOrder) => number> = {
  id: (a, b) => a.id - b.id,
  diningTableId: compareCustomerOrderByDiningTableId,
  opened: compareCustomerOrderByOpened,
  guests: compareCustomerOrderByGuests,
  total: compareCustomerOrderByTotal,
  status: compareCustomerOrderByStatus,
  server: compareCustomerOrderByServer,
};

/** Customer orders matching the query parameters. */
export function queryCustomerOrders(store: Store, query: Query): CustomerOrder[] {
  let items = store.customerOrders.list();
  if (query.q !== undefined) {
    const hits = new Set(store.customerOrders.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.diningTableId !== undefined) {
    const wanted = numberParam(query, "diningTableId");
    items = items.filter((item) => item.diningTableId === wanted);
  }
  if (query.openedFrom !== undefined) {
    const day = checkDate("openedFrom", query.openedFrom);
    items = items.filter((item) => item.opened >= day);
  }
  if (query.openedTo !== undefined) {
    const day = checkDate("openedTo", query.openedTo);
    items = items.filter((item) => item.opened <= day);
  }
  if (query.minGuests !== undefined) {
    const limit = numberParam(query, "minGuests");
    items = items.filter((item) => item.guests >= limit);
  }
  if (query.maxGuests !== undefined) {
    const limit = numberParam(query, "maxGuests");
    items = items.filter((item) => item.guests <= limit);
  }
  if (query.minTotal !== undefined) {
    const limit = numberParam(query, "minTotal");
    items = items.filter((item) => item.total >= limit);
  }
  if (query.maxTotal !== undefined) {
    const limit = numberParam(query, "maxTotal");
    items = items.filter((item) => item.total <= limit);
  }
  if (query.status !== undefined) {
    const wanted = checkChoice("status", query.status, CUSTOMER_ORDER_STATUS_VALUES);
    items = items.filter((item) => item.status === wanted);
  }
  if (query.server !== undefined) {
    const wanted = query.server;
    items = items.filter((item) => item.server === wanted);
  }
  return paginate(sortWith(items, query.sort, CUSTOMER_ORDER_COMPARERS), query);
}

/** What each customer order field holds and the rule it must follow. */
export function describeCustomerOrder(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "diningTableId", kind: "ref", rule: RULES.ref },
    { field: "opened", kind: "date", rule: RULES.date },
    { field: "guests", kind: "int", rule: RULES.int },
    { field: "total", kind: "money", rule: RULES.money },
    { field: "status", kind: "enum", rule: RULES.enum },
    { field: "server", kind: "str", rule: RULES.str },
  ];
}

const ORDER_LINE_COMPARERS: Record<string, (a: OrderLine, b: OrderLine) => number> = {
  id: (a, b) => a.id - b.id,
  customerOrderId: compareOrderLineByCustomerOrderId,
  menuItemId: compareOrderLineByMenuItemId,
  quantity: compareOrderLineByQuantity,
  unitPrice: compareOrderLineByUnitPrice,
  note: compareOrderLineByNote,
};

/** Order lines matching the query parameters. */
export function queryOrderLines(store: Store, query: Query): OrderLine[] {
  let items = store.orderLines.list();
  if (query.q !== undefined) {
    const hits = new Set(store.orderLines.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.customerOrderId !== undefined) {
    const wanted = numberParam(query, "customerOrderId");
    items = items.filter((item) => item.customerOrderId === wanted);
  }
  if (query.menuItemId !== undefined) {
    const wanted = numberParam(query, "menuItemId");
    items = items.filter((item) => item.menuItemId === wanted);
  }
  if (query.minQuantity !== undefined) {
    const limit = numberParam(query, "minQuantity");
    items = items.filter((item) => item.quantity >= limit);
  }
  if (query.maxQuantity !== undefined) {
    const limit = numberParam(query, "maxQuantity");
    items = items.filter((item) => item.quantity <= limit);
  }
  if (query.minUnitPrice !== undefined) {
    const limit = numberParam(query, "minUnitPrice");
    items = items.filter((item) => item.unitPrice >= limit);
  }
  if (query.maxUnitPrice !== undefined) {
    const limit = numberParam(query, "maxUnitPrice");
    items = items.filter((item) => item.unitPrice <= limit);
  }
  if (query.note !== undefined) {
    const wanted = query.note;
    items = items.filter((item) => item.note === wanted);
  }
  return paginate(sortWith(items, query.sort, ORDER_LINE_COMPARERS), query);
}

/** What each order line field holds and the rule it must follow. */
export function describeOrderLine(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "customerOrderId", kind: "ref", rule: RULES.ref },
    { field: "menuItemId", kind: "ref", rule: RULES.ref },
    { field: "quantity", kind: "int", rule: RULES.int },
    { field: "unitPrice", kind: "money", rule: RULES.money },
    { field: "note", kind: "text", rule: RULES.text },
  ];
}

const BOOKING_COMPARERS: Record<string, (a: Booking, b: Booking) => number> = {
  id: (a, b) => a.id - b.id,
  diningTableId: compareBookingByDiningTableId,
  name: compareBookingByName,
  phone: compareBookingByPhone,
  day: compareBookingByDay,
  partySize: compareBookingByPartySize,
};

/** Bookings matching the query parameters. */
export function queryBookings(store: Store, query: Query): Booking[] {
  let items = store.bookings.list();
  if (query.q !== undefined) {
    const hits = new Set(store.bookings.search(query.q).map((item) => item.id));
    items = items.filter((item) => hits.has(item.id));
  }
  if (query.diningTableId !== undefined) {
    const wanted = numberParam(query, "diningTableId");
    items = items.filter((item) => item.diningTableId === wanted);
  }
  if (query.name !== undefined) {
    const wanted = query.name;
    items = items.filter((item) => item.name === wanted);
  }
  if (query.phone !== undefined) {
    const wanted = query.phone;
    items = items.filter((item) => item.phone === wanted);
  }
  if (query.dayFrom !== undefined) {
    const day = checkDate("dayFrom", query.dayFrom);
    items = items.filter((item) => item.day >= day);
  }
  if (query.dayTo !== undefined) {
    const day = checkDate("dayTo", query.dayTo);
    items = items.filter((item) => item.day <= day);
  }
  if (query.minPartySize !== undefined) {
    const limit = numberParam(query, "minPartySize");
    items = items.filter((item) => item.partySize >= limit);
  }
  if (query.maxPartySize !== undefined) {
    const limit = numberParam(query, "maxPartySize");
    items = items.filter((item) => item.partySize <= limit);
  }
  if (query.confirmed !== undefined) {
    const wanted = flagParam(query, "confirmed");
    items = items.filter((item) => item.confirmed === wanted);
  }
  return paginate(sortWith(items, query.sort, BOOKING_COMPARERS), query);
}

/** What each booking field holds and the rule it must follow. */
export function describeBooking(): FieldInfo[] {
  return [
    { field: "id", kind: "int", rule: "assigned automatically" },
    { field: "diningTableId", kind: "ref", rule: RULES.ref },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "phone", kind: "str", rule: RULES.str },
    { field: "day", kind: "date", rule: RULES.date },
    { field: "partySize", kind: "int", rule: RULES.int },
    { field: "confirmed", kind: "bool", rule: RULES.bool },
  ];
}

const DOCUMENT_COMPARERS: Record<string, (a: Document, b: Document) => number> = {
  id: (a, b) => a.id - b.id,
  menuCategoryId: compareDocumentByMenuCategoryId,
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
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
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
  menuCategoryId: compareAddressByMenuCategoryId,
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
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
    { field: "street", kind: "str", rule: RULES.str },
    { field: "city", kind: "str", rule: RULES.str },
    { field: "postcode", kind: "str", rule: RULES.str },
    { field: "country", kind: "str", rule: RULES.str },
    { field: "billing", kind: "bool", rule: RULES.bool },
  ];
}

const REMINDER_COMPARERS: Record<string, (a: Reminder, b: Reminder) => number> = {
  id: (a, b) => a.id - b.id,
  menuCategoryId: compareReminderByMenuCategoryId,
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
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
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
  menuCategoryId: compareNoteByMenuCategoryId,
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
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
    { field: "subject", kind: "str", rule: RULES.str },
    { field: "body", kind: "text", rule: RULES.text },
    { field: "pinned", kind: "bool", rule: RULES.bool },
    { field: "written", kind: "date", rule: RULES.date },
  ];
}

const REVIEW_COMPARERS: Record<string, (a: Review, b: Review) => number> = {
  id: (a, b) => a.id - b.id,
  menuCategoryId: compareReviewByMenuCategoryId,
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
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
    { field: "author", kind: "str", rule: RULES.str },
    { field: "stars", kind: "int", rule: RULES.int },
    { field: "comment", kind: "text", rule: RULES.text },
    { field: "verified", kind: "bool", rule: RULES.bool },
    { field: "posted", kind: "date", rule: RULES.date },
  ];
}

const CONTACT_PERSON_COMPARERS: Record<string, (a: ContactPerson, b: ContactPerson) => number> = {
  id: (a, b) => a.id - b.id,
  menuCategoryId: compareContactPersonByMenuCategoryId,
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
  if (query.menuCategoryId !== undefined) {
    const wanted = numberParam(query, "menuCategoryId");
    items = items.filter((item) => item.menuCategoryId === wanted);
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
    { field: "menuCategoryId", kind: "ref", rule: RULES.ref },
    { field: "name", kind: "str", rule: RULES.str },
    { field: "email", kind: "email", rule: RULES.email },
    { field: "phone", kind: "str", rule: RULES.str },
    { field: "role", kind: "str", rule: RULES.str },
    { field: "primary", kind: "bool", rule: RULES.bool },
  ];
}
