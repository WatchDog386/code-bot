"""Python flavour: a standard-library-only service (models, repository, services,
HTTP API, unittest suite). Every typed file comes out as real, runnable code."""

from .schema import enum_type, NUMERIC, SORTABLE, TEXTUAL, camel

PY_TYPE = {"str": "str", "text": "str", "email": "str", "int": "int", "float": "float",
           "money": "float", "bool": "bool", "date": "str", "ref": "int"}
PY_DEFAULT = {"str": '""', "text": '""', "email": '""', "int": "0", "float": "0.0",
              "money": "0.0", "bool": "False", "date": '""', "ref": "0"}


def enum_name(e, f):
    return enum_type(e, f)


def ptype(e, f):
    return enum_name(e, f) if f.kind == "enum" else PY_TYPE[f.kind]


def check_call(e, f, var="value"):
    k = f.kind
    if k == "str":
        return f'check_text("{f.name}", {var})'
    if k == "text":
        return f'check_text("{f.name}", {var}, max_length=2000, required=False)'
    if k == "email":
        return f'check_email("{f.name}", {var})'
    if k == "int":
        return f'check_int("{f.name}", {var})'
    if k == "float":
        return f'check_number("{f.name}", {var})'
    if k == "money":
        return f'check_money("{f.name}", {var})'
    if k == "bool":
        return f'check_flag("{f.name}", {var})'
    if k == "date":
        return f'check_date("{f.name}", {var})'
    if k == "enum":
        return f'check_choice("{f.name}", {var}, {enum_name(e, f)})'
    return f'check_ref("{f.name}", {var})'


def sample_expr(e, f):
    """A Python expression (using `index`) giving a valid value."""
    k = f.kind
    if k == "str":
        return f'f"{e.human.capitalize()} {f.human} {{index}}"'
    if k == "text":
        return f'f"Notes about {e.human} {{index}}."'
    if k == "email":
        return f'f"{e.snake}{{index}}@example.com"'
    if k == "int":
        return "index + 1"
    if k == "float":
        return "round(1.5 * index + 0.25, 2)"
    if k == "money":
        return "round(10.0 * index + 0.99, 2)"
    if k == "bool":
        return "index % 2 == 1"
    if k == "date":
        return 'f"2026-{index % 12 + 1:02d}-{index % 28 + 1:02d}"'
    if k == "enum":
        return f"{f.values!r}[index % {len(f.values)}]"
    return f"(index - 1) % {SEED} + 1"


BAD = {"str": '""', "text": '"x" * 3000', "email": '"not-an-email"', "int": "-1",
       "float": "-1.0", "money": "-5.0", "bool": '"yes"', "date": '"2026-02-30"',
       "enum": '"nope"', "ref": "0"}
SEED = 3


class W:
    def __init__(self):
        self.lines = []

    def __call__(self, text="", indent=0):
        for line in text.split("\n") if text else [""]:
            self.lines.append(("    " * indent + line) if line else "")

    def text(self):
        return "\n".join(self.lines).rstrip() + "\n"


