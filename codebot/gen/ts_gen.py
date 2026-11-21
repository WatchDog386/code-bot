"""TypeScript flavour: a strict, dependency-free domain kit (models, store, services,
queries, self-test). Built with `tsc -p .` and checked with `node dist/selftest.js`."""

from .schema import enum_type, NUMERIC, TEXTUAL, camel, lower_camel

TS_TYPE = {"str": "string", "text": "string", "email": "string", "int": "number", "float": "number",
           "money": "number", "bool": "boolean", "date": "string", "ref": "number"}


def fname(f):
    return lower_camel(f.name)


def etype(e, f):
    return enum_type(e, f)


def values_const(e, f):
    return f"{e.snake.upper()}_{f.name.upper()}_VALUES"


def ttype(e, f):
    return etype(e, f) if f.kind == "enum" else TS_TYPE[f.kind]


def ev(e):                       # variable name for a record
    return lower_camel(e.snake)


def pv(e):                       # plural variable / property
    return lower_camel(e.plural)


class W:
    def __init__(self):
        self.lines = []

    def __call__(self, text="", indent=0):
        for line in text.split("\n") if text else [""]:
            self.lines.append(("  " * indent + line) if line else "")

    def text(self):
        return "\n".join(self.lines).rstrip() + "\n"


def check(e, f, var):
    k, n = f.kind, f.name
    lc = fname(f)
    return {
        "str": f'checkText("{lc}", {var})',
        "text": f'checkText("{lc}", {var}, 2000, false)',
        "email": f'checkEmail("{lc}", {var})',
        "int": f'checkInt("{lc}", {var})',
        "float": f'checkNumber("{lc}", {var})',
        "money": f'checkMoney("{lc}", {var})',
        "bool": f'checkFlag("{lc}", {var})',
        "date": f'checkDate("{lc}", {var})',
        "enum": f'checkChoice("{lc}", {var}, {values_const(e, f)})',
        "ref": f'checkRef("{lc}", {var})',
    }[k]


