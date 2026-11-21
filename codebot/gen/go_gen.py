"""Go flavour: a standard-library-only service (model, store, service, net/http API,
tests). Builds with `go vet ./...` / `go test ./...` and runs with `go run ./cmd/server`."""

from .schema import enum_type, NUMERIC, TEXTUAL, camel

GO_TYPE = {"str": "string", "text": "string", "email": "string", "int": "int", "float": "float64",
           "money": "float64", "bool": "bool", "date": "string", "ref": "int"}
INITIALISMS = {"id": "ID", "url": "URL", "kg": "Kg", "cm": "Cm", "mg": "Mg", "km": "Km", "vip": "VIP"}


def gname(name):
    return "".join(INITIALISMS.get(p, p[:1].upper() + p[1:]) for p in name.split("_"))


def etype(e, f):
    return enum_type(e, f)


def gtype(e, f, pkg=""):
    if f.kind == "enum":
        return (pkg + "." if pkg else "") + etype(e, f)
    return GO_TYPE[f.kind]


class W:
    def __init__(self):
        self.lines = []

    def __call__(self, text="", indent=0):
        for line in text.split("\n") if text else [""]:
            self.lines.append(("\t" * indent + line) if line else "")

    def text(self):
        return "\n".join(self.lines).rstrip() + "\n"


def struct(w, fields, indent=1):
    """Write aligned struct fields: [(name, type, tag)]."""
    n = max(len(a) for a, _, _ in fields)
    t = max(len(b) for _, b, _ in fields)
    for a, b, tag in fields:
        w(f"{a.ljust(n)} {b.ljust(t)} {tag}".rstrip(), indent)


def kv(w, pairs, indent):
    """Write `key: value,` lines with the values lined up, as gofmt does."""
    n = max(len(k) for k, _ in pairs) + 1
    for k, v in pairs:
        w(f"{(k + ':').ljust(n)} {v},", indent)


def has_money(d):
    return any(f.kind in ("money", "float") for e in d.entities for f in e.fields)