# --------------------------------------------------------------------------- models
def models(d, pkg):
    w = W()
    w(f'"""Domain models for the {d.title} service.\n\nEvery model is a dataclass with a\n'
      '`validate()` that checks and normalises its fields, plus `to_dict()` / `from_dict()`\n'
      'for the JSON API and `apply()` for partial updates.\n"""')
    w()
    w("from __future__ import annotations")
    w()
    w("import re")
    w("from dataclasses import dataclass, replace")
    w("from datetime import date")
    w("from enum import Enum")
    w("from typing import Any, Dict, FrozenSet, Optional, Tuple, Type")
    w()
    w('DATE_RE = re.compile(r"^\\d{4}-\\d{2}-\\d{2}$")')
    w('EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")')
    w("MAX_INT = 1_000_000_000")
    w()
    w()
    w("""class ValidationError(ValueError):
    \"\"\"A field holds a value the service can't accept.\"\"\"

    def __init__(self, field_name: str, message: str) -> None:
        super().__init__(f"{field_name}: {message}")
        self.field_name = field_name
        self.message = message


def check_text(name: str, value: Any, max_length: int = 120, required: bool = True) -> str:
    \"\"\"Trimmed text, not empty unless optional, and not too long.\"\"\"
    if not isinstance(value, str):
        raise ValidationError(name, "must be text")
    cleaned = value.strip()
    if required and not cleaned:
        raise ValidationError(name, "is required")
    if len(cleaned) > max_length:
        raise ValidationError(name, f"must be at most {max_length} characters")
    return cleaned


def check_email(name: str, value: Any) -> str:
    \"\"\"A plausible e-mail address, stored in lower case.\"\"\"
    text = check_text(name, value, max_length=254)
    if not EMAIL_RE.match(text):
        raise ValidationError(name, "must be an e-mail address")
    return text.lower()


def check_int(name: str, value: Any, minimum: int = 0, maximum: int = MAX_INT) -> int:
    \"\"\"A whole number inside [minimum, maximum].\"\"\"
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(name, "must be a whole number")
    if value < minimum:
        raise ValidationError(name, f"must be at least {minimum}")
    if value > maximum:
        raise ValidationError(name, f"must be at most {maximum}")
    return value


def check_number(name: str, value: Any, minimum: float = 0.0) -> float:
    \"\"\"Any number that isn't negative.\"\"\"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(name, "must be a number")
    if value < minimum:
        raise ValidationError(name, f"must be at least {minimum}")
    return float(value)


def check_money(name: str, value: Any) -> float:
    \"\"\"An amount of money, rounded to cents.\"\"\"
    return round(check_number(name, value), 2)


def check_flag(name: str, value: Any) -> bool:
    \"\"\"A real boolean (no "yes"/"no" strings).\"\"\"
    if not isinstance(value, bool):
        raise ValidationError(name, "must be true or false")
    return value


def check_date(name: str, value: Any) -> str:
    \"\"\"An ISO date (YYYY-MM-DD) that exists in the calendar.\"\"\"
    text = check_text(name, value, max_length=10)
    if not DATE_RE.match(text):
        raise ValidationError(name, "must look like YYYY-MM-DD")
    try:
        date.fromisoformat(text)
    except ValueError:
        raise ValidationError(name, "is not a real date") from None
    return text


def check_ref(name: str, value: Any) -> int:
    \"\"\"The id of another record (existence is checked by the services).\"\"\"
    return check_int(name, value, minimum=1)


def check_choice(name: str, value: Any, choices: Type[Enum]) -> Any:
    \"\"\"One of the values of an Enum.\"\"\"
    if isinstance(value, choices):
        return value
    try:
        return choices(value)
    except ValueError:
        allowed = ", ".join(member.value for member in choices)
        raise ValidationError(name, f"must be one of: {allowed}") from None


def unknown_fields(data: Dict[str, Any], known: FrozenSet[str]) -> Optional[str]:
    \"\"\"The first key in `data` that isn't a field, if any.\"\"\"
    extra = sorted(set(data) - known)
    return extra[0] if extra else None""")

    for e in d.entities:
        for f in e.of("enum"):
            w()
            w()
            w(f"class {enum_name(e, f)}(str, Enum):")
            w(f'    """Allowed values of {e.name}.{f.name}."""')
            w()
            for v in f.values:
                w(f'    {v.upper()} = "{v}"')
            w()
            w("    @property")
            w("    def label(self) -> str:")
            w('        """Human-friendly name, e.g. for a drop-down."""')
            w('        return self.value.replace("_", " ").capitalize()')
            w()
            w("    @classmethod")
            w(f"    def values(cls) -> Tuple[str, ...]:")
            w("        return tuple(member.value for member in cls)")

    for e in d.entities:
        up = e.snake.upper()
        w()
        w()
        w(f"# {'-' * 74} {e.name}")
        w(f"{up}_FIELDS: FrozenSet[str] = frozenset({{")
        w('    "id",')
        for f in e.fields:
            w(f'    "{f.name}",')
        w("})")
        sortable = [f.name for f in e.fields if f.kind in SORTABLE]
        w(f"{up}_SORTABLE: Tuple[str, ...] = ({', '.join(repr(s) for s in ['id'] + sortable)},)")
        w(f"{up}_REQUIRED: Tuple[str, ...] = (" +
          ", ".join(repr(f.name) for f in e.fields if f.kind in ("str", "email", "date", "ref")) + ",)")
        for f in e.fields:
            w()
            w()
            w(f"def validate_{e.snake}_{f.name}(value: Any) -> {ptype(e, f)}:")
            w(f'    """Check {e.name}.{f.name} ({f.kind})."""')
            w(f"    return {check_call(e, f)}")
        w()
        w()
        w("@dataclass")
        w(f"class {e.name}:")
        w(f'    """A {e.human} record."""')
        w()
        w("    id: int = 0")
        for f in e.fields:
            default = f"{enum_name(e, f)}.{f.values[0].upper()}" if f.kind == "enum" else PY_DEFAULT[f.kind]
            w(f"    {f.name}: {ptype(e, f)} = {default}")
        w()
        w(f'    def validate(self) -> "{e.name}":')
        w('        """Check every field and normalise the values in place."""')
        for f in e.fields:
            w(f"        self.{f.name} = validate_{e.snake}_{f.name}(self.{f.name})")
        w("        return self")
        w()
        w("    def to_dict(self) -> Dict[str, Any]:")
        w('        """Plain JSON-ready values."""')
        w("        return {")
        w('            "id": self.id,')
        for f in e.fields:
            val = f"self.{f.name}.value" if f.kind == "enum" else f"self.{f.name}"
            w(f'            "{f.name}": {val},')
        w("        }")
        w()
        w("    @classmethod")
        w(f'    def from_dict(cls, data: Dict[str, Any]) -> "{e.name}":')
        w('        """Build an (unvalidated) record from JSON values."""')
        w(f"        extra = unknown_fields(data, {up}_FIELDS)")
        w("        if extra:")
        w('            raise ValidationError(extra, "is not a known field")')
        w('        item = cls(id=check_int("id", data.get("id", 0)))')
        for f in e.fields:
            w(f'        if "{f.name}" in data:')
            w(f'            item.{f.name} = data["{f.name}"]')
        w("        return item")
        w()
        w(f'    def apply(self, changes: Dict[str, Any]) -> "{e.name}":')
        w('        """A validated copy with `changes` applied; the id never changes."""')
        w('        if "id" in changes:')
        w('            raise ValidationError("id", "cannot be changed")')
        w(f"        extra = unknown_fields(changes, {up}_FIELDS)")
        w("        if extra:")
        w('            raise ValidationError(extra, "is not a known field")')
        w("        return replace(self, **changes).validate()")
        w()
        w("    def summary(self) -> str:")
        w('        """One line for logs and lists."""')
        lf = e.label_field
        w(f'        return f"{e.name} #{{self.id}}' + (f': {{self.{lf.name}}}"' if lf else '"'))
        w()
        w("    def missing(self) -> Tuple[str, ...]:")
        w('        """Required fields that are still empty."""')
        w(f"        return tuple(name for name in {up}_REQUIRED if not getattr(self, name))")
    return w.text()