# ---------------------------------------------------------------------------- models
def models_ts(d):
    w = W()
    w("/**")
    w(f" * Domain models for the {d.title} kit: record types, the allowed values of every")
    w(" * choice field, and validation that turns untrusted data into checked records.")
    w(" */")
    w("""
export class ValidationError extends Error {
  constructor(
    public readonly field: string,
    message: string,
  ) {
    super(`${field}: ${message}`);
    this.name = "ValidationError";
  }
}

const DATE_RE = /^\\d{4}-\\d{2}-\\d{2}$/;
const EMAIL_RE = /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/;
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
}""")
    for e in d.entities:
        for f in e.of("enum"):
            c, t = values_const(e, f), etype(e, f)
            w()
            w(f"/** Allowed values of {e.name}.{fname(f)}. */")
            w(f"export const {c} = [" + ", ".join(f'"{v}"' for v in f.values) + "] as const;")
            w(f"export type {t} = (typeof {c})[number];")
            w()
            w(f"export function is{t}(value: unknown): value is {t} {{")
            w(f"  return typeof value === \"string\" && ({c} as readonly string[]).includes(value);")
            w("}")
            w()
            w(f"export function label{t}(value: {t}): string {{")
            w('  const text = value.replace(/_/g, " ");')
            w("  return text.charAt(0).toUpperCase() + text.slice(1);")
            w("}")
    for e in d.entities:
        N, up, v = e.name, e.snake.upper(), ev(e)
        w()
        w(f"// {'-' * 76} {N}")
        w()
        w(f"/** A {e.human} record. */")
        w(f"export interface {N} {{")
        w("  id: number;")
        for f in e.fields:
            w(f"  {fname(f)}: {ttype(e, f)};")
        w("}")
        w()
        w(f'export type {N}Input = Omit<{N}, "id">;')
        w()
        w(f"export const {up}_FIELDS = [\"id\", " + ", ".join(f'"{fname(f)}"' for f in e.fields) + "] as const;")
        w()
        for f in e.fields:
            w(f"/** Check {N}.{fname(f)} ({f.kind}). */")
            w(f"export function check{N}{camel(f.name)}(value: unknown): {ttype(e, f)} {{")
            w(f"  return {check(e, f, 'value')};")
            w("}")
            w()
        w(f"/** A checked {N} from untrusted data (every field is required). */")
        w(f"export function parse{N}(data: Record<string, unknown>, id = 0): {N} {{")
        w(f"  rejectUnknown(data, {up}_FIELDS);")
        w("  return {")
        w("    id,")
        for f in e.fields:
            w(f"    {fname(f)}: check{N}{camel(f.name)}(data.{fname(f)}),")
        w("  };")
        w("}")
        w()
        w(f"/** The fields of a {N} without its id. */")
        w(f"export function {v}Input(item: {N}): {N}Input {{")
        w("  return {")
        for f in e.fields:
            w(f"    {fname(f)}: item.{fname(f)},")
        w("  };")
        w("}")
        w()
        w(f"/** A checked copy of `item` with `changes` applied; the id never changes. */")
        w(f"export function patch{N}(item: {N}, changes: Record<string, unknown>): {N} {{")
        w('  if ("id" in changes) {')
        w('    throw new ValidationError("id", "cannot be changed");')
        w("  }")
        w(f"  rejectUnknown(changes, {up}_FIELDS);")
        w(f"  return parse{N}({{ ...{v}Input(item), ...changes }}, item.id);")
        w("}")
        w()
        lf = e.label_field
        w(f"/** One line for logs and lists. */")
        w(f"export function summarize{N}(item: {N}): string {{")
        if lf:
            w(f"  return `{N} #${{item.id}}: ${{item.{fname(lf)}}}`;")
        else:
            w(f"  return `{N} #${{item.id}}`;")
        w("}")
        w()
        w(f"/** The record as one CSV-ready row (same order as {up}_FIELDS). */")
        w(f"export function {v}Row(item: {N}): Array<string | number | boolean> {{")
        w("  return [item.id, " + ", ".join(f"item.{fname(f)}" for f in e.fields) + "];")
        w("}")
        for f in e.fields:
            if f.kind == "bool":
                continue
            a, b = f"a.{fname(f)}", f"b.{fname(f)}"
            w()
            w(f"export function compare{N}By{camel(f.name)}(a: {N}, b: {N}): number {{")
            if TS_TYPE.get(f.kind) == "number":
                w(f"  return {a} - {b};")
            else:
                w(f"  return {a} < {b} ? -1 : {a} > {b} ? 1 : 0;")
            w("}")
    return w.text()


