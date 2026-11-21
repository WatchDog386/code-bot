/**
 * Domain models for the Restaurant Orders kit: record types, the allowed values of every
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

/** Allowed values of DiningTable.area. */
export const DINING_TABLE_AREA_VALUES = ["inside", "terrace", "bar", "private"] as const;
export type DiningTableArea = (typeof DINING_TABLE_AREA_VALUES)[number];

export function isDiningTableArea(value: unknown): value is DiningTableArea {
  return typeof value === "string" && (DINING_TABLE_AREA_VALUES as readonly string[]).includes(value);
}

export function labelDiningTableArea(value: DiningTableArea): string {
  const text = value.replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Allowed values of CustomerOrder.status. */
export const CUSTOMER_ORDER_STATUS_VALUES = ["open", "served", "paid", "cancelled"] as const;
export type CustomerOrderStatus = (typeof CUSTOMER_ORDER_STATUS_VALUES)[number];

export function isCustomerOrderStatus(value: unknown): value is CustomerOrderStatus {
  return typeof value === "string" && (CUSTOMER_ORDER_STATUS_VALUES as readonly string[]).includes(value);
}

export function labelCustomerOrderStatus(value: CustomerOrderStatus): string {
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

// ---------------------------------------------------------------------------- MenuCategory

/** A menu category record. */
export interface MenuCategory {
  id: number;
  name: string;
  position: number;
  visible: boolean;
}

export type MenuCategoryInput = Omit<MenuCategory, "id">;

export const MENU_CATEGORY_FIELDS = ["id", "name", "position", "visible"] as const;

/** Check MenuCategory.name (str). */
export function checkMenuCategoryName(value: unknown): string {
  return checkText("name", value);
}

/** Check MenuCategory.position (int). */
export function checkMenuCategoryPosition(value: unknown): number {
  return checkInt("position", value);
}

/** Check MenuCategory.visible (bool). */
export function checkMenuCategoryVisible(value: unknown): boolean {
  return checkFlag("visible", value);
}

/** A checked MenuCategory from untrusted data (every field is required). */
export function parseMenuCategory(data: Record<string, unknown>, id = 0): MenuCategory {
  rejectUnknown(data, MENU_CATEGORY_FIELDS);
  return {
    id,
    name: checkMenuCategoryName(data.name),
    position: checkMenuCategoryPosition(data.position),
    visible: checkMenuCategoryVisible(data.visible),
  };
}

/** The fields of a MenuCategory without its id. */
export function menuCategoryInput(item: MenuCategory): MenuCategoryInput {
  return {
    name: item.name,
    position: item.position,
    visible: item.visible,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchMenuCategory(item: MenuCategory, changes: Record<string, unknown>): MenuCategory {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, MENU_CATEGORY_FIELDS);
  return parseMenuCategory({ ...menuCategoryInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeMenuCategory(item: MenuCategory): string {
  return `MenuCategory #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as MENU_CATEGORY_FIELDS). */
export function menuCategoryRow(item: MenuCategory): Array<string | number | boolean> {
  return [item.id, item.name, item.position, item.visible];
}

export function compareMenuCategoryByName(a: MenuCategory, b: MenuCategory): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareMenuCategoryByPosition(a: MenuCategory, b: MenuCategory): number {
  return a.position - b.position;
}

// ---------------------------------------------------------------------------- MenuItem

/** A menu item record. */
export interface MenuItem {
  id: number;
  menuCategoryId: number;
  name: string;
  price: number;
  calories: number;
  spicy: boolean;
  vegetarian: boolean;
  prepMinutes: number;
}

export type MenuItemInput = Omit<MenuItem, "id">;

export const MENU_ITEM_FIELDS = ["id", "menuCategoryId", "name", "price", "calories", "spicy", "vegetarian", "prepMinutes"] as const;

/** Check MenuItem.menuCategoryId (ref). */
export function checkMenuItemMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
}

/** Check MenuItem.name (str). */
export function checkMenuItemName(value: unknown): string {
  return checkText("name", value);
}

/** Check MenuItem.price (money). */
export function checkMenuItemPrice(value: unknown): number {
  return checkMoney("price", value);
}

/** Check MenuItem.calories (int). */
export function checkMenuItemCalories(value: unknown): number {
  return checkInt("calories", value);
}

/** Check MenuItem.spicy (bool). */
export function checkMenuItemSpicy(value: unknown): boolean {
  return checkFlag("spicy", value);
}

/** Check MenuItem.vegetarian (bool). */
export function checkMenuItemVegetarian(value: unknown): boolean {
  return checkFlag("vegetarian", value);
}

/** Check MenuItem.prepMinutes (int). */
export function checkMenuItemPrepMinutes(value: unknown): number {
  return checkInt("prepMinutes", value);
}

/** A checked MenuItem from untrusted data (every field is required). */
export function parseMenuItem(data: Record<string, unknown>, id = 0): MenuItem {
  rejectUnknown(data, MENU_ITEM_FIELDS);
  return {
    id,
    menuCategoryId: checkMenuItemMenuCategoryId(data.menuCategoryId),
    name: checkMenuItemName(data.name),
    price: checkMenuItemPrice(data.price),
    calories: checkMenuItemCalories(data.calories),
    spicy: checkMenuItemSpicy(data.spicy),
    vegetarian: checkMenuItemVegetarian(data.vegetarian),
    prepMinutes: checkMenuItemPrepMinutes(data.prepMinutes),
  };
}

/** The fields of a MenuItem without its id. */
export function menuItemInput(item: MenuItem): MenuItemInput {
  return {
    menuCategoryId: item.menuCategoryId,
    name: item.name,
    price: item.price,
    calories: item.calories,
    spicy: item.spicy,
    vegetarian: item.vegetarian,
    prepMinutes: item.prepMinutes,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchMenuItem(item: MenuItem, changes: Record<string, unknown>): MenuItem {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, MENU_ITEM_FIELDS);
  return parseMenuItem({ ...menuItemInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeMenuItem(item: MenuItem): string {
  return `MenuItem #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as MENU_ITEM_FIELDS). */
export function menuItemRow(item: MenuItem): Array<string | number | boolean> {
  return [item.id, item.menuCategoryId, item.name, item.price, item.calories, item.spicy, item.vegetarian, item.prepMinutes];
}

export function compareMenuItemByMenuCategoryId(a: MenuItem, b: MenuItem): number {
  return a.menuCategoryId - b.menuCategoryId;
}

export function compareMenuItemByName(a: MenuItem, b: MenuItem): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareMenuItemByPrice(a: MenuItem, b: MenuItem): number {
  return a.price - b.price;
}

export function compareMenuItemByCalories(a: MenuItem, b: MenuItem): number {
  return a.calories - b.calories;
}

export function compareMenuItemByPrepMinutes(a: MenuItem, b: MenuItem): number {
  return a.prepMinutes - b.prepMinutes;
}

// ---------------------------------------------------------------------------- DiningTable

/** A dining table record. */
export interface DiningTable {
  id: number;
  label: string;
  seats: number;
  area: DiningTableArea;
  active: boolean;
}

export type DiningTableInput = Omit<DiningTable, "id">;

export const DINING_TABLE_FIELDS = ["id", "label", "seats", "area", "active"] as const;

/** Check DiningTable.label (str). */
export function checkDiningTableLabel(value: unknown): string {
  return checkText("label", value);
}

/** Check DiningTable.seats (int). */
export function checkDiningTableSeats(value: unknown): number {
  return checkInt("seats", value);
}

/** Check DiningTable.area (enum). */
export function checkDiningTableArea(value: unknown): DiningTableArea {
  return checkChoice("area", value, DINING_TABLE_AREA_VALUES);
}

/** Check DiningTable.active (bool). */
export function checkDiningTableActive(value: unknown): boolean {
  return checkFlag("active", value);
}

/** A checked DiningTable from untrusted data (every field is required). */
export function parseDiningTable(data: Record<string, unknown>, id = 0): DiningTable {
  rejectUnknown(data, DINING_TABLE_FIELDS);
  return {
    id,
    label: checkDiningTableLabel(data.label),
    seats: checkDiningTableSeats(data.seats),
    area: checkDiningTableArea(data.area),
    active: checkDiningTableActive(data.active),
  };
}

/** The fields of a DiningTable without its id. */
export function diningTableInput(item: DiningTable): DiningTableInput {
  return {
    label: item.label,
    seats: item.seats,
    area: item.area,
    active: item.active,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchDiningTable(item: DiningTable, changes: Record<string, unknown>): DiningTable {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, DINING_TABLE_FIELDS);
  return parseDiningTable({ ...diningTableInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeDiningTable(item: DiningTable): string {
  return `DiningTable #${item.id}: ${item.label}`;
}

/** The record as one CSV-ready row (same order as DINING_TABLE_FIELDS). */
export function diningTableRow(item: DiningTable): Array<string | number | boolean> {
  return [item.id, item.label, item.seats, item.area, item.active];
}

export function compareDiningTableByLabel(a: DiningTable, b: DiningTable): number {
  return a.label < b.label ? -1 : a.label > b.label ? 1 : 0;
}

export function compareDiningTableBySeats(a: DiningTable, b: DiningTable): number {
  return a.seats - b.seats;
}

export function compareDiningTableByArea(a: DiningTable, b: DiningTable): number {
  return a.area < b.area ? -1 : a.area > b.area ? 1 : 0;
}

// ---------------------------------------------------------------------------- CustomerOrder

/** A customer order record. */
export interface CustomerOrder {
  id: number;
  diningTableId: number;
  opened: string;
  guests: number;
  total: number;
  status: CustomerOrderStatus;
  server: string;
}

export type CustomerOrderInput = Omit<CustomerOrder, "id">;

export const CUSTOMER_ORDER_FIELDS = ["id", "diningTableId", "opened", "guests", "total", "status", "server"] as const;

/** Check CustomerOrder.diningTableId (ref). */
export function checkCustomerOrderDiningTableId(value: unknown): number {
  return checkRef("diningTableId", value);
}

/** Check CustomerOrder.opened (date). */
export function checkCustomerOrderOpened(value: unknown): string {
  return checkDate("opened", value);
}

/** Check CustomerOrder.guests (int). */
export function checkCustomerOrderGuests(value: unknown): number {
  return checkInt("guests", value);
}

/** Check CustomerOrder.total (money). */
export function checkCustomerOrderTotal(value: unknown): number {
  return checkMoney("total", value);
}

/** Check CustomerOrder.status (enum). */
export function checkCustomerOrderStatus(value: unknown): CustomerOrderStatus {
  return checkChoice("status", value, CUSTOMER_ORDER_STATUS_VALUES);
}

/** Check CustomerOrder.server (str). */
export function checkCustomerOrderServer(value: unknown): string {
  return checkText("server", value);
}

/** A checked CustomerOrder from untrusted data (every field is required). */
export function parseCustomerOrder(data: Record<string, unknown>, id = 0): CustomerOrder {
  rejectUnknown(data, CUSTOMER_ORDER_FIELDS);
  return {
    id,
    diningTableId: checkCustomerOrderDiningTableId(data.diningTableId),
    opened: checkCustomerOrderOpened(data.opened),
    guests: checkCustomerOrderGuests(data.guests),
    total: checkCustomerOrderTotal(data.total),
    status: checkCustomerOrderStatus(data.status),
    server: checkCustomerOrderServer(data.server),
  };
}

/** The fields of a CustomerOrder without its id. */
export function customerOrderInput(item: CustomerOrder): CustomerOrderInput {
  return {
    diningTableId: item.diningTableId,
    opened: item.opened,
    guests: item.guests,
    total: item.total,
    status: item.status,
    server: item.server,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchCustomerOrder(item: CustomerOrder, changes: Record<string, unknown>): CustomerOrder {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, CUSTOMER_ORDER_FIELDS);
  return parseCustomerOrder({ ...customerOrderInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeCustomerOrder(item: CustomerOrder): string {
  return `CustomerOrder #${item.id}: ${item.server}`;
}

/** The record as one CSV-ready row (same order as CUSTOMER_ORDER_FIELDS). */
export function customerOrderRow(item: CustomerOrder): Array<string | number | boolean> {
  return [item.id, item.diningTableId, item.opened, item.guests, item.total, item.status, item.server];
}

export function compareCustomerOrderByDiningTableId(a: CustomerOrder, b: CustomerOrder): number {
  return a.diningTableId - b.diningTableId;
}

export function compareCustomerOrderByOpened(a: CustomerOrder, b: CustomerOrder): number {
  return a.opened < b.opened ? -1 : a.opened > b.opened ? 1 : 0;
}

export function compareCustomerOrderByGuests(a: CustomerOrder, b: CustomerOrder): number {
  return a.guests - b.guests;
}

export function compareCustomerOrderByTotal(a: CustomerOrder, b: CustomerOrder): number {
  return a.total - b.total;
}

export function compareCustomerOrderByStatus(a: CustomerOrder, b: CustomerOrder): number {
  return a.status < b.status ? -1 : a.status > b.status ? 1 : 0;
}

export function compareCustomerOrderByServer(a: CustomerOrder, b: CustomerOrder): number {
  return a.server < b.server ? -1 : a.server > b.server ? 1 : 0;
}

// ---------------------------------------------------------------------------- OrderLine

/** A order line record. */
export interface OrderLine {
  id: number;
  customerOrderId: number;
  menuItemId: number;
  quantity: number;
  unitPrice: number;
  note: string;
}

export type OrderLineInput = Omit<OrderLine, "id">;

export const ORDER_LINE_FIELDS = ["id", "customerOrderId", "menuItemId", "quantity", "unitPrice", "note"] as const;

/** Check OrderLine.customerOrderId (ref). */
export function checkOrderLineCustomerOrderId(value: unknown): number {
  return checkRef("customerOrderId", value);
}

/** Check OrderLine.menuItemId (ref). */
export function checkOrderLineMenuItemId(value: unknown): number {
  return checkRef("menuItemId", value);
}

/** Check OrderLine.quantity (int). */
export function checkOrderLineQuantity(value: unknown): number {
  return checkInt("quantity", value);
}

/** Check OrderLine.unitPrice (money). */
export function checkOrderLineUnitPrice(value: unknown): number {
  return checkMoney("unitPrice", value);
}

/** Check OrderLine.note (text). */
export function checkOrderLineNote(value: unknown): string {
  return checkText("note", value, 2000, false);
}

/** A checked OrderLine from untrusted data (every field is required). */
export function parseOrderLine(data: Record<string, unknown>, id = 0): OrderLine {
  rejectUnknown(data, ORDER_LINE_FIELDS);
  return {
    id,
    customerOrderId: checkOrderLineCustomerOrderId(data.customerOrderId),
    menuItemId: checkOrderLineMenuItemId(data.menuItemId),
    quantity: checkOrderLineQuantity(data.quantity),
    unitPrice: checkOrderLineUnitPrice(data.unitPrice),
    note: checkOrderLineNote(data.note),
  };
}

/** The fields of a OrderLine without its id. */
export function orderLineInput(item: OrderLine): OrderLineInput {
  return {
    customerOrderId: item.customerOrderId,
    menuItemId: item.menuItemId,
    quantity: item.quantity,
    unitPrice: item.unitPrice,
    note: item.note,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchOrderLine(item: OrderLine, changes: Record<string, unknown>): OrderLine {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, ORDER_LINE_FIELDS);
  return parseOrderLine({ ...orderLineInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeOrderLine(item: OrderLine): string {
  return `OrderLine #${item.id}`;
}

/** The record as one CSV-ready row (same order as ORDER_LINE_FIELDS). */
export function orderLineRow(item: OrderLine): Array<string | number | boolean> {
  return [item.id, item.customerOrderId, item.menuItemId, item.quantity, item.unitPrice, item.note];
}

export function compareOrderLineByCustomerOrderId(a: OrderLine, b: OrderLine): number {
  return a.customerOrderId - b.customerOrderId;
}

export function compareOrderLineByMenuItemId(a: OrderLine, b: OrderLine): number {
  return a.menuItemId - b.menuItemId;
}

export function compareOrderLineByQuantity(a: OrderLine, b: OrderLine): number {
  return a.quantity - b.quantity;
}

export function compareOrderLineByUnitPrice(a: OrderLine, b: OrderLine): number {
  return a.unitPrice - b.unitPrice;
}

export function compareOrderLineByNote(a: OrderLine, b: OrderLine): number {
  return a.note < b.note ? -1 : a.note > b.note ? 1 : 0;
}

// ---------------------------------------------------------------------------- Booking

/** A booking record. */
export interface Booking {
  id: number;
  diningTableId: number;
  name: string;
  phone: string;
  day: string;
  partySize: number;
  confirmed: boolean;
}

export type BookingInput = Omit<Booking, "id">;

export const BOOKING_FIELDS = ["id", "diningTableId", "name", "phone", "day", "partySize", "confirmed"] as const;

/** Check Booking.diningTableId (ref). */
export function checkBookingDiningTableId(value: unknown): number {
  return checkRef("diningTableId", value);
}

/** Check Booking.name (str). */
export function checkBookingName(value: unknown): string {
  return checkText("name", value);
}

/** Check Booking.phone (str). */
export function checkBookingPhone(value: unknown): string {
  return checkText("phone", value);
}

/** Check Booking.day (date). */
export function checkBookingDay(value: unknown): string {
  return checkDate("day", value);
}

/** Check Booking.partySize (int). */
export function checkBookingPartySize(value: unknown): number {
  return checkInt("partySize", value);
}

/** Check Booking.confirmed (bool). */
export function checkBookingConfirmed(value: unknown): boolean {
  return checkFlag("confirmed", value);
}

/** A checked Booking from untrusted data (every field is required). */
export function parseBooking(data: Record<string, unknown>, id = 0): Booking {
  rejectUnknown(data, BOOKING_FIELDS);
  return {
    id,
    diningTableId: checkBookingDiningTableId(data.diningTableId),
    name: checkBookingName(data.name),
    phone: checkBookingPhone(data.phone),
    day: checkBookingDay(data.day),
    partySize: checkBookingPartySize(data.partySize),
    confirmed: checkBookingConfirmed(data.confirmed),
  };
}

/** The fields of a Booking without its id. */
export function bookingInput(item: Booking): BookingInput {
  return {
    diningTableId: item.diningTableId,
    name: item.name,
    phone: item.phone,
    day: item.day,
    partySize: item.partySize,
    confirmed: item.confirmed,
  };
}

/** A checked copy of `item` with `changes` applied; the id never changes. */
export function patchBooking(item: Booking, changes: Record<string, unknown>): Booking {
  if ("id" in changes) {
    throw new ValidationError("id", "cannot be changed");
  }
  rejectUnknown(changes, BOOKING_FIELDS);
  return parseBooking({ ...bookingInput(item), ...changes }, item.id);
}

/** One line for logs and lists. */
export function summarizeBooking(item: Booking): string {
  return `Booking #${item.id}: ${item.name}`;
}

/** The record as one CSV-ready row (same order as BOOKING_FIELDS). */
export function bookingRow(item: Booking): Array<string | number | boolean> {
  return [item.id, item.diningTableId, item.name, item.phone, item.day, item.partySize, item.confirmed];
}

export function compareBookingByDiningTableId(a: Booking, b: Booking): number {
  return a.diningTableId - b.diningTableId;
}

export function compareBookingByName(a: Booking, b: Booking): number {
  return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
}

export function compareBookingByPhone(a: Booking, b: Booking): number {
  return a.phone < b.phone ? -1 : a.phone > b.phone ? 1 : 0;
}

export function compareBookingByDay(a: Booking, b: Booking): number {
  return a.day < b.day ? -1 : a.day > b.day ? 1 : 0;
}

export function compareBookingByPartySize(a: Booking, b: Booking): number {
  return a.partySize - b.partySize;
}

// ---------------------------------------------------------------------------- Document

/** A document record. */
export interface Document {
  id: number;
  menuCategoryId: number;
  title: string;
  pages: number;
  signed: boolean;
  version: number;
  issued: string;
}

export type DocumentInput = Omit<Document, "id">;

export const DOCUMENT_FIELDS = ["id", "menuCategoryId", "title", "pages", "signed", "version", "issued"] as const;

/** Check Document.menuCategoryId (ref). */
export function checkDocumentMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
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
    menuCategoryId: checkDocumentMenuCategoryId(data.menuCategoryId),
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
    menuCategoryId: item.menuCategoryId,
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
  return [item.id, item.menuCategoryId, item.title, item.pages, item.signed, item.version, item.issued];
}

export function compareDocumentByMenuCategoryId(a: Document, b: Document): number {
  return a.menuCategoryId - b.menuCategoryId;
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
  menuCategoryId: number;
  street: string;
  city: string;
  postcode: string;
  country: string;
  billing: boolean;
}

export type AddressInput = Omit<Address, "id">;

export const ADDRESS_FIELDS = ["id", "menuCategoryId", "street", "city", "postcode", "country", "billing"] as const;

/** Check Address.menuCategoryId (ref). */
export function checkAddressMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
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
    menuCategoryId: checkAddressMenuCategoryId(data.menuCategoryId),
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
    menuCategoryId: item.menuCategoryId,
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
  return [item.id, item.menuCategoryId, item.street, item.city, item.postcode, item.country, item.billing];
}

export function compareAddressByMenuCategoryId(a: Address, b: Address): number {
  return a.menuCategoryId - b.menuCategoryId;
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
  menuCategoryId: number;
  title: string;
  remindOn: string;
  done: boolean;
  priority: ReminderPriority;
}

export type ReminderInput = Omit<Reminder, "id">;

export const REMINDER_FIELDS = ["id", "menuCategoryId", "title", "remindOn", "done", "priority"] as const;

/** Check Reminder.menuCategoryId (ref). */
export function checkReminderMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
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
    menuCategoryId: checkReminderMenuCategoryId(data.menuCategoryId),
    title: checkReminderTitle(data.title),
    remindOn: checkReminderRemindOn(data.remindOn),
    done: checkReminderDone(data.done),
    priority: checkReminderPriority(data.priority),
  };
}

/** The fields of a Reminder without its id. */
export function reminderInput(item: Reminder): ReminderInput {
  return {
    menuCategoryId: item.menuCategoryId,
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
  return [item.id, item.menuCategoryId, item.title, item.remindOn, item.done, item.priority];
}

export function compareReminderByMenuCategoryId(a: Reminder, b: Reminder): number {
  return a.menuCategoryId - b.menuCategoryId;
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
  menuCategoryId: number;
  subject: string;
  body: string;
  pinned: boolean;
  written: string;
}

export type NoteInput = Omit<Note, "id">;

export const NOTE_FIELDS = ["id", "menuCategoryId", "subject", "body", "pinned", "written"] as const;

/** Check Note.menuCategoryId (ref). */
export function checkNoteMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
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
    menuCategoryId: checkNoteMenuCategoryId(data.menuCategoryId),
    subject: checkNoteSubject(data.subject),
    body: checkNoteBody(data.body),
    pinned: checkNotePinned(data.pinned),
    written: checkNoteWritten(data.written),
  };
}

/** The fields of a Note without its id. */
export function noteInput(item: Note): NoteInput {
  return {
    menuCategoryId: item.menuCategoryId,
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
  return [item.id, item.menuCategoryId, item.subject, item.body, item.pinned, item.written];
}

export function compareNoteByMenuCategoryId(a: Note, b: Note): number {
  return a.menuCategoryId - b.menuCategoryId;
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
  menuCategoryId: number;
  author: string;
  stars: number;
  comment: string;
  verified: boolean;
  posted: string;
}

export type ReviewInput = Omit<Review, "id">;

export const REVIEW_FIELDS = ["id", "menuCategoryId", "author", "stars", "comment", "verified", "posted"] as const;

/** Check Review.menuCategoryId (ref). */
export function checkReviewMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
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
    menuCategoryId: checkReviewMenuCategoryId(data.menuCategoryId),
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
    menuCategoryId: item.menuCategoryId,
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
  return [item.id, item.menuCategoryId, item.author, item.stars, item.comment, item.verified, item.posted];
}

export function compareReviewByMenuCategoryId(a: Review, b: Review): number {
  return a.menuCategoryId - b.menuCategoryId;
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
  menuCategoryId: number;
  name: string;
  email: string;
  phone: string;
  role: string;
  primary: boolean;
}

export type ContactPersonInput = Omit<ContactPerson, "id">;

export const CONTACT_PERSON_FIELDS = ["id", "menuCategoryId", "name", "email", "phone", "role", "primary"] as const;

/** Check ContactPerson.menuCategoryId (ref). */
export function checkContactPersonMenuCategoryId(value: unknown): number {
  return checkRef("menuCategoryId", value);
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
    menuCategoryId: checkContactPersonMenuCategoryId(data.menuCategoryId),
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
    menuCategoryId: item.menuCategoryId,
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
  return [item.id, item.menuCategoryId, item.name, item.email, item.phone, item.role, item.primary];
}

export function compareContactPersonByMenuCategoryId(a: ContactPerson, b: ContactPerson): number {
  return a.menuCategoryId - b.menuCategoryId;
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
