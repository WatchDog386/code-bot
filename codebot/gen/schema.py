"""The business domains the project generator can build, and the schema helpers.

A domain is a set of entities. Each entity line reads

    Name: field kind, field kind(args), ...

kinds: str, text, email, int, float, money, bool, date, enum(a|b|c), ref(Entity)
A ref field must point at an entity listed earlier and its name must end in "_id".
"""

import re
from dataclasses import dataclass, field

DOMAINS = {
    "library": ("Library Circulation", """
        Author: name str, email email, country str, born date, active bool
        Book: title str, author_id ref(Author), isbn str, pages int, price money, published date, genre enum(fiction|science|history|poetry|children), available bool
        Member: name str, email email, phone str, joined date, tier enum(basic|student|premium), fines money, active bool
        Loan: book_id ref(Book), member_id ref(Member), borrowed date, due date, renewals int, status enum(open|returned|overdue|lost), fee money
        Reservation: book_id ref(Book), member_id ref(Member), requested date, position int, status enum(waiting|ready|cancelled|fulfilled), notes text
        Branch: name str, city str, phone str, opened date, seats int, open_late bool
    """),
    "clinic": ("Clinic Scheduling", """
        Doctor: name str, email email, specialty enum(general|pediatrics|cardiology|dermatology|orthopedics), room str, hourly_rate money, accepting bool
        Patient: name str, email email, phone str, birth_date date, insurance str, allergies text, active bool
        Appointment: doctor_id ref(Doctor), patient_id ref(Patient), day date, slot int, duration int, reason text, status enum(booked|checked_in|completed|cancelled|no_show), fee money
        Prescription: appointment_id ref(Appointment), drug str, dose_mg int, times_per_day int, days int, refills int, notes text
        Invoice: patient_id ref(Patient), issued date, amount money, paid money, status enum(draft|sent|paid|void), due date
        LabResult: patient_id ref(Patient), test_name str, value float, unit str, taken date, flagged bool
    """),
    "hotel": ("Hotel Reservations", """
        RoomType: name str, beds int, max_guests int, nightly_rate money, smoking bool
        Room: room_type_id ref(RoomType), number str, floor int, status enum(clean|dirty|occupied|maintenance), sea_view bool
        Guest: name str, email email, phone str, country str, vip bool, loyalty_points int
        Booking: room_id ref(Room), guest_id ref(Guest), check_in date, check_out date, guests int, total money, status enum(pending|confirmed|checked_in|checked_out|cancelled), notes text
        Charge: booking_id ref(Booking), description str, amount money, posted date, category enum(minibar|restaurant|spa|laundry|other)
        Housekeeping: room_id ref(Room), cleaned date, minutes int, staff str, inspected bool
    """),
    "fleet": ("Fleet Management", """
        Vehicle: plate str, make str, model str, year int, mileage int, fuel enum(petrol|diesel|electric|hybrid), active bool
        Driver: name str, email email, license_no str, license_expiry date, rating float, on_duty bool
        Trip: vehicle_id ref(Vehicle), driver_id ref(Driver), started date, distance_km float, purpose str, status enum(planned|in_progress|done|cancelled)
        FuelLog: vehicle_id ref(Vehicle), filled date, litres float, cost money, station str
        ServiceRecord: vehicle_id ref(Vehicle), serviced date, odometer int, cost money, kind enum(oil|tyres|brakes|inspection|repair), notes text
        Incident: vehicle_id ref(Vehicle), driver_id ref(Driver), happened date, severity enum(minor|moderate|major), damage_cost money, reported bool
    """),
    "school": ("School Records", """
        Teacher: name str, email email, subject str, hired date, salary money, full_time bool
        Student: name str, email email, birth_date date, grade_level int, guardian str, active bool
        Course: teacher_id ref(Teacher), title str, code str, credits int, room str, term enum(fall|spring|summer)
        Enrollment: course_id ref(Course), student_id ref(Student), enrolled date, status enum(active|dropped|completed), final_score float
        Assignment: course_id ref(Course), title str, due date, max_points int, weight float, published bool
        Attendance: student_id ref(Student), course_id ref(Course), day date, present bool, minutes_late int, note text
    """),
    "warehouse": ("Warehouse Inventory", """
        Supplier: name str, email email, phone str, country str, lead_days int, preferred bool
        Product: supplier_id ref(Supplier), sku str, name str, unit_cost money, unit_price money, reorder_level int, category enum(hardware|electrical|plumbing|tools|safety), active bool
        Bin: code str, aisle str, shelf int, capacity int, refrigerated bool
        StockMovement: product_id ref(Product), bin_id ref(Bin), quantity int, moved date, reason enum(receive|issue|transfer|adjust|return), reference str
        PurchaseOrder: supplier_id ref(Supplier), ordered date, expected date, total money, status enum(draft|sent|partial|received|cancelled), notes text
        StockCount: bin_id ref(Bin), product_id ref(Product), counted date, expected int, found int, counter str
    """),
    "restaurant": ("Restaurant Orders", """
        MenuCategory: name str, position int, visible bool
        MenuItem: menu_category_id ref(MenuCategory), name str, price money, calories int, spicy bool, vegetarian bool, prep_minutes int
        DiningTable: label str, seats int, area enum(inside|terrace|bar|private), active bool
        CustomerOrder: dining_table_id ref(DiningTable), opened date, guests int, total money, status enum(open|served|paid|cancelled), server str
        OrderLine: customer_order_id ref(CustomerOrder), menu_item_id ref(MenuItem), quantity int, unit_price money, note text
        Booking: dining_table_id ref(DiningTable), name str, phone str, day date, party_size int, confirmed bool
    """),
    "gym": ("Gym Membership", """
        Plan: name str, monthly_fee money, months int, classes_included int, active bool
        Member: plan_id ref(Plan), name str, email email, phone str, joined date, status enum(active|frozen|cancelled|expired), visits int
        Trainer: name str, email email, specialty enum(strength|cardio|yoga|boxing|rehab), hourly_rate money, available bool
        Session: trainer_id ref(Trainer), member_id ref(Member), day date, minutes int, kind enum(personal|group|assessment), notes text
        CheckIn: member_id ref(Member), day date, minutes int, guest bool
        Payment: member_id ref(Member), paid_on date, amount money, method enum(card|cash|transfer|mobile), refunded bool
    """),
    "events": ("Event Ticketing", """
        Venue: name str, city str, capacity int, address str, accessible bool
        Concert: venue_id ref(Venue), title str, artist str, day date, doors_open str, status enum(planned|on_sale|sold_out|cancelled|finished)
        TicketType: concert_id ref(Concert), name str, price money, quantity int, sold int, seated bool
        Attendee: name str, email email, phone str, country str, newsletter bool
        Ticket: ticket_type_id ref(TicketType), attendee_id ref(Attendee), bought date, code str, status enum(valid|used|refunded|void), price_paid money
        Sponsor: concert_id ref(Concert), company str, amount money, tier enum(bronze|silver|gold|platinum), logo_url str
    """),
    "realestate": ("Real Estate Listings", """
        Agent: name str, email email, phone str, license_no str, commission_rate float, active bool
        Property: agent_id ref(Agent), address str, city str, bedrooms int, bathrooms int, area_sqm float, price money, kind enum(apartment|house|townhouse|land|office), listed date
        Client: name str, email email, phone str, budget money, buying bool
        Viewing: property_id ref(Property), client_id ref(Client), day date, minutes int, feedback text, interested bool
        Offer: property_id ref(Property), client_id ref(Client), amount money, made date, status enum(submitted|countered|accepted|rejected|withdrawn), conditions text
        OpenHouse: property_id ref(Property), day date, start_time str, visitors int, catered bool
    """),
    "helpdesk": ("Help Desk", """
        Team: name str, email email, timezone str, on_call bool
        SupportAgent: team_id ref(Team), name str, email email, level int, active bool
        Customer: name str, email email, company str, plan enum(free|pro|business|enterprise), since date
        SupportTicket: customer_id ref(Customer), support_agent_id ref(SupportAgent), subject str, body text, priority enum(low|normal|high|urgent), status enum(new|open|pending|solved|closed), opened date
        Reply: support_ticket_id ref(SupportTicket), author str, body text, sent date, internal bool
        Article: team_id ref(Team), title str, body text, views int, published bool, updated date
    """),
    "payroll": ("Payroll", """
        Department: name str, code str, budget money, cost_center str
        Employee: department_id ref(Department), name str, email email, hired date, salary money, kind enum(full_time|part_time|contractor|intern), active bool
        PayPeriod: starts date, ends date, pay_day date, status enum(open|processing|paid|closed)
        Payslip: employee_id ref(Employee), pay_period_id ref(PayPeriod), gross money, tax money, deductions money, net money, paid bool
        TimeEntry: employee_id ref(Employee), day date, hours float, overtime_hours float, project str, approved bool
        Expense: employee_id ref(Employee), spent date, amount money, category enum(travel|meals|equipment|training|other), receipt bool, note text
    """),
    "farm": ("Farm Operations", """
        Plot: name str, hectares float, soil enum(clay|loam|sand|silt|peat), irrigated bool
        Crop: name str, variety str, days_to_harvest int, seed_cost money, perennial bool
        Planting: plot_id ref(Plot), crop_id ref(Crop), planted date, rows int, expected_yield_kg float, status enum(planned|growing|harvested|failed)
        Harvest: planting_id ref(Planting), harvested date, yield_kg float, grade enum(a|b|c|reject), sold bool, price_per_kg money
        Equipment: name str, model str, bought date, hours_used int, cost money, working bool
        Task: plot_id ref(Plot), title str, due date, assignee str, done bool, notes text
    """),
    "shipping": ("Shipping & Tracking", """
        Customer: name str, email email, phone str, company str, account_no str, credit_limit money
        Depot: name str, city str, country str, capacity int, open_weekends bool
        Shipment: customer_id ref(Customer), depot_id ref(Depot), created date, service enum(standard|express|overnight|freight), status enum(created|in_transit|delivered|returned|lost), declared_value money
        Parcel: shipment_id ref(Shipment), weight_kg float, length_cm int, width_cm int, height_cm int, fragile bool
        TrackingEvent: shipment_id ref(Shipment), depot_id ref(Depot), happened date, kind enum(scanned|loaded|departed|arrived|delivered|exception), note text
        Courier: name str, phone str, vehicle str, rating float, on_shift bool
    """),
}