# ----------------------------------------------------------------------- repository
def repository(d, pkg):
    w = W()
    w(f'"""Storage for the {d.title} service: one thread-safe in-memory repository per\n'
      'model, with the lookups the services and the API need, and JSON / CSV import-export.\n"""')
    w()
    w("from __future__ import annotations")
    w()
    w("import csv")
    w("import io")
    w("import json")
    w("import threading")
    w("from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar")
    w()
    names = []
    for e in d.entities:
        names.append(e.name)
        names += [enum_name(e, f) for f in e.of("enum")]
    w("from .models import (")
    for n in sorted(names):
        w(f"    {n},")
    w(")")
    w()
    w('T = TypeVar("T")')
    w()
    w()
    w("""class Repository(Generic[T]):
    \"\"\"Records kept in memory, keyed by id. Subclasses set `model`.\"\"\"

    model: Any = None
    entity_name = "record"

    def __init__(self) -> None:
        self._items: Dict[int, T] = {}
        self._next_id = 1
        self._lock = threading.RLock()

    def add(self, item: T) -> T:
        \"\"\"Store a new record and give it the next id.\"\"\"
        with self._lock:
            item.id = self._next_id  # type: ignore[attr-defined]
            self._next_id += 1
            self._items[item.id] = item  # type: ignore[attr-defined]
            return item

    def get(self, item_id: int) -> Optional[T]:
        with self._lock:
            return self._items.get(item_id)

    def list(self) -> List[T]:
        \"\"\"Every record, oldest first.\"\"\"
        with self._lock:
            return [self._items[key] for key in sorted(self._items)]

    def save(self, item: T) -> T:
        \"\"\"Replace an existing record.\"\"\"
        with self._lock:
            key = item.id  # type: ignore[attr-defined]
            if key not in self._items:
                raise KeyError(key)
            self._items[key] = item
            return item

    def remove(self, item_id: int) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None

    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._next_id = 1

    def where(self, keep: Callable[[T], bool]) -> List[T]:
        \"\"\"Records for which `keep(record)` is true.\"\"\"
        return [item for item in self.list() if keep(item)]

    def first(self, keep: Callable[[T], bool]) -> Optional[T]:
        for item in self.list():
            if keep(item):
                return item
        return None

    def page(self, number: int = 1, size: int = 20) -> List[T]:
        \"\"\"One page of records (pages start at 1).\"\"\"
        start = max(0, (number - 1) * size)
        return self.list()[start:start + size]

    def sorted_by(self, field_name: str, reverse: bool = False) -> List[T]:
        return sorted(self.list(), key=lambda item: getattr(item, field_name), reverse=reverse)

    def to_json(self) -> str:
        return json.dumps([item.to_dict() for item in self.list()], indent=2)  # type: ignore[attr-defined]

    def load_json(self, text: str) -> int:
        \"\"\"Load records exported with `to_json()`; returns how many.\"\"\"
        rows = json.loads(text)
        with self._lock:
            for row in rows:
                item = self.model.from_dict(row).validate()
                self._items[item.id] = item
                self._next_id = max(self._next_id, item.id + 1)
        return len(rows)

    def to_csv(self) -> str:
        \"\"\"Every record as CSV with a header row.\"\"\"
        names = ["id"] + [name for name in self.model.__dataclass_fields__ if name != "id"]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=names, lineterminator="\\n")
        writer.writeheader()
        for item in self.list():
            writer.writerow(item.to_dict())  # type: ignore[attr-defined]
        return buffer.getvalue()""")
    for e in d.entities:
        cls = e.name
        w()
        w()
        w(f"class {cls}Repository(Repository[{cls}]):")
        w(f'    """All {e.plural.replace("_", " ")}, with the lookups the services need."""')
        w()
        w(f"    model = {cls}")
        w(f'    entity_name = "{e.snake}"')
        for f in e.fields:
            n = f.name
            if f.kind in TEXTUAL:
                w()
                w(f"    def find_by_{n}(self, value: str) -> List[{cls}]:")
                w(f'        """Records whose {f.human} is exactly `value`."""')
                w(f"        return self.where(lambda item: item.{n} == value)")
                w()
                w(f"    def search_{n}(self, text: str) -> List[{cls}]:")
                w(f'        """Records whose {f.human} contains `text` (any case)."""')
                w("        needle = text.strip().lower()")
                w(f"        return self.where(lambda item: needle in item.{n}.lower())")
            elif f.kind in NUMERIC:
                w()
                w(f"    def between_{n}(self, low: float, high: float) -> List[{cls}]:")
                w(f'        """Records whose {f.human} is within [low, high]."""')
                w(f"        return self.where(lambda item: low <= item.{n} <= high)")
                w()
                w(f"    def total_{n}(self) -> float:")
                w(f"        return sum(item.{n} for item in self.list())")
                w()
                w(f"    def average_{n}(self) -> float:")
                w("        items = self.list()")
                w(f"        return sum(item.{n} for item in items) / len(items) if items else 0.0")
                w()
                w(f"    def max_{n}(self) -> Optional[{cls}]:")
                w(f'        """The record with the highest {f.human}."""')
                w("        items = self.list()")
                w(f"        return max(items, key=lambda item: item.{n}) if items else None")
            elif f.kind == "enum":
                en = enum_name(e, f)
                w()
                w(f"    def with_{n}(self, value: Any) -> List[{cls}]:")
                w(f"        wanted = {en}(value)")
                w(f"        return self.where(lambda item: item.{n} == wanted)")
                w()
                w(f"    def count_by_{n}(self) -> Dict[str, int]:")
                w(f'        """How many records have each {f.human}."""')
                w(f"        counts = {{member.value: 0 for member in {en}}}")
                w("        for item in self.list():")
                w(f"            counts[{en}(item.{n}).value] += 1")
                w("        return counts")
            elif f.kind == "bool":
                w()
                w(f"    def where_{n}(self, flag: bool = True) -> List[{cls}]:")
                w(f"        return self.where(lambda item: item.{n} is flag)")
            elif f.kind == "date":
                w()
                w(f"    def {n}_before(self, day: str) -> List[{cls}]:")
                w(f"        return self.where(lambda item: item.{n} < day)")
                w()
                w(f"    def {n}_after(self, day: str) -> List[{cls}]:")
                w(f"        return self.where(lambda item: item.{n} > day)")
                w()
                w(f"    def {n}_on(self, day: str) -> List[{cls}]:")
                w(f"        return self.where(lambda item: item.{n} == day)")
            elif f.kind == "ref":
                w()
                w(f"    def for_{f.ref_stem}(self, {n}: int) -> List[{cls}]:")
                w(f'        """Records linked to {f.ref_stem.replace("_", " ")} `{n}`."""')
                w(f"        return self.where(lambda item: item.{n} == {n})")
                w()
                w(f"    def count_for_{f.ref_stem}(self, {n}: int) -> int:")
                w(f"        return len(self.for_{f.ref_stem}({n}))")
        text_fields = e.of("str", "text", "email")
        w()
        w(f"    def search(self, text: str) -> List[{cls}]:")
        w('        """Records where any text field contains `text`."""')
        w("        needle = text.strip().lower()")
        if text_fields:
            w("        return self.where(lambda item: any(needle in value.lower() for value in (")
            for f in text_fields:
                w(f"            item.{f.name},")
            w("        )))")
        else:
            w("        return self.where(lambda item: needle == str(item.id))")
    return w.text()