# ----------------------------------------------------------------------------- store
def store_ts(d):
    w = W()
    w("/** In-memory storage for the " + d.title + " kit, with the lookups the services need. */")
    w()
    names = set()
    for e in d.entities:
        names.add(e.name)
        for f in e.of("enum"):
            names.add(etype(e, f))
            names.add(values_const(e, f))
    w("import {")
    for n in sorted(names):
        w(f"  {n},")
    w('} from "./models";')
    w("""
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
}""")
    for e in d.entities:
        N = e.name
        w()
        w(f"/** Every {e.human}. */")
        w(f"export class {N}Store extends Collection<{N}> {{")
        first = True
        for f in e.fields:
            fn, C = fname(f), camel(f.name)
            if not first:
                pass
            if f.kind in TEXTUAL:
                w(f"""  findBy{C}(value: string): {N}[] {{
    return this.where((item) => item.{fn} === value);
  }}

  search{C}(text: string): {N}[] {{
    const needle = text.trim().toLowerCase();
    return this.where((item) => item.{fn}.toLowerCase().includes(needle));
  }}
""")
            elif f.kind in NUMERIC:
                w(f"""  between{C}(low: number, high: number): {N}[] {{
    return this.where((item) => item.{fn} >= low && item.{fn} <= high);
  }}

  total{C}(): number {{
    return this.list().reduce((sum, item) => sum + item.{fn}, 0);
  }}

  average{C}(): number {{
    const items = this.list();
    return items.length ? this.total{C}() / items.length : 0;
  }}

  max{C}(): {N} | undefined {{
    return this.list().reduce<{N} | undefined>((best, item) => (best === undefined || item.{fn} > best.{fn} ? item : best), undefined);
  }}
""")
            elif f.kind == "enum":
                t, c = etype(e, f), values_const(e, f)
                w(f"""  with{C}(value: {t}): {N}[] {{
    return this.where((item) => item.{fn} === value);
  }}

  countBy{C}(): Record<{t}, number> {{
    const counts = Object.fromEntries({c}.map((value) => [value, 0])) as Record<{t}, number>;
    for (const item of this.list()) {{
      counts[item.{fn}] += 1;
    }}
    return counts;
  }}
""")
            elif f.kind == "bool":
                w(f"""  where{C}(flag = true): {N}[] {{
    return this.where((item) => item.{fn} === flag);
  }}
""")
            elif f.kind == "date":
                w(f"""  {fn}Before(day: string): {N}[] {{
    return this.where((item) => item.{fn} < day);
  }}

  {fn}After(day: string): {N}[] {{
    return this.where((item) => item.{fn} > day);
  }}

  {fn}On(day: string): {N}[] {{
    return this.where((item) => item.{fn} === day);
  }}
""")
            elif f.kind == "ref":
                st = camel(f.ref_stem)
                w(f"""  for{st}(id: number): {N}[] {{
    return this.where((item) => item.{fn} === id);
  }}

  countFor{st}(id: number): number {{
    return this.for{st}(id).length;
  }}
""")
        tf = e.of("str", "text", "email")
        w(f"  /** Records where any text field contains `text`. */")
        w(f"  search(text: string): {N}[] {{")
        w("    const needle = text.trim().toLowerCase();")
        if tf:
            w("    return this.where((item) => [" + ", ".join(f"item.{fname(f)}" for f in tf) +
              "].some((value) => value.toLowerCase().includes(needle)));")
        else:
            w('    return this.where((item) => needle === "" || String(item.id) === needle);')
        w("  }")
        w("}")
    return w.text()


# -------------------------------------------------------------------------- services
def sample(e, f):
    k = f.kind
    if k == "str":
        return "`" + f"{e.human.capitalize()} {f.human} " + "${i}`"
    if k == "text":
        return "`" + f"Notes about {e.human} " + "${i}.`"
    if k == "email":
        return "`" + e.snake + "${i}@example.com`"
    if k == "int":
        return "i + 1"
    if k == "float":
        return "1.5 * i + 0.25"
    if k == "money":
        return "Math.round((10 * i + 0.99) * 100) / 100"
    if k == "bool":
        return "i % 2 === 1"
    if k == "date":
        return "`2026-${String((i % 12) + 1).padStart(2, \"0\")}-${String((i % 28) + 1).padStart(2, \"0\")}`"
    if k == "enum":
        return f"{values_const(e, f)}[i % {len(f.values)}]"
    return "((i - 1) % 3) + 1"


