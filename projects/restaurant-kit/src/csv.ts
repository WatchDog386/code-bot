/** Small CSV helpers for exporting validated records and report rows. */

export type CsvValue = string | number | boolean | null | undefined;

function cell(value: CsvValue): string {
  const text = value == null ? "" : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

/** Convert a header and equally sized rows to RFC 4180 style CSV with a final newline. */
export function toCsv(headers: readonly string[], rows: readonly (readonly CsvValue[])[]): string {
  for (const [index, row] of rows.entries()) {
    if (row.length !== headers.length) {
      throw new Error(`row ${index + 1} has ${row.length} values; expected ${headers.length}`);
    }
  }
  return [headers.map(cell).join(","), ...rows.map((row) => row.map(cell).join(","))].join("\r\n") + "\r\n";
}