# Generic records most real apps grow sooner or later. Added (owned by the domain's first
# entity) until every generated file is long enough. "{owner}" = the owner entity.
POOL = """
    Note: {owner}_id ref({Owner}), subject str, body text, pinned bool, written date
    Tag: {owner}_id ref({Owner}), label str, color str, usage int
    Attachment: {owner}_id ref({Owner}), filename str, size_kb int, mime str, uploaded date
    AuditEntry: actor str, action enum(create|update|delete|login|export), at date, details text
    Notification: recipient email, title str, sent date, channel enum(email|sms|push), read bool
    ContactPerson: {owner}_id ref({Owner}), name str, email email, phone str, role str, primary bool
    Address: {owner}_id ref({Owner}), street str, city str, postcode str, country str, billing bool
    Setting: key_name str, value str, editable bool, changed date
    Reminder: {owner}_id ref({Owner}), title str, remind_on date, done bool, priority enum(low|normal|high)
    Document: {owner}_id ref({Owner}), title str, pages int, signed bool, version int, issued date
    Review: {owner}_id ref({Owner}), author str, stars int, comment text, verified bool, posted date
    Discount: code str, percent float, starts date, ends date, active bool
"""

SORTABLE = {"str", "email", "int", "float", "money", "date", "enum", "ref"}
NUMERIC = {"int", "float", "money"}
TEXTUAL = {"str", "text", "email"}


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def camel(name):
    return "".join(p[:1].upper() + p[1:] for p in name.split("_"))