def services_ts(d):
    w = W()
    w("/**")
    w(f" * Business rules for the {d.title} kit: validation, links between records (a record")
    w(" * can't point at something missing, or be deleted while others point at it), small")
    w(" * domain operations and statistics.")
    w(" */")
    w()
    names = {"ValidationError"}
    for e in d.entities:
        names |= {e.name, f"parse{e.name}", f"patch{e.name}"}
        for f in e.of("enum"):
            names |= {etype(e, f), values_const(e, f)}
    w("import {")
    for n in sorted(names):
        w(f"  {n},")
    w('} from "./models";')
    w("import {")
    for e in d.entities:
        w(f"  {e.name}Store,")
    w('} from "./store";')
    w("""
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
export class Store {""")
    for e in d.entities:
        w(f"  readonly {pv(e)} = new {e.name}Store();")
    w()
    w("  counts(): Record<string, number> {")
    w("    return {")
    for e in d.entities:
        w(f"      {pv(e)}: this.{pv(e)}.count(),")
    w("    };")
    w("  }")
    w("}")
    for e in d.entities:
        N, P = e.name, pv(e)
        w()
        w(f"/** Create, change and remove {e.plural.replace('_', ' ')}. */")
        w(f"export class {N}Service {{")
        w("  constructor(private readonly store: Store) {}")
        w()
        w(f"  private get repo(): {N}Store {{")
        w(f"    return this.store.{P};")
        w("  }")
        w(f"""
  /** Validate and store a new {e.human}. */
  create(data: Record<string, unknown>): {N} {{
    if ("id" in data) {{
      throw new ValidationError("id", "is assigned automatically");
    }}
    const item = parse{N}(data);
    this.checkLinks(item);
    return this.repo.add(item);
  }}

  get(id: number): {N} {{
    const item = this.repo.get(id);
    if (!item) {{
      throw new NotFoundError("{e.human}", id);
    }}
    return item;
  }}

  list(): {N}[] {{
    return this.repo.list();
  }}

  /** Change some fields of a {e.human}. */
  update(id: number, changes: Record<string, unknown>): {N} {{
    const updated = patch{N}(this.get(id), changes);
    this.checkLinks(updated);
    return this.repo.save(updated);
  }}

  /** Remove a {e.human} nothing points at any more. */
  delete(id: number): void {{
    this.get(id);""")
        for de, df in d.dependents(e):
            w(f"    const {pv(de)} = this.store.{pv(de)}.countFor{camel(df.ref_stem)}(id);")
            w(f"    if ({pv(de)} > 0) {{")
            w(f"      throw new ConflictError(`{e.human} ${{id}} is still used by ${{{pv(de)}}} {de.plural.replace('_', ' ')}`);")
            w("    }")
        w("    this.repo.remove(id);")
        w("  }")
        refs = e.of("ref")
        w()
        if refs:
            w(f"  private checkLinks(item: {N}): void {{")
            for f in refs:
                t = d.get(f.ref)
                w(f"    if (!this.store.{pv(t)}.get(item.{fname(f)})) {{")
                w(f'      throw new NotFoundError("{t.human}", item.{fname(f)});')
                w("    }")
            w("  }")
        else:
            w(f"  private checkLinks(item: {N}): void {{")
            w(f"    void item; // a {e.human} doesn't point at other records")
            w("  }")
        for f in e.fields:
            fn, C = fname(f), camel(f.name)
            if f.kind == "enum":
                w(f"""
  set{C}(id: number, value: {etype(e, f)}): {N} {{
    return this.update(id, {{ {fn}: value }});
  }}""")
            elif f.kind == "bool":
                w(f"""
  toggle{C}(id: number): {N} {{
    return this.update(id, {{ {fn}: !this.get(id).{fn} }});
  }}""")
            elif f.kind == "int":
                w(f"""
  /** Add `delta` to the {f.human} (it can't go below zero). */
  adjust{C}(id: number, delta: number): {N} {{
    return this.update(id, {{ {fn}: this.get(id).{fn} + delta }});
  }}""")
            elif f.kind in ("float", "money"):
                w(f"""
  adjust{C}(id: number, delta: number): {N} {{
    return this.update(id, {{ {fn}: Math.round((this.get(id).{fn} + delta) * 100) / 100 }});
  }}""")
        w()
        w("  /** Totals and breakdowns over every " + e.human + ". */")
        w("  stats(): Record<string, unknown> {")
        w("    return {")
        w("      count: this.repo.count(),")
        for f in e.fields:
            fn, C = fname(f), camel(f.name)
            if f.kind in NUMERIC:
                w(f"      total{C}: this.repo.total{C}(),")
                w(f"      average{C}: this.repo.average{C}(),")
            elif f.kind == "enum":
                w(f"      by{C}: this.repo.countBy{C}(),")
            elif f.kind == "bool":
                w(f"      {fn}: this.repo.where{C}(true).length,")
        w("    };")
        w("  }")
        w("}")
    w()
    w("/** The whole kit: storage plus one service per record type. */")
    w("export class Services {")
    w("  readonly store = new Store();")
    for e in d.entities:
        w(f"  readonly {pv(e)} = new {e.name}Service(this.store);")
    w()
    w("  /** Fill every store with `count` sample records. */")
    w("  seed(count = 3): void {")
    w("    for (let i = 1; i <= count; i += 1) {")
    for e in d.entities:
        w(f"      this.{pv(e)}.create(sample{e.name}(i));")
    w("    }")
    w("  }")
    w()
    w("  summary(): Record<string, unknown> {")
    w("    return {")
    for e in d.entities:
        w(f"      {pv(e)}: this.{pv(e)}.stats(),")
    w("    };")
    w("  }")
    w("}")
    for e in d.entities:
        w()
        w(f"/** Valid data for a new {e.human} (links point at seeded records). */")
        w(f"export function sample{e.name}(i: number): Record<string, unknown> {{")
        w("  return {")
        for f in e.fields:
            w(f"    {fname(f)}: {sample(e, f)},")
        w("  };")
        w("}")
    return w.text()