# ---------------------------------------------------------------------------- model
def model_go(d, mod):
    w = W()
    w(f"// Package model holds the {d.title} records and their validation rules.")
    w("package model")
    w()
    w("import (")
    w('\t"cmp"')
    w('\t"errors"')
    w('\t"fmt"')
    if any(f.kind == "money" for e in d.entities for f in e.fields):
        w('\t"math"')
    w('\t"regexp"')
    w('\t"strings"')
    w('\t"time"')
    w(")")
    w()
    w("var emailPattern = regexp.MustCompile(`^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$`)")
    w("""
// ValidationError reports a field holding a value the service can't accept.
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string { return e.Field + ": " + e.Message }

// Invalid builds a ValidationError.
func Invalid(field, format string, args ...any) error {
	return &ValidationError{Field: field, Message: fmt.Sprintf(format, args...)}
}

// IsValidation reports whether err is (or wraps) a ValidationError.
func IsValidation(err error) bool {
	var v *ValidationError
	return errors.As(err, &v)
}

// CheckText trims value and checks it isn't empty (unless optional) or too long.
func CheckText(field, value string, max int, required bool) (string, error) {
	cleaned := strings.TrimSpace(value)
	if required && cleaned == "" {
		return "", Invalid(field, "is required")
	}
	if len(cleaned) > max {
		return "", Invalid(field, "must be at most %d characters", max)
	}
	return cleaned, nil
}

// CheckEmail checks for a plausible e-mail address and lower-cases it.
func CheckEmail(field, value string) (string, error) {
	text, err := CheckText(field, value, 254, true)
	if err != nil {
		return "", err
	}
	if !emailPattern.MatchString(text) {
		return "", Invalid(field, "must be an e-mail address")
	}
	return strings.ToLower(text), nil
}

// CheckInt rejects negative numbers.
func CheckInt(field string, value int) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	if value > 1_000_000_000 {
		return Invalid(field, "must be at most 1000000000")
	}
	return nil
}

// CheckNumber rejects negative amounts.
func CheckNumber(field string, value float64) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	return nil
}

// CheckDate wants an ISO date (YYYY-MM-DD) that exists in the calendar.
func CheckDate(field, value string) error {
	if _, err := time.Parse("2006-01-02", value); err != nil {
		return Invalid(field, "must be a real date like 2026-01-31")
	}
	return nil
}

// CheckRef wants the id of another record (existence is checked by the service).
func CheckRef(field string, value int) error {
	if value < 1 {
		return Invalid(field, "must point at a record")
	}
	return nil
}""")
    for e in d.entities:
        for f in e.of("enum"):
            t = etype(e, f)
            w()
            w(f"// {t} is the {f.human} of a {e.name}.")
            w(f"type {t} string")
            w()
            w(f"// Allowed {t} values.")
            w("const (")
            struct(w, [(t + gname(v), t, f'= "{v}"') for v in f.values])
            w(")")
            w()
            w(f"// {t}Values lists every allowed {t}.")
            w(f"var {t}Values = []{t}{{" + ", ".join(t + gname(v) for v in f.values) + "}")
            w(f"""
// Valid reports whether v is one of the allowed values.
func (v {t}) Valid() bool {{
	for _, allowed := range {t}Values {{
		if v == allowed {{
			return true
		}}
	}}
	return false
}}

// Label is a human-friendly name for v.
func (v {t}) Label() string {{
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}}

// Parse{t} turns text into a {t}.
func Parse{t}(text string) ({t}, error) {{
	v := {t}(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {{
		return "", Invalid("{f.name}", "must be one of %s", {t}List())
	}}
	return v, nil
}}

// {t}List is every allowed value, comma separated.
func {t}List() string {{
	parts := make([]string, len({t}Values))
	for i, v := range {t}Values {{
		parts[i] = string(v)
	}}
	return strings.Join(parts, ", ")
}}""")
    for e in d.entities:
        r = e.name[0].lower()
        w()
        w(f"// {e.name} is a {e.human} record.")
        w(f"type {e.name} struct {{")
        struct(w, [("ID", "int", '`json:"id"`')] +
               [(gname(f.name), gtype(e, f), f'`json:"{f.name}"`') for f in e.fields])
        w("}")
        w()
        w("// Validate checks every field and normalises text and amounts in place.")
        w(f"func ({r} *{e.name}) Validate() error {{")
        w("\tvar err error")
        uses_err = False
        for f in e.fields:
            g = f"{r}.{gname(f.name)}"
            if f.kind == "str":
                w(f'\tif {g}, err = CheckText("{f.name}", {g}, 120, true); err != nil {{')
            elif f.kind == "text":
                w(f'\tif {g}, err = CheckText("{f.name}", {g}, 2000, false); err != nil {{')
            elif f.kind == "email":
                w(f'\tif {g}, err = CheckEmail("{f.name}", {g}); err != nil {{')
            elif f.kind == "int":
                w(f'\tif err = CheckInt("{f.name}", {g}); err != nil {{')
            elif f.kind in ("float", "money"):
                w(f'\tif err = CheckNumber("{f.name}", {g}); err != nil {{')
            elif f.kind == "date":
                w(f'\tif err = CheckDate("{f.name}", {g}); err != nil {{')
            elif f.kind == "ref":
                w(f'\tif err = CheckRef("{f.name}", {g}); err != nil {{')
            elif f.kind == "enum":
                w(f"\tif !{g}.Valid() {{")
                w(f'\t\treturn Invalid("{f.name}", "must be one of %s", {etype(e, f)}List())')
                w("\t}")
                continue
            else:
                continue
            uses_err = True
            w("\t\treturn err")
            w("\t}")
            if f.kind == "money":
                w(f"\t{g} = math.Round({g}*100) / 100")
        if not uses_err:
            w("\t_ = err")
        w("\treturn nil")
        w("}")
        lf = e.label_field
        w()
        w("// Summary is one line for logs and lists.")
        w(f"func ({r} {e.name}) Summary() string {{")
        if lf:
            w(f'\treturn fmt.Sprintf("{e.name} #%d: %s", {r}.ID, {r}.{gname(lf.name)})')
        else:
            w(f'\treturn fmt.Sprintf("{e.name} #%d", {r}.ID)')
        w("}")
        w()
        w("// Map is the record as plain values (for CSV export and templates).")
        w(f"func ({r} {e.name}) Map() map[string]any {{")
        w("\treturn map[string]any{")
        kv(w, [('"id"', f"{r}.ID")] + [
            (f'"{f.name}"', f"string({r}.{gname(f.name)})" if f.kind == "enum" else f"{r}.{gname(f.name)}")
            for f in e.fields], 2)
        w("\t}")
        w("}")
        for f in e.fields:
            if f.kind == "bool":
                continue
            g = gname(f.name)
            a, b = f"a.{g}", f"b.{g}"
            if f.kind == "enum":
                a, b = f"string({a})", f"string({b})"
            w()
            w(f"// Compare{e.name}By{g} orders {e.plural.replace('_', ' ')} by {f.human} (for slices.SortFunc).")
            w(f"func Compare{e.name}By{g}(a, b {e.name}) int {{")
            w(f"\treturn cmp.Compare({a}, {b})")
            w("}")
        w()
        w(f'// {e.name}Patch changes some fields of a {e.name}; nil means "leave as it is".')
        w(f"type {e.name}Patch struct {{")
        struct(w, [(gname(f.name), "*" + gtype(e, f), f'`json:"{f.name},omitempty"`') for f in e.fields])
        w("}")
        w()
        w(f"// Apply returns a validated copy of item with the patch applied.")
        w(f"func (p {e.name}Patch) Apply(item {e.name}) ({e.name}, error) {{")
        for f in e.fields:
            g = gname(f.name)
            w(f"\tif p.{g} != nil {{")
            w(f"\t\titem.{g} = *p.{g}")
            w("\t}")
        w("\terr := item.Validate()")
        w("\treturn item, err")
        w("}")
    return w.text()