def lower_camel(name):
    c = camel(name)
    return c[:1].lower() + c[1:]


def plural(word):
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    if re.search(r"(s|x|z|ch|sh)$", word):
        return word + "es"
    return word + "s"


@dataclass
class Field:
    name: str
    kind: str
    values: list = field(default_factory=list)   # enum
    ref: str = ""                                 # ref target entity

    @property
    def human(self):
        return self.name.replace("_", " ")

    @property
    def ref_stem(self):            # author_id -> author
        return self.name[:-3] if self.name.endswith("_id") else self.name


@dataclass
class Entity:
    name: str
    fields: list

    @property
    def snake(self):
        return snake(self.name)

    @property
    def human(self):
        return self.snake.replace("_", " ")

    @property
    def plural(self):
        return plural(self.snake)

    @property
    def plural_camel(self):
        return camel(self.plural)

    @property
    def path(self):
        return self.plural.replace("_", "-")

    def of(self, *kinds):
        return [f for f in self.fields if f.kind in kinds]

    @property
    def label_field(self):
        for f in self.fields:
            if f.kind in ("str", "email"):
                return f
        return None


@dataclass
class Domain:
    key: str
    title: str
    entities: list

    def dependents(self, entity):
        """(entity, field) pairs whose ref points at `entity`."""
        return [(e, f) for e in self.entities for f in e.fields if f.kind == "ref" and f.ref == entity.name]

    def get(self, name):
        return next(e for e in self.entities if e.name == name)


_FIELD_RE = re.compile(r"^(\w+)\s+(\w+)(?:\((.*)\))?$")


def parse_entity(line):
    name, rest = line.split(":", 1)
    fields = []
    for part in rest.split(","):
        part = part.strip()
        m = _FIELD_RE.match(part)
        if not m:
            raise ValueError(f"bad field spec {part!r} in {name}")
        fname, kind, arg = m.groups()
        f = Field(fname, kind)
        if kind == "enum":
            f.values = arg.split("|")
        elif kind == "ref":
            f.ref = arg
        fields.append(f)
    return Entity(name.strip(), fields)


def parse_lines(text):
    return [parse_entity(l.strip()) for l in text.strip().splitlines() if l.strip()]


def load_domain(key):
    title, text = DOMAINS[key]
    return Domain(key, title, parse_lines(text))


def pool_entities(owner, taken):
    text = POOL.replace("{owner}", owner.snake).replace("{Owner}", owner.name)
    return [e for e in parse_lines(text) if e.name not in taken]


CLASHING = {"Service", "Store", "Stats", "Patch", "Tests", "Repository", "Input", "Row"}


def enum_type(e, f):
    """Type name for a choice field: Book + genre -> BookGenre. Names that would clash
    with the generated Service / Store / Stats... classes get "Type" added."""
    base = camel(f.name)
    return e.name + base + ("Type" if base in CLASHING else "")