# --------------------------------------------------------------------------- queries
def queries_ts(d):
    w = W()
    w("/**")
    w(f" * Query layer for the {d.title} kit: filters, search, sorting and paging driven by")
    w(" * plain string parameters (as they arrive from a URL or a form), plus field descriptions.")
    w(" */")
    w()
    names = {"ValidationError", "checkChoice", "checkDate"}
    for e in d.entities:
        names.add(e.name)
        for f in e.fields:
            if f.kind == "enum":
                names.add(values_const(e, f))
            if f.kind != "bool":
                names.add(f"compare{e.name}By{camel(f.name)}")
    w("import {")
    for n in sorted(names):
        w(f"  {n},")
    w('} from "./models";')
    w('import { Store } from "./services";')
    w("""
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
};""")
    for e in d.entities:
        N, P = e.name, pv(e)
        w()
        w(f"const {e.snake.upper()}_COMPARERS: Record<string, (a: {N}, b: {N}) => number> = {{")
        w("  id: (a, b) => a.id - b.id,")
        for f in e.fields:
            if f.kind != "bool":
                w(f"  {fname(f)}: compare{N}By{camel(f.name)},")
        w("};")
        w()
        w(f"/** {e.plural.replace('_', ' ').capitalize()} matching the query parameters. */")
        w(f"export function query{e.plural_camel}(store: Store, query: Query): {N}[] {{")
        w(f"  let items = store.{P}.list();")
        w("  if (query.q !== undefined) {")
        w(f"    const hits = new Set(store.{P}.search(query.q).map((item) => item.id));")
        w("    items = items.filter((item) => hits.has(item.id));")
        w("  }")
        for f in e.fields:
            fn, C = fname(f), camel(f.name)
            if f.kind in TEXTUAL:
                w(f"  if (query.{fn} !== undefined) {{")
                w(f"    const wanted = query.{fn};")
                w(f"    items = items.filter((item) => item.{fn} === wanted);")
                w("  }")
            elif f.kind in NUMERIC:
                for side, op in (("min", ">="), ("max", "<=")):
                    w(f"  if (query.{side}{C} !== undefined) {{")
                    w(f'    const limit = numberParam(query, "{side}{C}");')
                    w(f"    items = items.filter((item) => item.{fn} {op} limit);")
                    w("  }")
            elif f.kind == "enum":
                w(f"  if (query.{fn} !== undefined) {{")
                w(f'    const wanted = checkChoice("{fn}", query.{fn}, {values_const(e, f)});')
                w(f"    items = items.filter((item) => item.{fn} === wanted);")
                w("  }")
            elif f.kind == "bool":
                w(f"  if (query.{fn} !== undefined) {{")
                w(f'    const wanted = flagParam(query, "{fn}");')
                w(f"    items = items.filter((item) => item.{fn} === wanted);")
                w("  }")
            elif f.kind == "date":
                for side, op in (("From", ">="), ("To", "<=")):
                    w(f"  if (query.{fn}{side} !== undefined) {{")
                    w(f'    const day = checkDate("{fn}{side}", query.{fn}{side});')
                    w(f"    items = items.filter((item) => item.{fn} {op} day);")
                    w("  }")
            elif f.kind == "ref":
                w(f"  if (query.{fn} !== undefined) {{")
                w(f'    const wanted = numberParam(query, "{fn}");')
                w(f"    items = items.filter((item) => item.{fn} === wanted);")
                w("  }")
        w(f"  return paginate(sortWith(items, query.sort, {e.snake.upper()}_COMPARERS), query);")
        w("}")
        w()
        w(f"/** What each {e.human} field holds and the rule it must follow. */")
        w(f"export function describe{N}(): FieldInfo[] {{")
        w("  return [")
        w('    { field: "id", kind: "int", rule: "assigned automatically" },')
        for f in e.fields:
            w(f'    {{ field: "{fname(f)}", kind: "{f.kind}", rule: RULES.{f.kind} }},')
        w("  ];")
        w("}")
    return w.text()