# ------------------------------------------------------------------------- services
def services(d, pkg):
    w = W()
    w(f'"""Business rules for the {d.title} service: validation, links between records\n'
      '(a record can\'t point at something that doesn\'t exist, and can\'t be deleted while\n'
      'others still point at it), small domain operations and statistics.\n"""')
    w()
    w("from __future__ import annotations")
    w()
    w("from enum import Enum")
    w("from typing import Any, Dict, List, Optional")
    w()
    names = ["ValidationError"]
    for e in d.entities:
        names += [e.name, f"{e.snake.upper()}_FIELDS"]
    w("from .models import (")
    for n in sorted(names):
        w(f"    {n},")
    w(")")
    w("from .repository import (")
    for e in d.entities:
        w(f"    {e.name}Repository,")
    w(")")
    w()
    w()
    w("""class NotFound(LookupError):
    \"\"\"No record with that id.\"\"\"

    def __init__(self, entity: str, item_id: int) -> None:
        super().__init__(f"{entity} {item_id} not found")
        self.entity = entity
        self.item_id = item_id


class Conflict(ValueError):
    \"\"\"The change would break a link between records.\"\"\"


def plain(value: Any) -> str:
    \"\"\"A value as the text a query string would carry.\"\"\"
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class Store:
    \"\"\"Every repository of the service.\"\"\"

    def __init__(self) -> None:""")
    for e in d.entities:
        w(f"        self.{e.plural} = {e.name}Repository()")
    w()
    w("    def counts(self) -> Dict[str, int]:")
    w("        return {")
    for e in d.entities:
        w(f'            "{e.plural}": self.{e.plural}.count(),')
    w("        }")
    for e in d.entities:
        cls, up = e.name, e.snake.upper()
        w()
        w()
        w(f"class {cls}Service:")
        w(f'    """Create, change and remove {e.plural.replace("_", " ")}."""')
        w()
        w("    def __init__(self, store: Store) -> None:")
        w("        self.store = store")
        w(f"        self.repo = store.{e.plural}")
        w()
        w(f"    def create(self, data: Dict[str, Any]) -> {cls}:")
        w(f'        """Validate and store a new {e.human}."""')
        w('        if "id" in data:')
        w('            raise ValidationError("id", "is assigned automatically")')
        w(f"        item = {cls}.from_dict(data).validate()")
        w("        self._check_links(item)")
        w("        return self.repo.add(item)")
        w()
        w(f"    def get(self, item_id: int) -> {cls}:")
        w("        item = self.repo.get(item_id)")
        w("        if item is None:")
        w(f'            raise NotFound("{e.human}", item_id)')
        w("        return item")
        w()
        w(f"    def list(self, **filters: Any) -> List[{cls}]:")
        w('        """Records whose fields equal the given values (as query-string text)."""')
        w("        items = self.repo.list()")
        w("        for key, value in filters.items():")
        w(f"            if key not in {up}_FIELDS:")
        w('                raise ValidationError(key, "is not a field you can filter on")')
        w("            items = [item for item in items if plain(getattr(item, key)) == plain(value)]")
        w("        return items")
        w()
        w(f"    def update(self, item_id: int, changes: Dict[str, Any]) -> {cls}:")
        w(f'        """Change some fields of a {e.human}."""')
        w("        updated = self.get(item_id).apply(changes)")
        w("        self._check_links(updated)")
        w("        return self.repo.save(updated)")
        w()
        w("    def delete(self, item_id: int) -> None:")
        w(f'        """Remove a {e.human} nobody points at any more."""')
        w("        self.get(item_id)")
        for de, df in d.dependents(e):
            w(f"        if self.store.{de.plural}.count_for_{df.ref_stem}(item_id):")
            w(f'            raise Conflict(f"{e.human} {{item_id}} is still used by {de.plural.replace("_", " ")}")')
        w("        self.repo.remove(item_id)")
        w()
        w(f"    def _check_links(self, item: {cls}) -> None:")
        refs = e.of("ref")
        if not refs:
            w(f'        """{cls} doesn\'t point at other records."""')
        for f in refs:
            target = d.get(f.ref)
            w(f"        if self.store.{target.plural}.get(item.{f.name}) is None:")
            w(f'            raise NotFound("{target.human}", item.{f.name})')
        if not refs:
            w("        return None")
        for f in e.fields:
            if f.kind == "enum":
                w()
                w(f"    def set_{f.name}(self, item_id: int, value: Any) -> {cls}:")
                w(f'        """Move a {e.human} to another {f.human}."""')
                w(f'        return self.update(item_id, {{"{f.name}": value}})')
            elif f.kind == "bool":
                w()
                w(f"    def toggle_{f.name}(self, item_id: int) -> {cls}:")
                w(f"        item = self.get(item_id)")
                w(f'        return self.update(item_id, {{"{f.name}": not item.{f.name}}})')
            elif f.kind == "int":
                w()
                w(f"    def adjust_{f.name}(self, item_id: int, delta: int) -> {cls}:")
                w(f'        """Add `delta` to the {f.human} (it can\'t go below zero)."""')
                w(f"        item = self.get(item_id)")
                w(f'        return self.update(item_id, {{"{f.name}": item.{f.name} + delta}})')
            elif f.kind in ("float", "money"):
                w()
                w(f"    def adjust_{f.name}(self, item_id: int, delta: float) -> {cls}:")
                w(f"        item = self.get(item_id)")
                w(f'        return self.update(item_id, {{"{f.name}": round(item.{f.name} + delta, 2)}})')
        w()
        w("    def stats(self) -> Dict[str, Any]:")
        w(f'        """Totals and breakdowns over every {e.human}."""')
        w("        return {")
        w('            "count": self.repo.count(),')
        for f in e.fields:
            if f.kind in NUMERIC:
                w(f'            "total_{f.name}": round(self.repo.total_{f.name}(), 2),')
                w(f'            "average_{f.name}": round(self.repo.average_{f.name}(), 2),')
            elif f.kind == "enum":
                w(f'            "by_{f.name}": self.repo.count_by_{f.name}(),')
            elif f.kind == "bool":
                w(f'            "{f.name}": len(self.repo.where_{f.name}(True)),')
        w("        }")
    w()
    w()
    w("class Services:")
    w('    """The whole service: storage plus one service object per model."""')
    w()
    w("    def __init__(self, store: Optional[Store] = None) -> None:")
    w("        self.store = store or Store()")
    for e in d.entities:
        w(f"        self.{e.plural} = {e.name}Service(self.store)")
    w()
    w(f"    def seed(self, count: int = {SEED}) -> None:")
    w('        """Fill every repository with `count` sample records."""')
    w("        for index in range(1, count + 1):")
    for e in d.entities:
        w(f"            self.{e.plural}.create(sample_{e.snake}(index))")
    w()
    w("    def summary(self) -> Dict[str, Any]:")
    w("        return {")
    for e in d.entities:
        w(f'            "{e.plural}": self.{e.plural}.stats(),')
    w("        }")
    for e in d.entities:
        w()
        w()
        w(f"def sample_{e.snake}(index: int = 1) -> Dict[str, Any]:")
        w(f'    """Valid data for a new {e.human} (refs point at seeded records)."""')
        w("    return {")
        for f in e.fields:
            w(f'        "{f.name}": {sample_expr(e, f)},')
        w("    }")
    return w.text()