# ---------------------------------------------------------------------------- store
def store_go(d, mod):
    w = W()
    w(f"// Package store keeps the {d.title} records in memory, safe for concurrent use.")
    w("package store")
    w()
    w("import (")
    w('\t"sort"')
    w('\t"strings"')
    w('\t"sync"')
    w()
    w(f'\t"{mod}/internal/model"')
    w(")")
    for e in d.entities:
        T, S = f"model.{e.name}", f"{e.name}Store"
        w(f"""
// {S} keeps every {e.human}.
type {S} struct {{
	mu     sync.RWMutex
	items  map[int]{T}
	nextID int
}}

// New{S} returns an empty store.
func New{S}() *{S} {{
	return &{S}{{items: map[int]{T}{{}}, nextID: 1}}
}}

// Create stores item under the next id and returns it.
func (s *{S}) Create(item {T}) {T} {{
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}}

// Get returns the record with that id.
func (s *{S}) Get(id int) ({T}, bool) {{
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}}

// List returns every record, oldest first.
func (s *{S}) List() []{T} {{
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]{T}, 0, len(s.items))
	for _, item := range s.items {{
		out = append(out, item)
	}}
	sort.Slice(out, func(i, j int) bool {{ return out[i].ID < out[j].ID }})
	return out
}}

// Update replaces an existing record; false if there is none.
func (s *{S}) Update(item {T}) bool {{
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {{
		return false
	}}
	s.items[item.ID] = item
	return true
}}

// Delete removes a record; false if there was none.
func (s *{S}) Delete(id int) bool {{
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {{
		return false
	}}
	delete(s.items, id)
	return true
}}

// Count is the number of records.
func (s *{S}) Count() int {{
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}}

// Filter returns the records keep() accepts, oldest first.
func (s *{S}) Filter(keep func({T}) bool) []{T} {{
	out := []{T}{{}}
	for _, item := range s.List() {{
		if keep(item) {{
			out = append(out, item)
		}}
	}}
	return out
}}""")
        for f in e.fields:
            g = gname(f.name)
            if f.kind in TEXTUAL:
                w(f"""
// FindBy{g} returns records whose {f.human} is exactly value.
func (s *{S}) FindBy{g}(value string) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} == value }})
}}

// Search{g} returns records whose {f.human} contains text (any case).
func (s *{S}) Search{g}(text string) []{T} {{
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item {T}) bool {{ return strings.Contains(strings.ToLower(item.{g}), needle) }})
}}""")
            elif f.kind in NUMERIC:
                t = GO_TYPE[f.kind]
                w(f"""
// Between{g} returns records whose {f.human} is within [low, high].
func (s *{S}) Between{g}(low, high {t}) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} >= low && item.{g} <= high }})
}}

// Total{g} adds up the {f.human} of every record.
func (s *{S}) Total{g}() {t} {{
	var total {t}
	for _, item := range s.List() {{
		total += item.{g}
	}}
	return total
}}

// Average{g} is the mean {f.human} (0 when there are no records).
func (s *{S}) Average{g}() float64 {{
	items := s.List()
	if len(items) == 0 {{
		return 0
	}}
	return float64(s.Total{g}()) / float64(len(items))
}}

// Max{g} returns the record with the highest {f.human}.
func (s *{S}) Max{g}() ({T}, bool) {{
	var best {T}
	found := false
	for _, item := range s.List() {{
		if !found || item.{g} > best.{g} {{
			best, found = item, true
		}}
	}}
	return best, found
}}""")
            elif f.kind == "enum":
                t = f"model.{etype(e, f)}"
                w(f"""
// With{g} returns records whose {f.human} is value.
func (s *{S}) With{g}(value {t}) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} == value }})
}}

// CountBy{g} counts records for every {f.human}.
func (s *{S}) CountBy{g}() map[{t}]int {{
	counts := map[{t}]int{{}}
	for _, v := range model.{etype(e, f)}Values {{
		counts[v] = 0
	}}
	for _, item := range s.List() {{
		counts[item.{g}]++
	}}
	return counts
}}""")
            elif f.kind == "bool":
                w(f"""
// Where{g} returns records whose {f.human} flag equals flag.
func (s *{S}) Where{g}(flag bool) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} == flag }})
}}""")
            elif f.kind == "date":
                w(f"""
// {g}Before returns records whose {f.human} is before day (YYYY-MM-DD).
func (s *{S}) {g}Before(day string) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} < day }})
}}

// {g}After returns records whose {f.human} is after day (YYYY-MM-DD).
func (s *{S}) {g}After(day string) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} > day }})
}}

// {g}On returns records whose {f.human} is day.
func (s *{S}) {g}On(day string) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} == day }})
}}""")
            elif f.kind == "ref":
                st = gname(f.ref_stem)
                w(f"""
// For{st} returns records linked to {f.ref_stem.replace('_', ' ')} id.
func (s *{S}) For{st}(id int) []{T} {{
	return s.Filter(func(item {T}) bool {{ return item.{g} == id }})
}}

// CountFor{st} counts records linked to {f.ref_stem.replace('_', ' ')} id.
func (s *{S}) CountFor{st}(id int) int {{
	return len(s.For{st}(id))
}}""")
        tf = e.of("str", "text", "email")
        w()
        w("// Search returns records where any text field contains text (any case).")
        w(f"func (s *{S}) Search(text string) []{T} {{")
        w("\tneedle := strings.ToLower(strings.TrimSpace(text))")
        w(f"\treturn s.Filter(func(item {T}) bool {{")
        if tf:
            w("\t\tfor _, value := range []string{" + ", ".join(f"item.{gname(f.name)}" for f in tf) + "} {")
            w("\t\t\tif strings.Contains(strings.ToLower(value), needle) {")
            w("\t\t\t\treturn true")
            w("\t\t\t}")
            w("\t\t}")
            w("\t\treturn false")
        else:
            w("\t\treturn needle == \"\"")
        w("\t})")
        w("}")
    return w.text()