# -------------------------------------------------------------------------- selftest
BAD = {"str": '""', "text": '"x".repeat(3000)', "email": '"not-an-email"', "int": "-1",
       "float": "-1", "money": "-5", "bool": '"yes"', "date": '"2026-02-30"', "enum": '"nope"', "ref": "0"}


def selftest_ts(d):
    w = W()
    w(f"/** Self-test for the {d.title} kit: run `node dist/selftest.js` after `tsc -p .`. */")
    w()
    w('import { ValidationError } from "./models";')
    w("import {")
    w("  ConflictError,")
    w("  NotFoundError,")
    w("  Services,")
    for e in d.entities:
        w(f"  sample{e.name},")
    w('} from "./services";')
    w("import {")
    for e in d.entities:
        w(f"  describe{e.name},")
        w(f"  query{e.plural_camel},")
    w('} from "./queries";')
    w("""
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
}""")
    for e in d.entities:
        N, P, h = e.name, pv(e), e.human
        w()
        w(f"// {'-' * 76} {N}")
        w(f"""
test("{h}: create and get", () => {{
  const s = seeded();
  const item = s.{P}.create(sample{N}(10));
  assert(s.{P}.get(item.id) === item, "stored record differs");
  assert(s.{P}.list().length === 4, "list should have 4 records");
}});

test("{h}: missing record", () => {{
  throwsKind(() => seeded().{P}.get(9999), NotFoundError);
}});

test("{h}: unknown field", () => {{
  const data = sample{N}(11);
  data.noSuchField = 1;
  throwsField(() => seeded().{P}.create(data), "noSuchField");
}});

test("{h}: id can't be chosen", () => {{
  const data = sample{N}(11);
  data.id = 42;
  throwsField(() => seeded().{P}.create(data), "id");
}});""")
        for f in e.fields:
            fn = fname(f)
            w(f"""
test("{h}: rejects a bad {f.human}", () => {{
  const data = sample{N}(12);
  data.{fn} = {BAD[f.kind]};
  throwsField(() => seeded().{P}.create(data), "{fn}");
}});""")
        for f in e.of("ref"):
            w(f"""
test("{h}: {f.human} must exist", () => {{
  const data = sample{N}(13);
  data.{fname(f)} = 9999;
  throwsKind(() => seeded().{P}.create(data), NotFoundError);
}});""")
        for f in e.fields:
            fn, C = fname(f), camel(f.name)
            if f.kind == "enum":
                last = f.values[-1]
                w(f"""
test("{h}: set {f.human}", () => {{
  const s = seeded();
  assert(s.{P}.set{C}(1, "{last}").{fn} === "{last}", "value not changed");
  assert(s.store.{P}.countBy{C}()["{last}"] === s.store.{P}.with{C}("{last}").length, "counts differ");
}});""")
            elif f.kind == "bool":
                w(f"""
test("{h}: toggle {f.human}", () => {{
  const s = seeded();
  const before = s.{P}.get(1).{fn};
  assert(s.{P}.toggle{C}(1).{fn} === !before, "flag not flipped");
}});""")
            elif f.kind == "int":
                w(f"""
test("{h}: adjust {f.human}", () => {{
  const s = seeded();
  const before = s.{P}.get(1).{fn};
  assert(s.{P}.adjust{C}(1, 2).{fn} === before + 2, "not adjusted");
  throwsField(() => s.{P}.adjust{C}(1, -(before + 100)), "{fn}");
}});""")
            elif f.kind in ("float", "money"):
                w(f"""
test("{h}: adjust {f.human}", () => {{
  const s = seeded();
  const before = s.{P}.get(1).{fn};
  assert(Math.abs(s.{P}.adjust{C}(1, 1.5).{fn} - (before + 1.5)) < 0.01, "not adjusted");
}});""")
            elif f.kind in TEXTUAL:
                w(f"""
test("{h}: search {f.human}", () => {{
  const s = seeded();
  const target = s.{P}.get(2);
  assert(s.store.{P}.search{C}(target.{fn}.toUpperCase()).includes(target), "search missed it");
  assert(s.store.{P}.findBy{C}(target.{fn}).includes(target), "find missed it");
}});""")
            elif f.kind == "date":
                w(f"""
test("{h}: {f.human} ranges", () => {{
  const s = seeded();
  const day = s.{P}.get(2).{fn};
  const total = s.store.{P}.{fn}Before(day).length + s.store.{P}.{fn}On(day).length + s.store.{P}.{fn}After(day).length;
  assert(total === s.store.{P}.count(), "ranges don't cover every record");
}});""")
        w(f"""
test("{h}: delete an unused record", () => {{
  const s = seeded();
  const item = s.{P}.create(sample{N}(14));
  s.{P}.delete(item.id);
  throwsKind(() => s.{P}.get(item.id), NotFoundError);
}});""")
        if d.dependents(e):
            w(f"""
test("{h}: delete a record in use", () => {{
  throwsKind(() => seeded().{P}.delete(1), ConflictError);
}});""")
        w(f"""
test("{h}: stats and queries", () => {{
  const s = seeded();
  assert(s.{P}.stats().count === 3, "wrong count");
  const newest = query{e.plural_camel}(s.store, {{ sort: "-id", size: "1" }});
  assert(newest.length === 1 && newest[0].id === 3, "sort/page failed");
  throwsField(() => query{e.plural_camel}(s.store, {{ sort: "nope" }}), "sort");
  assert(describe{N}().length === {len(e.fields) + 1}, "field list incomplete");
}});""")
    w("""
console.log(`${passed} passed, ${failures.length} failed`);
for (const failure of failures) {
  console.log(`FAIL ${failure}`);
}
if (failures.length > 0) {
  throw new Error(`${failures.length} test(s) failed`);
}""")
    return w.text()