# ------------------------------------------------------------------------------ api
def api(d, pkg):
    w = W()
    w(f'"""HTTP API for the {d.title} service (standard library only).\n\n'
      f'Run it with   python -m {pkg}.api   and open http://127.0.0.1:8000/health\n\n'
      'Every collection supports GET (list, with filters, ?q= search, ?sort=, ?page=&size=),\n'
      'POST, GET /<id>, PATCH /<id>, DELETE /<id> and GET /stats.\n"""')
    w()
    w("from __future__ import annotations")
    w()
    w("import json")
    w("from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer")
    w("from typing import Any, Callable, Dict, List, Optional, Tuple")
    w("from urllib.parse import parse_qs, urlparse")
    w()
    names = ["ValidationError", "check_choice", "check_date"]
    for e in d.entities:
        names.append(f"{e.snake.upper()}_SORTABLE")
        names += [enum_name(e, f) for f in e.of("enum")]
    w("from .models import (")
    for n in sorted(names):
        w(f"    {n},")
    w(")")
    w("from .services import Conflict, NotFound, Services")
    w()
    w("Response = Tuple[int, Any]")
    w("Query = Dict[str, str]")
    w()
    w()
    w("""def query_int(query: Query, name: str, default: int = 0) -> int:
    raw = query.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(name, "must be a whole number") from None


def query_number(query: Query, name: str) -> float:
    try:
        return float(query[name])
    except ValueError:
        raise ValidationError(name, "must be a number") from None


def query_flag(query: Query, name: str) -> bool:
    raw = query[name].lower()
    if raw in ("1", "true", "yes"):
        return True
    if raw in ("0", "false", "no"):
        return False
    raise ValidationError(name, "must be true or false")


def paginate(items: List[Any], query: Query) -> List[Dict[str, Any]]:
    page = max(1, query_int(query, "page", 1))
    size = min(200, max(1, query_int(query, "size", 50)))
    start = (page - 1) * size
    return [item.to_dict() for item in items[start:start + size]]


def sort_items(items: List[Any], query: Query, allowed: Tuple[str, ...]) -> List[Any]:
    key = query.get("sort")
    if not key:
        return items
    reverse = key.startswith("-")
    key = key.lstrip("-")
    if key not in allowed:
        raise ValidationError("sort", "can't sort on " + key)
    return sorted(items, key=lambda item: getattr(item, key), reverse=reverse)


class Api:
    \"\"\"Maps HTTP requests onto the services and returns (status, payload).\"\"\"

    def __init__(self, services: Optional[Services] = None) -> None:
        self.services = services or Services()
        self.routes: Dict[str, Callable[[str, Optional[int], Query, Dict[str, Any]], Response]] = {""")
    for e in d.entities:
        w(f'            "{e.path}": self.{e.plural},')
    w("""        }

    def handle(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Response:
        \"\"\"Answer one request.\"\"\"
        parsed = urlparse(path)
        parts = [part for part in parsed.path.split("/") if part]
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        if parts == ["health"]:
            return 200, {"status": "ok"}
        if parts == ["summary"]:
            return 200, self.services.summary()
        if parts == []:
            return 200, {"collections": sorted(self.routes)}
        if parts[0] not in self.routes or len(parts) > 2:
            return 404, {"error": "unknown resource"}
        item_id: Optional[int] = None
        if len(parts) == 2:
            if parts[1] == "stats":
                method = "STATS"
            elif parts[1].isdigit():
                item_id = int(parts[1])
            else:
                return 404, {"error": "unknown resource"}
        try:
            return self.routes[parts[0]](method, item_id, query, body or {})
        except ValidationError as exc:
            return 400, {"error": str(exc), "field": exc.field_name}
        except NotFound as exc:
            return 404, {"error": str(exc)}
        except Conflict as exc:
            return 409, {"error": str(exc)}""")
    for e in d.entities:
        up = e.snake.upper()
        w()
        w(f"    def {e.plural}(self, method: str, item_id: Optional[int], query: Query, body: Dict[str, Any]) -> Response:")
        w(f"        service = self.services.{e.plural}")
        w('        if method == "STATS":')
        w("            return 200, service.stats()")
        w("        if item_id is None:")
        w('            if method == "GET":')
        w(f"                return 200, self.list_{e.plural}(query)")
        w('            if method == "POST":')
        w("                return 201, service.create(body).to_dict()")
        w('            return 405, {"error": "method not allowed"}')
        w('        if method == "GET":')
        w("            return 200, service.get(item_id).to_dict()")
        w('        if method in ("PATCH", "PUT"):')
        w("            return 200, service.update(item_id, body).to_dict()")
        w('        if method == "DELETE":')
        w("            service.delete(item_id)")
        w("            return 204, None")
        w('        return 405, {"error": "method not allowed"}')
        w()
        w(f"    def list_{e.plural}(self, query: Query) -> List[Dict[str, Any]]:")
        w(f'        """{e.plural.replace("_", " ").capitalize()} matching the query-string filters."""')
        w(f"        repo = self.services.store.{e.plural}")
        w("        items = repo.list()")
        w('        if "q" in query:')
        w('            hits = {item.id for item in repo.search(query["q"])}')
        w("            items = [item for item in items if item.id in hits]")
        for f in e.fields:
            n = f.name
            if f.kind in TEXTUAL:
                w(f'        if "{n}" in query:')
                w(f'            items = [item for item in items if item.{n} == query["{n}"]]')
            elif f.kind in NUMERIC:
                for side, op in (("min", ">="), ("max", "<=")):
                    w(f'        if "{side}_{n}" in query:')
                    w(f'            limit = query_number(query, "{side}_{n}")')
                    w(f"            items = [item for item in items if item.{n} {op} limit]")
            elif f.kind == "enum":
                w(f'        if "{n}" in query:')
                w(f'            wanted = check_choice("{n}", query["{n}"], {enum_name(e, f)})')
                w(f"            items = [item for item in items if item.{n} == wanted]")
            elif f.kind == "bool":
                w(f'        if "{n}" in query:')
                w(f'            flag = query_flag(query, "{n}")')
                w(f"            items = [item for item in items if item.{n} is flag]")
            elif f.kind == "date":
                for side, op in (("from", ">="), ("to", "<=")):
                    w(f'        if "{n}_{side}" in query:')
                    w(f'            day = check_date("{n}_{side}", query["{n}_{side}"])')
                    w(f"            items = [item for item in items if item.{n} {op} day]")
            elif f.kind == "ref":
                w(f'        if "{n}" in query:')
                w(f'            wanted_id = query_int(query, "{n}")')
                w(f"            items = [item for item in items if item.{n} == wanted_id]")
        w(f"        items = sort_items(items, query, {up}_SORTABLE)")
        w("        return paginate(items, query)")
    w(f'''

class Handler(BaseHTTPRequestHandler):
    """Turns HTTP requests into `Api.handle` calls."""

    api = Api()

    def _respond(self, status: int, payload: Any) -> None:
        data = b"" if payload is None else json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self, method: str) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = None
        if length:
            try:
                body = json.loads(self.rfile.read(length))
            except ValueError:
                self._respond(400, {{"error": "invalid JSON"}})
                return
        status, payload = self.api.handle(method, self.path, body)
        self._respond(status, payload)

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    def do_PATCH(self) -> None:  # noqa: N802
        self._dispatch("PATCH")

    def do_PUT(self) -> None:  # noqa: N802
        self._dispatch("PUT")

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch("DELETE")


def main(port: int = 8000) -> None:
    """Seed some sample data and serve until Ctrl+C."""
    api = Api()
    api.services.seed()
    Handler.api = api
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"{d.title} API on http://127.0.0.1:{{port}}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()''')
    return w.text()


