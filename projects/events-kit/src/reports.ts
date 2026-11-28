/** Ticket inventory summaries for the Event Ticketing kit. */

import { TicketType } from "./models";
import { toCsv } from "./csv";

export interface TicketSales {
  ticketTypeId: number;
  concertId: number;
  name: string;
  sold: number;
  remaining: number;
  gross: number;
}

/** Summarize ticket capacity and gross sales for every ticket type. */
export function ticketSales(ticketTypes: readonly TicketType[]): TicketSales[] {
  return ticketTypes.slice().sort((a, b) => a.concertId - b.concertId || a.id - b.id).map((item) => ({
    ticketTypeId: item.id,
    concertId: item.concertId,
    name: item.name,
    sold: item.sold,
    remaining: Math.max(0, item.quantity - item.sold),
    gross: Math.round(item.price * item.sold * 100) / 100,
  }));
}

/** Export ticket inventory and gross revenue as spreadsheet friendly CSV. */
export function ticketSalesCsv(ticketTypes: readonly TicketType[]): string {
  return toCsv(["ticketTypeId", "concertId", "name", "sold", "remaining", "gross"],
    ticketSales(ticketTypes).map((row) => [
      row.ticketTypeId, row.concertId, row.name, row.sold, row.remaining, row.gross.toFixed(2),
    ]));
}