# -------------------------------------------------------------------------- service
def sample(e, f, d):
    k = f.kind
    if k == "str":
        return f'fmt.Sprintf("{e.human.capitalize()} {f.human} %d", i)'
    if k == "text":
        return f'fmt.Sprintf("Notes about {e.human} %d.", i)'
    if k == "email":
        return f'fmt.Sprintf("{e.snake}%d@example.com", i)'
    if k == "int":
        return "i + 1"
    if k == "float":
        return "1.5*float64(i) + 0.25"
    if k == "money":
        return "math.Round((10*float64(i)+0.99)*100) / 100"
    if k == "bool":
        return "i%2 == 1"
    if k == "date":
        return 'fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1)'
    if k == "enum":
        return f"model.{etype(e, f)}Values[i%{len(f.values)}]"
    return "(i-1)%3 + 1"


def service_go(d, mod):
    w = W()
    w(f"// Package service holds the {d.title} business rules: validation, links between")
    w("// records, small domain operations and statistics.")
    w("package service")
    w()
    w("import (")
    w('\t"errors"')
    w('\t"fmt"')
    if has_money(d):
        w('\t"math"')
    w()
    w(f'\t"{mod}/internal/model"')
    w(f'\t"{mod}/internal/store"')
    w(")")
    w("""
// Errors the service returns (wrapped with details).
var (
	ErrNotFound = errors.New("not found")
	ErrConflict = errors.New("conflict")
)

func notFound(entity string, id int) error {
	return fmt.Errorf("%s %d: %w", entity, id, ErrNotFound)
}

func inUse(entity string, id, n int, by string) error {
	return fmt.Errorf("%s %d is still used by %d %s: %w", entity, id, n, by, ErrConflict)
}
""")
    w("// Service is the whole application: every store plus the rules between them.")
    w("type Service struct {")
    struct(w, [(e.plural_camel, f"*store.{e.name}Store", "") for e in d.entities])
    w("}")
    w()
    w("// New returns a service with empty stores.")
    w("func New() *Service {")
    w("\treturn &Service{")
    kv(w, [(e.plural_camel, f"store.New{e.name}Store()") for e in d.entities], 2)
    w("\t}")
    w("}")
    w()
    w("// Seed creates n sample records of every kind.")
    w("func (s *Service) Seed(n int) error {")
    w("\tfor i := 1; i <= n; i++ {")
    for e in d.entities:
        w(f"\t\tif _, err := s.Create{e.name}(Sample{e.name}(i)); err != nil {{")
        w("\t\t\treturn err")
        w("\t\t}")
    w("\t}")
    w("\treturn nil")
    w("}")
    for e in d.entities:
        T, N, P = f"model.{e.name}", e.name, e.plural_camel
        w(f"""
// Create{N} validates and stores a new {e.human}.
func (s *Service) Create{N}(item {T}) ({T}, error) {{
	item.ID = 0
	if err := item.Validate(); err != nil {{
		return {T}{{}}, err
	}}
	if err := s.check{N}Links(item); err != nil {{
		return {T}{{}}, err
	}}
	return s.{P}.Create(item), nil
}}

// Get{N} returns one {e.human}.
func (s *Service) Get{N}(id int) ({T}, error) {{
	item, ok := s.{P}.Get(id)
	if !ok {{
		return {T}{{}}, notFound("{e.human}", id)
	}}
	return item, nil
}}

// List{P} returns every {e.human}, oldest first.
func (s *Service) List{P}() []{T} {{
	return s.{P}.List()
}}

// Update{N} applies patch to a {e.human}.
func (s *Service) Update{N}(id int, patch model.{N}Patch) ({T}, error) {{
	current, err := s.Get{N}(id)
	if err != nil {{
		return {T}{{}}, err
	}}
	updated, err := patch.Apply(current)
	if err != nil {{
		return {T}{{}}, err
	}}
	if err := s.check{N}Links(updated); err != nil {{
		return {T}{{}}, err
	}}
	s.{P}.Update(updated)
	return updated, nil
}}

// Delete{N} removes a {e.human} nothing points at any more.
func (s *Service) Delete{N}(id int) error {{
	if _, err := s.Get{N}(id); err != nil {{
		return err
	}}""")
        for de, df in d.dependents(e):
            w(f"\tif n := s.{de.plural_camel}.CountFor{gname(df.ref_stem)}(id); n > 0 {{")
            w(f'\t\treturn inUse("{e.human}", id, n, "{de.plural.replace("_", " ")}")')
            w("\t}")
        w(f"\ts.{P}.Delete(id)")
        w("\treturn nil")
        w("}")
        refs = e.of("ref")
        w()
        w(f"// check{N}Links makes sure every record a {e.human} points at exists.")
        if refs:
            w(f"func (s *Service) check{N}Links(item {T}) error {{")
            for f in refs:
                t = d.get(f.ref)
                w(f"\tif _, ok := s.{t.plural_camel}.Get(item.{gname(f.name)}); !ok {{")
                w(f'\t\treturn notFound("{t.human}", item.{gname(f.name)})')
                w("\t}")
            w("\treturn nil")
            w("}")
        else:
            w(f"func (s *Service) check{N}Links(_ {T}) error {{")
            w("\treturn nil")
            w("}")
        for f in e.fields:
            g = gname(f.name)
            if f.kind == "enum":
                w(f"""
// Set{N}{g} moves a {e.human} to another {f.human}.
func (s *Service) Set{N}{g}(id int, value model.{etype(e, f)}) ({T}, error) {{
	return s.Update{N}(id, model.{N}Patch{{{g}: &value}})
}}""")
            elif f.kind == "bool":
                w(f"""
// Toggle{N}{g} flips the {f.human} flag of a {e.human}.
func (s *Service) Toggle{N}{g}(id int) ({T}, error) {{
	item, err := s.Get{N}(id)
	if err != nil {{
		return {T}{{}}, err
	}}
	flipped := !item.{g}
	return s.Update{N}(id, model.{N}Patch{{{g}: &flipped}})
}}""")
            elif f.kind in NUMERIC:
                t = GO_TYPE[f.kind]
                expr = f"item.{g} + delta" if f.kind == "int" else f"math.Round((item.{g}+delta)*100) / 100"
                w(f"""
// Adjust{N}{g} adds delta to the {f.human} of a {e.human} (it can't go below zero).
func (s *Service) Adjust{N}{g}(id int, delta {t}) ({T}, error) {{
	item, err := s.Get{N}(id)
	if err != nil {{
		return {T}{{}}, err
	}}
	value := {expr}
	return s.Update{N}(id, model.{N}Patch{{{g}: &value}})
}}""")
        stats = [("Count", "int", '`json:"count"`')]
        for f in e.fields:
            g = gname(f.name)
            if f.kind in NUMERIC:
                stats.append((f"Total{g}", GO_TYPE[f.kind], f'`json:"total_{f.name}"`'))
                stats.append((f"Average{g}", "float64", f'`json:"average_{f.name}"`'))
            elif f.kind == "enum":
                stats.append((f"By{g}", f"map[model.{etype(e, f)}]int", f'`json:"by_{f.name}"`'))
            elif f.kind == "bool":
                stats.append((g, "int", f'`json:"{f.name}"`'))
        w()
        w(f"// {N}Stats sums up every {e.human}.")
        w(f"type {N}Stats struct {{")
        struct(w, stats)
        w("}")
        w()
        w(f"// {N}Stats returns totals and breakdowns over every {e.human}.")
        w(f"func (s *Service) {N}Stats() {N}Stats {{")
        w(f"\treturn {N}Stats{{")
        pairs = [("Count", f"s.{P}.Count()")]
        for f in e.fields:
            g = gname(f.name)
            if f.kind in NUMERIC:
                pairs += [(f"Total{g}", f"s.{P}.Total{g}()"), (f"Average{g}", f"s.{P}.Average{g}()")]
            elif f.kind == "enum":
                pairs.append((f"By{g}", f"s.{P}.CountBy{g}()"))
            elif f.kind == "bool":
                pairs.append((g, f"len(s.{P}.Where{g}(true))"))
        kv(w, pairs, 2)
        w("\t}")
        w("}")
        w()
        w(f"// Sample{N} returns valid data for a new {e.human} (links point at seeded records).")
        w(f"func Sample{N}(i int) {T} {{")
        w(f"\treturn {T}{{")
        kv(w, [(gname(f.name), sample(e, f, d)) for f in e.fields], 2)
        w("\t}")
        w("}")
    return w.text()