# ---------------------------------------------------------------------------- tests
def tests(d, pkg):
    w = W()
    w(f'"""Tests for the {d.title} service (run: python -m unittest discover -s tests -t .)."""')
    w()
    w("import unittest")
    w()
    w(f"from {pkg}.api import Api")
    w(f"from {pkg}.models import ValidationError")
    w(f"from {pkg}.repository import (")
    for e in d.entities:
        w(f"    {e.name}Repository,")
    w(")")
    w(f"from {pkg}.services import (")
    w("    Conflict,")
    w("    NotFound,")
    w("    Services,")
    for e in d.entities:
        w(f"    sample_{e.snake},")
    w(")")
    for e in d.entities:
        svc = f"self.services.{e.plural}"
        lf = e.label_field
        w()
        w()
        w(f"class {e.name}Tests(unittest.TestCase):")
        w(f'    """{e.name}: validation, links, operations, storage and the API."""')
        w()
        w("    def setUp(self) -> None:")
        w("        self.services = Services()")
        w("        self.services.seed()")
        w(f"        self.service = {svc}")
        w(f"        self.repo = self.services.store.{e.plural}")
        w()
        w("    def test_create_and_get(self) -> None:")
        w(f"        item = self.service.create(sample_{e.snake}(10))")
        w("        self.assertGreater(item.id, 0)")
        w("        self.assertEqual(self.service.get(item.id), item)")
        w()
        w("    def test_seeded_records_are_listed(self) -> None:")
        w(f"        self.assertEqual(len(self.service.list()), {SEED})")
        w()
        w("    def test_missing_record_raises(self) -> None:")
        w("        with self.assertRaises(NotFound):")
        w("            self.service.get(9999)")
        w()
        w("    def test_unknown_field_is_rejected(self) -> None:")
        w(f"        data = sample_{e.snake}(11)")
        w('        data["no_such_field"] = 1')
        w("        with self.assertRaises(ValidationError):")
        w("            self.service.create(data)")
        w()
        w("    def test_id_cannot_be_chosen(self) -> None:")
        w(f"        data = sample_{e.snake}(11)")
        w('        data["id"] = 42')
        w("        with self.assertRaises(ValidationError):")
        w("            self.service.create(data)")
        for f in e.fields:
            w()
            w(f"    def test_rejects_bad_{f.name}(self) -> None:")
            w(f"        data = sample_{e.snake}(12)")
            w(f'        data["{f.name}"] = {BAD[f.kind]}')
            w("        with self.assertRaises(ValidationError) as caught:")
            w("            self.service.create(data)")
            w(f'        self.assertEqual(caught.exception.field_name, "{f.name}")')
        for f in e.of("ref"):
            w()
            w(f"    def test_{f.name}_must_exist(self) -> None:")
            w(f"        data = sample_{e.snake}(13)")
            w(f'        data["{f.name}"] = 9999')
            w("        with self.assertRaises(NotFound):")
            w("            self.service.create(data)")
        for f in e.fields:
            if f.kind == "enum":
                w()
                w(f"    def test_set_{f.name}(self) -> None:")
                w(f'        item = self.service.set_{f.name}(1, "{f.values[-1]}")')
                w(f'        self.assertEqual(item.{f.name}.value, "{f.values[-1]}")')
                w(f'        self.assertEqual(self.repo.count_by_{f.name}()["{f.values[-1]}"], '
                  f'len(self.repo.with_{f.name}("{f.values[-1]}")))')
            elif f.kind == "bool":
                w()
                w(f"    def test_toggle_{f.name}(self) -> None:")
                w(f"        before = self.service.get(1).{f.name}")
                w(f"        self.assertEqual(self.service.toggle_{f.name}(1).{f.name}, not before)")
            elif f.kind == "int":
                w()
                w(f"    def test_adjust_{f.name}(self) -> None:")
                w(f"        before = self.service.get(1).{f.name}")
                w(f"        self.assertEqual(self.service.adjust_{f.name}(1, 2).{f.name}, before + 2)")
                w("        with self.assertRaises(ValidationError):")
                w(f"            self.service.adjust_{f.name}(1, -(before + 100))")
            elif f.kind in ("float", "money"):
                w()
                w(f"    def test_adjust_{f.name}(self) -> None:")
                w(f"        before = self.service.get(1).{f.name}")
                w(f"        self.assertAlmostEqual(self.service.adjust_{f.name}(1, 1.5).{f.name}, before + 1.5, places=2)")
            elif f.kind in TEXTUAL:
                w()
                w(f"    def test_search_{f.name}(self) -> None:")
                w(f"        target = self.service.get(2).{f.name}")
                w(f"        self.assertIn(self.service.get(2), self.repo.search_{f.name}(target.upper()))")
                w(f"        self.assertEqual(len(self.repo.find_by_{f.name}(target)), "
                  f"len([i for i in self.repo.list() if i.{f.name} == target]))")
            elif f.kind == "date":
                w()
                w(f"    def test_{f.name}_ranges(self) -> None:")
                w(f"        day = self.service.get(2).{f.name}")
                w(f"        total = len(self.repo.{f.name}_before(day)) + len(self.repo.{f.name}_on(day)) + "
                  f"len(self.repo.{f.name}_after(day))")
                w(f"        self.assertEqual(total, self.repo.count())")
        if e.label_field:
            lf = e.label_field
            w()
            w("    def test_update_changes_only_given_fields(self) -> None:")
            w("        before = self.service.get(1)")
            w(f'        new_value = sample_{e.snake}(20)["{lf.name}"]')
            w(f'        after = self.service.update(1, {{"{lf.name}": new_value}})')
            w(f"        self.assertEqual(after.{lf.name}, new_value)")
            w("        self.assertEqual(after.id, before.id)")
        w()
        w("    def test_delete_unused_record(self) -> None:")
        w(f"        item = self.service.create(sample_{e.snake}(14))")
        w("        self.service.delete(item.id)")
        w("        with self.assertRaises(NotFound):")
        w("            self.service.get(item.id)")
        if d.dependents(e):
            w()
            w("    def test_delete_record_in_use_conflicts(self) -> None:")
            w("        with self.assertRaises(Conflict):")
            w("            self.service.delete(1)")
        w()
        w("    def test_stats_count(self) -> None:")
        w('        self.assertEqual(self.service.stats()["count"], self.repo.count())')
        w()
        w("    def test_json_round_trip(self) -> None:")
        w(f"        copy = {e.name}Repository()")
        w(f"        self.assertEqual(copy.load_json(self.repo.to_json()), {SEED})")
        w("        self.assertEqual(copy.list(), self.repo.list())")
        w("        self.assertEqual(copy.add(copy.model()).id, " + f"{SEED + 1})")
        w()
        w("    def test_csv_export(self) -> None:")
        w("        lines = self.repo.to_csv().splitlines()")
        w('        self.assertTrue(lines[0].startswith("id,"))')
        w(f"        self.assertEqual(len(lines), {SEED + 1})")
        w()
        w("    def test_api_round_trip(self) -> None:")
        w("        api = Api(self.services)")
        w(f'        status, body = api.handle("POST", "/{e.path}", sample_{e.snake}(15))')
        w("        self.assertEqual(status, 201)")
        w(f'        status, fetched = api.handle("GET", f"/{e.path}/{{body[\'id\']}}")')
        w("        self.assertEqual((status, fetched), (200, body))")
        w(f'        status, listed = api.handle("GET", "/{e.path}?sort=-id&size=1")')
        w('        self.assertEqual(listed[0]["id"], body["id"])')
        w(f'        status, _ = api.handle("GET", "/{e.path}/stats")')
        w("        self.assertEqual(status, 200)")
        w(f'        status, _ = api.handle("DELETE", f"/{e.path}/{{body[\'id\']}}")')
        w("        self.assertEqual(status, 204)")
        w(f'        self.assertEqual(api.handle("GET", f"/{e.path}/{{body[\'id\']}}")[0], 404)')
        w()
        w("    def test_api_rejects_bad_input(self) -> None:")
        w("        api = Api(self.services)")
        w(f'        status, body = api.handle("POST", "/{e.path}", {{"no_such_field": 1}})')
        w("        self.assertEqual(status, 400)")
        w(f'        self.assertEqual(api.handle("GET", "/{e.path}?sort=nope")[0], 400)')
    w()
    w()
    w('if __name__ == "__main__":')
    w("    unittest.main()")
    return w.text()