def render(d, name):
    typed = [
        ("src/models.ts", models_ts(d)),
        ("src/store.ts", store_ts(d)),
        ("src/services.ts", services_ts(d)),
        ("src/queries.ts", queries_ts(d)),
        ("src/selftest.ts", selftest_ts(d)),
    ]
    package = ('{\n  "name": "' + name + '",\n  "version": "0.1.0",\n  "private": true,\n'
               '  "scripts": {\n    "build": "tsc -p .",\n    "test": "node dist/selftest.js"\n  },\n'
               '  "devDependencies": {\n    "typescript": "^5.6.3"\n  }\n}\n')
    tsconfig = ('{\n  "compilerOptions": {\n    "target": "es2020",\n    "module": "commonjs",\n'
                '    "lib": ["es2020", "dom"],\n    "strict": true,\n    "outDir": "dist",\n'
                '    "rootDir": "src"\n  },\n  "include": ["src"]\n}\n')
    readme = (f"# {name}\n\n{d.title} kit in strict TypeScript (no runtime dependencies).\n\n"
              f"Records: {', '.join(e.name for e in d.entities)}.\n\n"
              "```bash\nnpm install\nnpx tsc -p .\nnode dist/selftest.js\n```\n")
    scaffold = [("package.json", package), ("tsconfig.json", tsconfig), ("README.md", readme),
                (".gitignore", "node_modules/\ndist/\n")]
    steps = [
        {"cmd": "npm install --no-audit --no-fund", "serve": False, "open": None, "wait": 45},
        {"cmd": "npx tsc -p .", "serve": False, "open": None, "wait": 20},
        {"cmd": "node dist/selftest.js", "serve": False, "open": None, "wait": 8},
    ]
    return typed, scaffold, steps