# ---------------------------------------------------------------------------- http
def http_go(d, mod):
    w = W()
    w(f"// Package httpapi serves the {d.title} service as JSON over HTTP (net/http only).")
    w("//")
    w("// Every collection has GET (list, with filters, ?q= search, ?page=&size=), POST,")
    w("// GET /{id}, PATCH /{id}, DELETE /{id} and GET /stats.")
    w("package httpapi")
    w()
    w("import (")
    w('\t"encoding/json"')
    w('\t"errors"')
    w('\t"net/http"')
    w('\t"strconv"')
    w()
    w(f'\t"{mod}/internal/model"')
    w(f'\t"{mod}/internal/service"')
    w(")")
    w()
    w("// API answers HTTP requests using the service.")
    w("type API struct {")
    w("\tsvc *service.Service")
    w("}")
    w()
    w("// New returns the routes of the whole service.")
    w("func New(svc *service.Service) http.Handler {")
    w("\ta := &API{svc: svc}")
    w("\tmux := http.NewServeMux()")
    w('\tmux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {')
    w('\t\twriteJSON(w, http.StatusOK, map[string]string{"status": "ok"})')
    w("\t})")
    for e in d.entities:
        p, P = e.path, e.plural_camel
        for meth, route, fn in (("GET", "", f"list{P}"), ("POST", "", f"create{e.name}"),
                                ("GET", "/stats", f"stats{e.name}"), ("GET", "/{id}", f"get{e.name}"),
                                ("PATCH", "/{id}", f"update{e.name}"), ("DELETE", "/{id}", f"delete{e.name}")):
            w(f'\tmux.HandleFunc("{meth} /{p}{route}", a.{fn})')
    w("\treturn mux")
    w("}")
    w("""
func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if value != nil {
		_ = json.NewEncoder(w).Encode(value)
	}
}

func writeError(w http.ResponseWriter, err error) {
	var invalid *model.ValidationError
	switch {
	case errors.As(err, &invalid):
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": err.Error(), "field": invalid.Field})
	case errors.Is(err, service.ErrNotFound):
		writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
	case errors.Is(err, service.ErrConflict):
		writeJSON(w, http.StatusConflict, map[string]string{"error": err.Error()})
	default:
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
}

func decode(r *http.Request, into any) error {
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(into); err != nil {
		return &model.ValidationError{Field: "body", Message: err.Error()}
	}
	return nil
}

func pathID(r *http.Request) (int, error) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil || id < 1 {
		return 0, &model.ValidationError{Field: "id", Message: "must be a positive whole number"}
	}
	return id, nil
}

func queryInt(r *http.Request, name string) (int, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.Atoi(raw)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a whole number"}
	}
	return v, true, nil
}

func queryFloat(r *http.Request, name string) (float64, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return 0, false, nil
	}
	v, err := strconv.ParseFloat(raw, 64)
	if err != nil {
		return 0, false, &model.ValidationError{Field: name, Message: "must be a number"}
	}
	return v, true, nil
}

func queryBool(r *http.Request, name string) (bool, bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return false, false, nil
	}
	v, err := strconv.ParseBool(raw)
	if err != nil {
		return false, false, &model.ValidationError{Field: name, Message: "must be true or false"}
	}
	return v, true, nil
}

// keep returns the items ok() accepts.
func keep[T any](items []T, ok func(T) bool) []T {
	out := make([]T, 0, len(items))
	for _, item := range items {
		if ok(item) {
			out = append(out, item)
		}
	}
	return out
}

// window returns one page of items (?page= from 1, ?size= up to 200).
func window[T any](r *http.Request, items []T) ([]T, error) {
	page, ok, err := queryInt(r, "page")
	if err != nil {
		return nil, err
	}
	if !ok || page < 1 {
		page = 1
	}
	size, ok, err := queryInt(r, "size")
	if err != nil {
		return nil, err
	}
	if !ok || size < 1 || size > 200 {
		size = 50
	}
	start := (page - 1) * size
	if start >= len(items) {
		return []T{}, nil
	}
	end := min(start+size, len(items))
	return items[start:end], nil
}""")
    for e in d.entities:
        T, N, P = f"model.{e.name}", e.name, e.plural_camel
        w()
        w(f"func (a *API) list{P}(w http.ResponseWriter, r *http.Request) {{")
        w(f"\titems := a.svc.List{P}()")
        w("\tq := r.URL.Query()")
        w('\tif text := q.Get("q"); text != "" {')
        w("\t\thits := map[int]bool{}")
        w(f"\t\tfor _, item := range a.svc.{P}.Search(text) {{")
        w("\t\t\thits[item.ID] = true")
        w("\t\t}")
        w(f"\t\titems = keep(items, func(item {T}) bool {{ return hits[item.ID] }})")
        w("\t}")
        for f in e.fields:
            g, n = gname(f.name), f.name
            if f.kind in TEXTUAL:
                w(f'\tif value := q.Get("{n}"); value != "" {{')
                w(f"\t\titems = keep(items, func(item {T}) bool {{ return item.{g} == value }})")
                w("\t}")
            elif f.kind in NUMERIC:
                qf = "queryInt" if f.kind == "int" else "queryFloat"
                for side, op in (("min", ">="), ("max", "<=")):
                    w(f'\tif limit, ok, err := {qf}(r, "{side}_{n}"); err != nil {{')
                    w("\t\twriteError(w, err)")
                    w("\t\treturn")
                    w("\t} else if ok {")
                    w(f"\t\titems = keep(items, func(item {T}) bool {{ return item.{g} {op} limit }})")
                    w("\t}")
            elif f.kind == "enum":
                w(f'\tif raw := q.Get("{n}"); raw != "" {{')
                w(f"\t\twanted, err := model.Parse{etype(e, f)}(raw)")
                w("\t\tif err != nil {")
                w("\t\t\twriteError(w, err)")
                w("\t\t\treturn")
                w("\t\t}")
                w(f"\t\titems = keep(items, func(item {T}) bool {{ return item.{g} == wanted }})")
                w("\t}")
            elif f.kind == "bool":
                w(f'\tif flag, ok, err := queryBool(r, "{n}"); err != nil {{')
                w("\t\twriteError(w, err)")
                w("\t\treturn")
                w("\t} else if ok {")
                w(f"\t\titems = keep(items, func(item {T}) bool {{ return item.{g} == flag }})")
                w("\t}")
            elif f.kind == "date":
                for side, op in (("from", ">="), ("to", "<=")):
                    w(f'\tif day := q.Get("{n}_{side}"); day != "" {{')
                    w(f"\t\titems = keep(items, func(item {T}) bool {{ return item.{g} {op} day }})")
                    w("\t}")
            elif f.kind == "ref":
                w(f'\tif id, ok, err := queryInt(r, "{n}"); err != nil {{')
                w("\t\twriteError(w, err)")
                w("\t\treturn")
                w("\t} else if ok {")
                w(f"\t\titems = keep(items, func(item {T}) bool {{ return item.{g} == id }})")
                w("\t}")
        w("\tpage, err := window(r, items)")
        w("\tif err != nil {")
        w("\t\twriteError(w, err)")
        w("\t\treturn")
        w("\t}")
        w("\twriteJSON(w, http.StatusOK, page)")
        w("}")
        w(f"""
func (a *API) create{N}(w http.ResponseWriter, r *http.Request) {{
	var item {T}
	if err := decode(r, &item); err != nil {{
		writeError(w, err)
		return
	}}
	created, err := a.svc.Create{N}(item)
	if err != nil {{
		writeError(w, err)
		return
	}}
	writeJSON(w, http.StatusCreated, created)
}}

func (a *API) stats{N}(w http.ResponseWriter, _ *http.Request) {{
	writeJSON(w, http.StatusOK, a.svc.{N}Stats())
}}

func (a *API) get{N}(w http.ResponseWriter, r *http.Request) {{
	id, err := pathID(r)
	if err != nil {{
		writeError(w, err)
		return
	}}
	item, err := a.svc.Get{N}(id)
	if err != nil {{
		writeError(w, err)
		return
	}}
	writeJSON(w, http.StatusOK, item)
}}

func (a *API) update{N}(w http.ResponseWriter, r *http.Request) {{
	id, err := pathID(r)
	if err != nil {{
		writeError(w, err)
		return
	}}
	var patch model.{N}Patch
	if err := decode(r, &patch); err != nil {{
		writeError(w, err)
		return
	}}
	item, err := a.svc.Update{N}(id, patch)
	if err != nil {{
		writeError(w, err)
		return
	}}
	writeJSON(w, http.StatusOK, item)
}}

func (a *API) delete{N}(w http.ResponseWriter, r *http.Request) {{
	id, err := pathID(r)
	if err != nil {{
		writeError(w, err)
		return
	}}
	if err := a.svc.Delete{N}(id); err != nil {{
		writeError(w, err)
		return
	}}
	w.WriteHeader(http.StatusNoContent)
}}""")
    return w.text()