def render(d, name):
    pkg = d.key.replace("-", "_") + "_service"
    typed = [
        (f"{pkg}/models.py", models(d, pkg)),
        (f"{pkg}/repository.py", repository(d, pkg)),
        (f"{pkg}/services.py", services(d, pkg)),
        (f"{pkg}/api.py", api(d, pkg)),
        (f"tests/test_{d.key}.py", tests(d, pkg)),
    ]
    readme = (f"# {name}\n\n{d.title} service in plain Python (standard library only).\n\n"
              f"Records: {', '.join(e.name for e in d.entities)}.\n\n"
              "```bash\npython -m unittest discover -s tests -t .\n"
              f"python -m {pkg}.api      # http://127.0.0.1:8000/health\n```\n")
    scaffold = [("README.md", readme), (f"{pkg}/__init__.py", f'"""{d.title} service."""\n'),
                ("tests/__init__.py", "")]
    steps = [
        {"cmd": "python -m compileall -q .", "serve": False, "open": None, "wait": None},
        {"cmd": "python -m unittest discover -s tests -t .", "serve": False, "open": None, "wait": 20},
        {"cmd": f"python -m {pkg}.api", "serve": True, "open": "http://127.0.0.1:8000/summary", "wait": None},
    ]
    return typed, scaffold, steps
