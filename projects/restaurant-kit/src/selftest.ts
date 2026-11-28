/** Self-test for the Restaurant Orders kit: run `node dist/selftest.js` after `tsc -p .`. */

import { ValidationError } from "./models";
import { toCsv } from "./csv";
import { dailySales, dailySalesCsv } from "./reports";
import {
  ConflictError,
  NotFoundError,
  Services,
  sampleMenuCategory,
  sampleMenuItem,
  sampleDiningTable,
  sampleCustomerOrder,
  sampleOrderLine,
  sampleBooking,
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
  describeMenuCategory,
  queryMenuCategories,
  describeMenuItem,
  queryMenuItems,
  describeDiningTable,
  queryDiningTables,
  describeCustomerOrder,
  queryCustomerOrders,
  describeOrderLine,
  queryOrderLines,
  describeBooking,
  queryBookings,
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

// ---------------------------------------------------------------------------- MenuCategory

test("menu category: create and get", () => {
  const s = seeded();
  const item = s.menuCategories.create(sampleMenuCategory(10));
  assert(s.menuCategories.get(item.id) === item, "stored record differs");
  assert(s.menuCategories.list().length === 4, "list should have 4 records");
});

test("menu category: missing record", () => {
  throwsKind(() => seeded().menuCategories.get(9999), NotFoundError);
});

test("menu category: unknown field", () => {
  const data = sampleMenuCategory(11);
  data.noSuchField = 1;
  throwsField(() => seeded().menuCategories.create(data), "noSuchField");
});

test("menu category: id can't be chosen", () => {
  const data = sampleMenuCategory(11);
  data.id = 42;
  throwsField(() => seeded().menuCategories.create(data), "id");
});

test("menu category: rejects a bad name", () => {
  const data = sampleMenuCategory(12);
  data.name = "";
  throwsField(() => seeded().menuCategories.create(data), "name");
});

test("menu category: rejects a bad position", () => {
  const data = sampleMenuCategory(12);
  data.position = -1;
  throwsField(() => seeded().menuCategories.create(data), "position");
});

test("menu category: rejects a bad visible", () => {
  const data = sampleMenuCategory(12);
  data.visible = "yes";
  throwsField(() => seeded().menuCategories.create(data), "visible");
});

test("menu category: search name", () => {
  const s = seeded();
  const target = s.menuCategories.get(2);
  assert(s.store.menuCategories.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.menuCategories.findByName(target.name).includes(target), "find missed it");
});

test("menu category: adjust position", () => {
  const s = seeded();
  const before = s.menuCategories.get(1).position;
  assert(s.menuCategories.adjustPosition(1, 2).position === before + 2, "not adjusted");
  throwsField(() => s.menuCategories.adjustPosition(1, -(before + 100)), "position");
});

test("menu category: toggle visible", () => {
  const s = seeded();
  const before = s.menuCategories.get(1).visible;
  assert(s.menuCategories.toggleVisible(1).visible === !before, "flag not flipped");
});

test("menu category: delete an unused record", () => {
  const s = seeded();
  const item = s.menuCategories.create(sampleMenuCategory(14));
  s.menuCategories.delete(item.id);
  throwsKind(() => s.menuCategories.get(item.id), NotFoundError);
});

test("menu category: delete a record in use", () => {
  throwsKind(() => seeded().menuCategories.delete(1), ConflictError);
});

test("menu category: stats and queries", () => {
  const s = seeded();
  assert(s.menuCategories.stats().count === 3, "wrong count");
  const newest = queryMenuCategories(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryMenuCategories(s.store, { sort: "nope" }), "sort");
  assert(describeMenuCategory().length === 4, "field list incomplete");
});

// ---------------------------------------------------------------------------- MenuItem

test("menu item: create and get", () => {
  const s = seeded();
  const item = s.menuItems.create(sampleMenuItem(10));
  assert(s.menuItems.get(item.id) === item, "stored record differs");
  assert(s.menuItems.list().length === 4, "list should have 4 records");
});

test("menu item: missing record", () => {
  throwsKind(() => seeded().menuItems.get(9999), NotFoundError);
});

test("menu item: unknown field", () => {
  const data = sampleMenuItem(11);
  data.noSuchField = 1;
  throwsField(() => seeded().menuItems.create(data), "noSuchField");
});

test("menu item: id can't be chosen", () => {
  const data = sampleMenuItem(11);
  data.id = 42;
  throwsField(() => seeded().menuItems.create(data), "id");
});

test("menu item: rejects a bad menu category id", () => {
  const data = sampleMenuItem(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().menuItems.create(data), "menuCategoryId");
});

test("menu item: rejects a bad name", () => {
  const data = sampleMenuItem(12);
  data.name = "";
  throwsField(() => seeded().menuItems.create(data), "name");
});

test("menu item: rejects a bad price", () => {
  const data = sampleMenuItem(12);
  data.price = -5;
  throwsField(() => seeded().menuItems.create(data), "price");
});

test("menu item: rejects a bad calories", () => {
  const data = sampleMenuItem(12);
  data.calories = -1;
  throwsField(() => seeded().menuItems.create(data), "calories");
});

test("menu item: rejects a bad spicy", () => {
  const data = sampleMenuItem(12);
  data.spicy = "yes";
  throwsField(() => seeded().menuItems.create(data), "spicy");
});

test("menu item: rejects a bad vegetarian", () => {
  const data = sampleMenuItem(12);
  data.vegetarian = "yes";
  throwsField(() => seeded().menuItems.create(data), "vegetarian");
});

test("menu item: rejects a bad prep minutes", () => {
  const data = sampleMenuItem(12);
  data.prepMinutes = -1;
  throwsField(() => seeded().menuItems.create(data), "prepMinutes");
});

test("menu item: menu category id must exist", () => {
  const data = sampleMenuItem(13);
  data.menuCategoryId = 9999;
  throwsKind(() => seeded().menuItems.create(data), NotFoundError);
});

test("menu item: search name", () => {
  const s = seeded();
  const target = s.menuItems.get(2);
  assert(s.store.menuItems.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.menuItems.findByName(target.name).includes(target), "find missed it");
});

test("menu item: adjust price", () => {
  const s = seeded();
  const before = s.menuItems.get(1).price;
  assert(Math.abs(s.menuItems.adjustPrice(1, 1.5).price - (before + 1.5)) < 0.01, "not adjusted");
});

test("menu item: adjust calories", () => {
  const s = seeded();
  const before = s.menuItems.get(1).calories;
  assert(s.menuItems.adjustCalories(1, 2).calories === before + 2, "not adjusted");
  throwsField(() => s.menuItems.adjustCalories(1, -(before + 100)), "calories");
});

test("menu item: toggle spicy", () => {
  const s = seeded();
  const before = s.menuItems.get(1).spicy;
  assert(s.menuItems.toggleSpicy(1).spicy === !before, "flag not flipped");
});

test("menu item: toggle vegetarian", () => {
  const s = seeded();
  const before = s.menuItems.get(1).vegetarian;
  assert(s.menuItems.toggleVegetarian(1).vegetarian === !before, "flag not flipped");
});

test("menu item: adjust prep minutes", () => {
  const s = seeded();
  const before = s.menuItems.get(1).prepMinutes;
  assert(s.menuItems.adjustPrepMinutes(1, 2).prepMinutes === before + 2, "not adjusted");
  throwsField(() => s.menuItems.adjustPrepMinutes(1, -(before + 100)), "prepMinutes");
});

test("menu item: delete an unused record", () => {
  const s = seeded();
  const item = s.menuItems.create(sampleMenuItem(14));
  s.menuItems.delete(item.id);
  throwsKind(() => s.menuItems.get(item.id), NotFoundError);
});

test("menu item: delete a record in use", () => {
  throwsKind(() => seeded().menuItems.delete(1), ConflictError);
});

test("menu item: stats and queries", () => {
  const s = seeded();
  assert(s.menuItems.stats().count === 3, "wrong count");
  const newest = queryMenuItems(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryMenuItems(s.store, { sort: "nope" }), "sort");
  assert(describeMenuItem().length === 8, "field list incomplete");
});

// ---------------------------------------------------------------------------- DiningTable

test("dining table: create and get", () => {
  const s = seeded();
  const item = s.diningTables.create(sampleDiningTable(10));
  assert(s.diningTables.get(item.id) === item, "stored record differs");
  assert(s.diningTables.list().length === 4, "list should have 4 records");
});

test("dining table: missing record", () => {
  throwsKind(() => seeded().diningTables.get(9999), NotFoundError);
});

test("dining table: unknown field", () => {
  const data = sampleDiningTable(11);
  data.noSuchField = 1;
  throwsField(() => seeded().diningTables.create(data), "noSuchField");
});

test("dining table: id can't be chosen", () => {
  const data = sampleDiningTable(11);
  data.id = 42;
  throwsField(() => seeded().diningTables.create(data), "id");
});

test("dining table: rejects a bad label", () => {
  const data = sampleDiningTable(12);
  data.label = "";
  throwsField(() => seeded().diningTables.create(data), "label");
});

test("dining table: rejects a bad seats", () => {
  const data = sampleDiningTable(12);
  data.seats = -1;
  throwsField(() => seeded().diningTables.create(data), "seats");
});

test("dining table: rejects a bad area", () => {
  const data = sampleDiningTable(12);
  data.area = "nope";
  throwsField(() => seeded().diningTables.create(data), "area");
});

test("dining table: rejects a bad active", () => {
  const data = sampleDiningTable(12);
  data.active = "yes";
  throwsField(() => seeded().diningTables.create(data), "active");
});

test("dining table: search label", () => {
  const s = seeded();
  const target = s.diningTables.get(2);
  assert(s.store.diningTables.searchLabel(target.label.toUpperCase()).includes(target), "search missed it");
  assert(s.store.diningTables.findByLabel(target.label).includes(target), "find missed it");
});

test("dining table: adjust seats", () => {
  const s = seeded();
  const before = s.diningTables.get(1).seats;
  assert(s.diningTables.adjustSeats(1, 2).seats === before + 2, "not adjusted");
  throwsField(() => s.diningTables.adjustSeats(1, -(before + 100)), "seats");
});

test("dining table: set area", () => {
  const s = seeded();
  assert(s.diningTables.setArea(1, "private").area === "private", "value not changed");
  assert(s.store.diningTables.countByArea()["private"] === s.store.diningTables.withArea("private").length, "counts differ");
});

test("dining table: toggle active", () => {
  const s = seeded();
  const before = s.diningTables.get(1).active;
  assert(s.diningTables.toggleActive(1).active === !before, "flag not flipped");
});

test("dining table: delete an unused record", () => {
  const s = seeded();
  const item = s.diningTables.create(sampleDiningTable(14));
  s.diningTables.delete(item.id);
  throwsKind(() => s.diningTables.get(item.id), NotFoundError);
});

test("dining table: delete a record in use", () => {
  throwsKind(() => seeded().diningTables.delete(1), ConflictError);
});

test("dining table: stats and queries", () => {
  const s = seeded();
  assert(s.diningTables.stats().count === 3, "wrong count");
  const newest = queryDiningTables(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryDiningTables(s.store, { sort: "nope" }), "sort");
  assert(describeDiningTable().length === 5, "field list incomplete");
});

// ---------------------------------------------------------------------------- CustomerOrder

test("customer order: create and get", () => {
  const s = seeded();
  const item = s.customerOrders.create(sampleCustomerOrder(10));
  assert(s.customerOrders.get(item.id) === item, "stored record differs");
  assert(s.customerOrders.list().length === 4, "list should have 4 records");
});

test("customer order: missing record", () => {
  throwsKind(() => seeded().customerOrders.get(9999), NotFoundError);
});

test("customer order: unknown field", () => {
  const data = sampleCustomerOrder(11);
  data.noSuchField = 1;
  throwsField(() => seeded().customerOrders.create(data), "noSuchField");
});

test("customer order: id can't be chosen", () => {
  const data = sampleCustomerOrder(11);
  data.id = 42;
  throwsField(() => seeded().customerOrders.create(data), "id");
});

test("customer order: rejects a bad dining table id", () => {
  const data = sampleCustomerOrder(12);
  data.diningTableId = 0;
  throwsField(() => seeded().customerOrders.create(data), "diningTableId");
});

test("customer order: rejects a bad opened", () => {
  const data = sampleCustomerOrder(12);
  data.opened = "2026-02-30";
  throwsField(() => seeded().customerOrders.create(data), "opened");
});

test("customer order: rejects a bad guests", () => {
  const data = sampleCustomerOrder(12);
  data.guests = -1;
  throwsField(() => seeded().customerOrders.create(data), "guests");
});

test("customer order: rejects a bad total", () => {
  const data = sampleCustomerOrder(12);
  data.total = -5;
  throwsField(() => seeded().customerOrders.create(data), "total");
});

test("customer order: rejects a bad status", () => {
  const data = sampleCustomerOrder(12);
  data.status = "nope";
  throwsField(() => seeded().customerOrders.create(data), "status");
});

test("customer order: rejects a bad server", () => {
  const data = sampleCustomerOrder(12);
  data.server = "";
  throwsField(() => seeded().customerOrders.create(data), "server");
});

test("customer order: dining table id must exist", () => {
  const data = sampleCustomerOrder(13);
  data.diningTableId = 9999;
  throwsKind(() => seeded().customerOrders.create(data), NotFoundError);
});

test("customer order: opened ranges", () => {
  const s = seeded();
  const day = s.customerOrders.get(2).opened;
  const total = s.store.customerOrders.openedBefore(day).length + s.store.customerOrders.openedOn(day).length + s.store.customerOrders.openedAfter(day).length;
  assert(total === s.store.customerOrders.count(), "ranges don't cover every record");
});

test("customer order: adjust guests", () => {
  const s = seeded();
  const before = s.customerOrders.get(1).guests;
  assert(s.customerOrders.adjustGuests(1, 2).guests === before + 2, "not adjusted");
  throwsField(() => s.customerOrders.adjustGuests(1, -(before + 100)), "guests");
});

test("customer order: adjust total", () => {
  const s = seeded();
  const before = s.customerOrders.get(1).total;
  assert(Math.abs(s.customerOrders.adjustTotal(1, 1.5).total - (before + 1.5)) < 0.01, "not adjusted");
});

test("customer order: set status", () => {
  const s = seeded();
  assert(s.customerOrders.setStatus(1, "cancelled").status === "cancelled", "value not changed");
  assert(s.store.customerOrders.countByStatus()["cancelled"] === s.store.customerOrders.withStatus("cancelled").length, "counts differ");
});

test("customer order: search server", () => {
  const s = seeded();
  const target = s.customerOrders.get(2);
  assert(s.store.customerOrders.searchServer(target.server.toUpperCase()).includes(target), "search missed it");
  assert(s.store.customerOrders.findByServer(target.server).includes(target), "find missed it");
});

test("customer order: delete an unused record", () => {
  const s = seeded();
  const item = s.customerOrders.create(sampleCustomerOrder(14));
  s.customerOrders.delete(item.id);
  throwsKind(() => s.customerOrders.get(item.id), NotFoundError);
});

test("customer order: delete a record in use", () => {
  throwsKind(() => seeded().customerOrders.delete(1), ConflictError);
});

test("customer order: stats and queries", () => {
  const s = seeded();
  assert(s.customerOrders.stats().count === 3, "wrong count");
  const newest = queryCustomerOrders(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryCustomerOrders(s.store, { sort: "nope" }), "sort");
  assert(describeCustomerOrder().length === 7, "field list incomplete");
});

// ---------------------------------------------------------------------------- OrderLine

test("order line: create and get", () => {
  const s = seeded();
  const item = s.orderLines.create(sampleOrderLine(10));
  assert(s.orderLines.get(item.id) === item, "stored record differs");
  assert(s.orderLines.list().length === 4, "list should have 4 records");
});

test("order line: missing record", () => {
  throwsKind(() => seeded().orderLines.get(9999), NotFoundError);
});

test("order line: unknown field", () => {
  const data = sampleOrderLine(11);
  data.noSuchField = 1;
  throwsField(() => seeded().orderLines.create(data), "noSuchField");
});

test("order line: id can't be chosen", () => {
  const data = sampleOrderLine(11);
  data.id = 42;
  throwsField(() => seeded().orderLines.create(data), "id");
});

test("order line: rejects a bad customer order id", () => {
  const data = sampleOrderLine(12);
  data.customerOrderId = 0;
  throwsField(() => seeded().orderLines.create(data), "customerOrderId");
});

test("order line: rejects a bad menu item id", () => {
  const data = sampleOrderLine(12);
  data.menuItemId = 0;
  throwsField(() => seeded().orderLines.create(data), "menuItemId");
});

test("order line: rejects a bad quantity", () => {
  const data = sampleOrderLine(12);
  data.quantity = -1;
  throwsField(() => seeded().orderLines.create(data), "quantity");
});

test("order line: rejects a bad unit price", () => {
  const data = sampleOrderLine(12);
  data.unitPrice = -5;
  throwsField(() => seeded().orderLines.create(data), "unitPrice");
});

test("order line: rejects a bad note", () => {
  const data = sampleOrderLine(12);
  data.note = "x".repeat(3000);
  throwsField(() => seeded().orderLines.create(data), "note");
});

test("order line: customer order id must exist", () => {
  const data = sampleOrderLine(13);
  data.customerOrderId = 9999;
  throwsKind(() => seeded().orderLines.create(data), NotFoundError);
});

test("order line: menu item id must exist", () => {
  const data = sampleOrderLine(13);
  data.menuItemId = 9999;
  throwsKind(() => seeded().orderLines.create(data), NotFoundError);
});

test("order line: adjust quantity", () => {
  const s = seeded();
  const before = s.orderLines.get(1).quantity;
  assert(s.orderLines.adjustQuantity(1, 2).quantity === before + 2, "not adjusted");
  throwsField(() => s.orderLines.adjustQuantity(1, -(before + 100)), "quantity");
});

test("order line: adjust unit price", () => {
  const s = seeded();
  const before = s.orderLines.get(1).unitPrice;
  assert(Math.abs(s.orderLines.adjustUnitPrice(1, 1.5).unitPrice - (before + 1.5)) < 0.01, "not adjusted");
});

test("order line: search note", () => {
  const s = seeded();
  const target = s.orderLines.get(2);
  assert(s.store.orderLines.searchNote(target.note.toUpperCase()).includes(target), "search missed it");
  assert(s.store.orderLines.findByNote(target.note).includes(target), "find missed it");
});

test("order line: delete an unused record", () => {
  const s = seeded();
  const item = s.orderLines.create(sampleOrderLine(14));
  s.orderLines.delete(item.id);
  throwsKind(() => s.orderLines.get(item.id), NotFoundError);
});

test("order line: stats and queries", () => {
  const s = seeded();
  assert(s.orderLines.stats().count === 3, "wrong count");
  const newest = queryOrderLines(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryOrderLines(s.store, { sort: "nope" }), "sort");
  assert(describeOrderLine().length === 6, "field list incomplete");
});

// ---------------------------------------------------------------------------- Booking

test("booking: create and get", () => {
  const s = seeded();
  const item = s.bookings.create(sampleBooking(10));
  assert(s.bookings.get(item.id) === item, "stored record differs");
  assert(s.bookings.list().length === 4, "list should have 4 records");
});

test("booking: missing record", () => {
  throwsKind(() => seeded().bookings.get(9999), NotFoundError);
});

test("booking: unknown field", () => {
  const data = sampleBooking(11);
  data.noSuchField = 1;
  throwsField(() => seeded().bookings.create(data), "noSuchField");
});

test("booking: id can't be chosen", () => {
  const data = sampleBooking(11);
  data.id = 42;
  throwsField(() => seeded().bookings.create(data), "id");
});

test("booking: rejects a bad dining table id", () => {
  const data = sampleBooking(12);
  data.diningTableId = 0;
  throwsField(() => seeded().bookings.create(data), "diningTableId");
});

test("booking: rejects a bad name", () => {
  const data = sampleBooking(12);
  data.name = "";
  throwsField(() => seeded().bookings.create(data), "name");
});

test("booking: rejects a bad phone", () => {
  const data = sampleBooking(12);
  data.phone = "";
  throwsField(() => seeded().bookings.create(data), "phone");
});

test("booking: rejects a bad day", () => {
  const data = sampleBooking(12);
  data.day = "2026-02-30";
  throwsField(() => seeded().bookings.create(data), "day");
});

test("booking: rejects a bad party size", () => {
  const data = sampleBooking(12);
  data.partySize = -1;
  throwsField(() => seeded().bookings.create(data), "partySize");
});

test("booking: rejects a bad confirmed", () => {
  const data = sampleBooking(12);
  data.confirmed = "yes";
  throwsField(() => seeded().bookings.create(data), "confirmed");
});

test("booking: dining table id must exist", () => {
  const data = sampleBooking(13);
  data.diningTableId = 9999;
  throwsKind(() => seeded().bookings.create(data), NotFoundError);
});

test("booking: search name", () => {
  const s = seeded();
  const target = s.bookings.get(2);
  assert(s.store.bookings.searchName(target.name.toUpperCase()).includes(target), "search missed it");
  assert(s.store.bookings.findByName(target.name).includes(target), "find missed it");
});

test("booking: search phone", () => {
  const s = seeded();
  const target = s.bookings.get(2);
  assert(s.store.bookings.searchPhone(target.phone.toUpperCase()).includes(target), "search missed it");
  assert(s.store.bookings.findByPhone(target.phone).includes(target), "find missed it");
});

test("booking: day ranges", () => {
  const s = seeded();
  const day = s.bookings.get(2).day;
  const total = s.store.bookings.dayBefore(day).length + s.store.bookings.dayOn(day).length + s.store.bookings.dayAfter(day).length;
  assert(total === s.store.bookings.count(), "ranges don't cover every record");
});

test("booking: adjust party size", () => {
  const s = seeded();
  const before = s.bookings.get(1).partySize;
  assert(s.bookings.adjustPartySize(1, 2).partySize === before + 2, "not adjusted");
  throwsField(() => s.bookings.adjustPartySize(1, -(before + 100)), "partySize");
});

test("booking: toggle confirmed", () => {
  const s = seeded();
  const before = s.bookings.get(1).confirmed;
  assert(s.bookings.toggleConfirmed(1).confirmed === !before, "flag not flipped");
});

test("booking: delete an unused record", () => {
  const s = seeded();
  const item = s.bookings.create(sampleBooking(14));
  s.bookings.delete(item.id);
  throwsKind(() => s.bookings.get(item.id), NotFoundError);
});

test("booking: stats and queries", () => {
  const s = seeded();
  assert(s.bookings.stats().count === 3, "wrong count");
  const newest = queryBookings(s.store, { sort: "-id", size: "1" });
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => queryBookings(s.store, { sort: "nope" }), "sort");
  assert(describeBooking().length === 7, "field list incomplete");
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

test("document: rejects a bad menu category id", () => {
  const data = sampleDocument(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().documents.create(data), "menuCategoryId");
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

test("document: menu category id must exist", () => {
  const data = sampleDocument(13);
  data.menuCategoryId = 9999;
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

test("address: rejects a bad menu category id", () => {
  const data = sampleAddress(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().addresses.create(data), "menuCategoryId");
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

test("address: menu category id must exist", () => {
  const data = sampleAddress(13);
  data.menuCategoryId = 9999;
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

test("reminder: rejects a bad menu category id", () => {
  const data = sampleReminder(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().reminders.create(data), "menuCategoryId");
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

test("reminder: menu category id must exist", () => {
  const data = sampleReminder(13);
  data.menuCategoryId = 9999;
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

test("note: rejects a bad menu category id", () => {
  const data = sampleNote(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().notes.create(data), "menuCategoryId");
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

test("note: menu category id must exist", () => {
  const data = sampleNote(13);
  data.menuCategoryId = 9999;
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

test("review: rejects a bad menu category id", () => {
  const data = sampleReview(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().reviews.create(data), "menuCategoryId");
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

test("review: menu category id must exist", () => {
  const data = sampleReview(13);
  data.menuCategoryId = 9999;
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

test("contact person: rejects a bad menu category id", () => {
  const data = sampleContactPerson(12);
  data.menuCategoryId = 0;
  throwsField(() => seeded().contactPersons.create(data), "menuCategoryId");
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

test("contact person: menu category id must exist", () => {
  const data = sampleContactPerson(13);
  data.menuCategoryId = 9999;
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
  const output = toCsv(["name", "note"], [["Tea", "hot, iced"]]);
  assert(output === "name,note\r\nTea,\"hot, iced\"\r\n", "CSV quoting was incorrect");
});

test("reports: daily totals include paid orders only", () => {
  const rows = dailySales([
    { id: 1, diningTableId: 1, opened: "2026-04-02", guests: 2, total: 12.5, status: "paid", server: "Sam" },
    { id: 2, diningTableId: 1, opened: "2026-04-02", guests: 1, total: 7.5, status: "paid", server: "Lee" },
    { id: 3, diningTableId: 2, opened: "2026-04-02", guests: 2, total: 99, status: "open", server: "Sam" },
  ]);
  assert(rows.length === 1 && rows[0].orders === 2 && rows[0].gross === 20 && rows[0].average === 10,
    "paid daily sales were incorrect");
  assert(dailySalesCsv([]) === "day,orders,gross,average\r\n", "empty report header was incorrect");
});

console.log(`${passed} passed, ${failures.length} failed`);
for (const failure of failures) {
  console.log(`FAIL ${failure}`);
}
if (failures.length > 0) {
  throw new Error(`${failures.length} test(s) failed`);
}