# ---------------------------------------------------------------------------- tests
BAD = {"str": '""', "text": 'strings.Repeat("x", 3000)', "email": '"not-an-email"', "int": "-1",
       "float": "-1", "money": "-5", "date": '"2026-02-30"', "enum": '"nope"', "ref": "0"}


def test_go(d, mod):
    w = W()
    w("package service_test")
    w()
    w("import (")
    for imp in ("bytes", "encoding/json", "errors", "fmt", "net/http", "net/http/httptest", "strings", "testing"):
        w(f'\t"{imp}"')
    w()
    w(f'\t"{mod}/internal/httpapi"')
    w(f'\t"{mod}/internal/model"')
    w(f'\t"{mod}/internal/service"')
    w(")")
    w("""
func seeded(t *testing.T) *service.Service {
	t.Helper()
	svc := service.New()
	if err := svc.Seed(3); err != nil {
		t.Fatalf("seed: %v", err)
	}
	return svc
}

func wantField(t *testing.T, err error, field string) {
	t.Helper()
	var invalid *model.ValidationError
	if !errors.As(err, &invalid) || invalid.Field != field {
		t.Fatalf("want a validation error on %q, got %v", field, err)
	}
}

func call(t *testing.T, h http.Handler, method, path string, body any) *httptest.ResponseRecorder {
	t.Helper()
	var reader *bytes.Reader
	if body == nil {
		reader = bytes.NewReader(nil)
	} else {
		data, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal: %v", err)
		}
		reader = bytes.NewReader(data)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest(method, path, reader))
	return rec
}

// keep the imports used even for domains without text fields
var _ = strings.ToUpper""")
    for e in d.entities:
        N, P = e.name, e.plural_camel
        w(f"""
func Test{N}CreateAndGet(t *testing.T) {{
	svc := seeded(t)
	created, err := svc.Create{N}(service.Sample{N}(10))
	if err != nil {{
		t.Fatalf("create: %v", err)
	}}
	got, err := svc.Get{N}(created.ID)
	if err != nil || got != created {{
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}}
	if n := len(svc.List{P}()); n != 4 {{
		t.Fatalf("list has %d records, want 4", n)
	}}
}}

func Test{N}Missing(t *testing.T) {{
	svc := seeded(t)
	if _, err := svc.Get{N}(9999); !errors.Is(err, service.ErrNotFound) {{
		t.Fatalf("want ErrNotFound, got %v", err)
	}}
}}""")
        for f in e.fields:
            if f.kind == "bool":
                continue
            g = gname(f.name)
            w(f"""
func Test{N}RejectsBad{g}(t *testing.T) {{
	svc := seeded(t)
	item := service.Sample{N}(12)
	item.{g} = {BAD[f.kind]}
	_, err := svc.Create{N}(item)
	wantField(t, err, "{f.name}")
}}""")
        for f in e.of("ref"):
            g = gname(f.name)
            w(f"""
func Test{N}{g}MustExist(t *testing.T) {{
	svc := seeded(t)
	item := service.Sample{N}(13)
	item.{g} = 9999
	if _, err := svc.Create{N}(item); !errors.Is(err, service.ErrNotFound) {{
		t.Fatalf("want ErrNotFound, got %v", err)
	}}
}}""")
        for f in e.fields:
            g = gname(f.name)
            if f.kind == "enum":
                t = etype(e, f)
                w(f"""
func TestSet{N}{g}(t *testing.T) {{
	svc := seeded(t)
	last := model.{t}Values[len(model.{t}Values)-1]
	item, err := svc.Set{N}{g}(1, last)
	if err != nil || item.{g} != last {{
		t.Fatalf("set = %v, %v", item.{g}, err)
	}}
	if got, want := svc.{P}.CountBy{g}()[last], len(svc.{P}.With{g}(last)); got != want {{
		t.Fatalf("count %d != %d", got, want)
	}}
}}""")
            elif f.kind == "bool":
                w(f"""
func TestToggle{N}{g}(t *testing.T) {{
	svc := seeded(t)
	before, _ := svc.Get{N}(1)
	after, err := svc.Toggle{N}{g}(1)
	if err != nil || after.{g} == before.{g} {{
		t.Fatalf("toggle = %v, %v", after.{g}, err)
	}}
}}""")
            elif f.kind == "int":
                w(f"""
func TestAdjust{N}{g}(t *testing.T) {{
	svc := seeded(t)
	before, _ := svc.Get{N}(1)
	after, err := svc.Adjust{N}{g}(1, 2)
	if err != nil || after.{g} != before.{g}+2 {{
		t.Fatalf("adjust = %v, %v", after.{g}, err)
	}}
	_, err = svc.Adjust{N}{g}(1, -(after.{g} + 100))
	wantField(t, err, "{f.name}")
}}""")
            elif f.kind in ("float", "money"):
                w(f"""
func TestAdjust{N}{g}(t *testing.T) {{
	svc := seeded(t)
	before, _ := svc.Get{N}(1)
	after, err := svc.Adjust{N}{g}(1, 1.5)
	if err != nil || after.{g}-before.{g} < 1.49 || after.{g}-before.{g} > 1.51 {{
		t.Fatalf("adjust = %v, %v", after.{g}, err)
	}}
}}""")
            elif f.kind in TEXTUAL:
                w(f"""
func TestSearch{N}{g}(t *testing.T) {{
	svc := seeded(t)
	target, _ := svc.Get{N}(2)
	for _, item := range svc.{P}.Search{g}(strings.ToUpper(target.{g})) {{
		if item.ID == target.ID {{
			return
		}}
	}}
	t.Fatalf("search did not find %q", target.{g})
}}""")
            elif f.kind == "date":
                w(f"""
func Test{N}{g}Ranges(t *testing.T) {{
	svc := seeded(t)
	day := service.Sample{N}(2).{g}
	total := len(svc.{P}.{g}Before(day)) + len(svc.{P}.{g}On(day)) + len(svc.{P}.{g}After(day))
	if total != svc.{P}.Count() {{
		t.Fatalf("ranges cover %d of %d records", total, svc.{P}.Count())
	}}
}}""")
        w(f"""
func TestDelete{N}(t *testing.T) {{
	svc := seeded(t)
	item, err := svc.Create{N}(service.Sample{N}(14))
	if err != nil {{
		t.Fatalf("create: %v", err)
	}}
	if err := svc.Delete{N}(item.ID); err != nil {{
		t.Fatalf("delete: %v", err)
	}}
	if _, err := svc.Get{N}(item.ID); !errors.Is(err, service.ErrNotFound) {{
		t.Fatalf("still there: %v", err)
	}}
}}""")
        if d.dependents(e):
            w(f"""
func TestDelete{N}InUse(t *testing.T) {{
	svc := seeded(t)
	if err := svc.Delete{N}(1); !errors.Is(err, service.ErrConflict) {{
		t.Fatalf("want ErrConflict, got %v", err)
	}}
}}""")
        w(f"""
func Test{N}Stats(t *testing.T) {{
	svc := seeded(t)
	if got := svc.{N}Stats().Count; got != 3 {{
		t.Fatalf("count = %d", got)
	}}
}}

func Test{N}API(t *testing.T) {{
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/{e.path}", service.Sample{N}(15))
	if rec.Code != http.StatusCreated {{
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}}
	var created model.{N}
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {{
		t.Fatalf("decode: %v", err)
	}}
	path := fmt.Sprintf("/{e.path}/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {{
		t.Fatalf("GET = %d", rec.Code)
	}}
	if rec := call(t, h, http.MethodGet, "/{e.path}?size=2&page=1", nil); rec.Code != http.StatusOK {{
		t.Fatalf("list = %d", rec.Code)
	}}
	if rec := call(t, h, http.MethodGet, "/{e.path}/stats", nil); rec.Code != http.StatusOK {{
		t.Fatalf("stats = %d", rec.Code)
	}}
	if rec := call(t, h, http.MethodPost, "/{e.path}", map[string]int{{"no_such_field": 1}}); rec.Code != http.StatusBadRequest {{
		t.Fatalf("bad POST = %d", rec.Code)
	}}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {{
		t.Fatalf("DELETE = %d", rec.Code)
	}}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {{
		t.Fatalf("GET after delete = %d", rec.Code)
	}}
}}""")
    return w.text()


