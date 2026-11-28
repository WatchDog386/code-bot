/** Sales summaries for the Restaurant Orders kit. */

import { CustomerOrder } from "./models";
import { toCsv } from "./csv";

export interface DailySales {
  day: string;
  orders: number;
  gross: number;
  average: number;
}

/** Group completed orders by service day and calculate rounded gross totals. */
export function dailySales(orders: readonly CustomerOrder[]): DailySales[] {
  const totals = new Map<string, { orders: number; cents: number }>();
  for (const order of orders) {
    if (order.status !== "paid") continue;
    const total = totals.get(order.opened) ?? { orders: 0, cents: 0 };
    total.orders += 1;
    total.cents += Math.round(order.total * 100);
    totals.set(order.opened, total);
  }
  return [...totals.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([day, total]) => {
    const gross = total.cents / 100;
    return { day, orders: total.orders, gross, average: Math.round(gross / total.orders * 100) / 100 };
  });
}

/** Export a daily sales summary that opens cleanly in spreadsheet software. */
export function dailySalesCsv(orders: readonly CustomerOrder[]): string {
  return toCsv(["day", "orders", "gross", "average"], dailySales(orders).map((row) => [
    row.day, row.orders, row.gross.toFixed(2), row.average.toFixed(2),
  ]));
}