def render(d, name):
    mod = name
    typed = [
        ("internal/model/model.go", model_go(d, mod)),
        ("internal/store/store.go", store_go(d, mod)),
        ("internal/service/service.go", service_go(d, mod)),
        ("internal/httpapi/httpapi.go", http_go(d, mod)),
        ("internal/service/service_test.go", test_go(d, mod)),
    ]
    main = f'''// Command server runs the {d.title} API on http://127.0.0.1:8080
package main

import (
	"log"
	"net/http"

	"{mod}/internal/httpapi"
	"{mod}/internal/service"
)

func main() {{
	svc := service.New()
	if err := svc.Seed(3); err != nil {{
		log.Fatal(err)
	}}
	addr := "127.0.0.1:8080"
	log.Printf("{d.title} API on http://%s (Ctrl+C to stop)", addr)
	log.Fatal(http.ListenAndServe(addr, httpapi.New(svc)))
}}
'''
    readme = (f"# {name}\n\n{d.title} service in Go (standard library only).\n\n"
              f"Records: {', '.join(e.name for e in d.entities)}.\n\n"
              "```bash\ngo test ./...\ngo run ./cmd/server     # http://127.0.0.1:8080/health\n```\n")
    scaffold = [("go.mod", f"module {mod}\n\ngo 1.22\n"), ("cmd/server/main.go", main), ("README.md", readme)]
    first = d.entities[0].path
    steps = [
        {"cmd": "go vet ./...", "serve": False, "open": None, "wait": 25},
        {"cmd": "go test ./...", "serve": False, "open": None, "wait": 30},
        {"cmd": "go run ./cmd/server", "serve": True, "open": f"http://127.0.0.1:8080/{first}", "wait": 12},
    ]
    return typed, scaffold, steps
