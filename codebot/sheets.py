"""Spreadsheet projects: realistic workbooks the bot types into WPS / Excel cell by cell,
with formulas for totals, averages, checks and lookups.

A project is {"name", "title", "kind": "sheet", "files": [(rel.xlsx, rows)], "steps": []};
rows are lists of cell texts ("=SUM(B2:B9)" for formulas).
"""

import csv
import os
import random
import re
import zipfile
from xml.etree import ElementTree as ET

FIRST = ["Amina", "Brian", "Cynthia", "David", "Esther", "Felix", "Grace", "Hassan", "Irene", "James", "Kevin",
         "Lucy", "Mercy", "Nelson", "Olive", "Peter", "Queen", "Rose", "Samuel", "Tabitha", "Victor", "Wanjiku"]
LAST = ["Otieno", "Mwangi", "Wanjala", "Kariuki", "Achieng", "Njoroge", "Kiptoo", "Mutua", "Omondi", "Chebet"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def col(n):
    """0 -> A, 25 -> Z, 26 -> AA"""
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def person(rng):
    return f"{rng.choice(FIRST)} {rng.choice(LAST)}"


def money(rng, lo, hi):
    return f"{rng.uniform(lo, hi):.2f}"


def totals_row(label, first, last, cols, start_col, fn="SUM"):
    row = [label] + [""] * (start_col - 1)
    for c in range(start_col, cols):
        row.append(f"={fn}({col(c)}{first}:{col(c)}{last})")
    return row


def budget(rng):
    cats = ["Rent", "Salaries", "Electricity", "Water", "Internet", "Transport", "Marketing", "Stock purchases",
            "Insurance", "Repairs", "Stationery", "Bank charges", "Licences", "Security", "Cleaning"]
    rng.shuffle(cats)
    cats = cats[:rng.randint(10, 15)]
    rows = [["Category"] + MONTHS + ["Total", "Average", "Share"]]
    n = len(cats)
    for i, c in enumerate(cats, start=2):
        base = rng.uniform(2000, 90000)
        rows.append([c] + [f"{base * rng.uniform(0.85, 1.2):.0f}" for _ in MONTHS] +
                    [f"=SUM(B{i}:M{i})", f"=AVERAGE(B{i}:M{i})", f"=N{i}/N{n + 2}"])
    rows.append(totals_row("Total", 2, n + 1, 14, 1))          # B..N
    rows[-1] += ["=AVERAGE(B{0}:M{0})".format(n + 2), "=SUM(P2:P{0})".format(n + 1)]
    rows.append([])
    rows.append(["Biggest cost", f"=INDEX(A2:A{n + 1},MATCH(MAX(N2:N{n + 1}),N2:N{n + 1},0))"])
    rows.append(["Months over budget", f'=COUNTIF(B{n + 2}:M{n + 2},">"&AVERAGE(B{n + 2}:M{n + 2}))'])
    return "monthly-budget", "Monthly Budget", rows


def sales(rng):
    regions = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Nyeri", "Machakos"]
    products = ["Routers", "Cables", "Switches", "Laptops", "Phones", "Printers", "Monitors", "Keyboards"]
    rows = [["Date", "Region", "Product", "Sales rep", "Units", "Unit price", "Revenue", "Discount", "Net", "Target met"]]
    n = rng.randint(60, 110)
    for i in range(2, n + 2):
        rows.append([f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}", rng.choice(regions), rng.choice(products),
                     person(rng), str(rng.randint(1, 120)), money(rng, 15, 950),
                     f"=E{i}*F{i}", f"=IF(G{i}>20000,G{i}*0.05,0)", f"=G{i}-H{i}", f'=IF(I{i}>=15000,"Yes","No")'])
    rows.append(["Total", "", "", "", f"=SUM(E2:E{n + 1})", f"=AVERAGE(F2:F{n + 1})",
                 f"=SUM(G2:G{n + 1})", f"=SUM(H2:H{n + 1})", f"=SUM(I2:I{n + 1})", f'=COUNTIF(J2:J{n + 1},"Yes")'])
    rows.append([])
    rows.append(["Region", "Revenue", "Orders", "Average order"])
    for k, r in enumerate(regions, start=n + 5):
        rows.append([r, f'=SUMIF(B2:B{n + 1},A{k},I2:I{n + 1})', f'=COUNTIF(B2:B{n + 1},A{k})',
                     f"=IF(C{k}=0,0,B{k}/C{k})"])
    return "sales-report", "Sales Report", rows


def inventory(rng):
    items = ["Fibre cable 1km", "ONU device", "Patch cord", "Splitter 1x8", "Router AX3000", "Switch 24-port",
             "Cable ties (100)", "Wall box", "Connector SC/APC", "Drop cable 100m", "Power adapter", "Ladder",
             "Splice tray", "Fusion splicer", "OTDR rental", "Pole bracket", "Duct 50m", "Label printer"]
    rng.shuffle(items)
    items = items[:rng.randint(12, 18)]
    rows = [["SKU", "Item", "Opening", "Received", "Issued", "Closing", "Unit cost", "Stock value", "Reorder level", "Status"]]
    for i, it in enumerate(items, start=2):
        rows.append([f"SKU-{1000 + i * 7}", it, str(rng.randint(0, 200)), str(rng.randint(0, 150)), str(rng.randint(0, 180)),
                     f"=C{i}+D{i}-E{i}", money(rng, 50, 25000), f"=F{i}*G{i}", str(rng.randint(5, 40)),
                     f'=IF(F{i}<0,"Check count",IF(F{i}<=I{i},"Reorder","OK"))'])
    n = len(items)
    rows.append(["", "Total", f"=SUM(C2:C{n + 1})", f"=SUM(D2:D{n + 1})", f"=SUM(E2:E{n + 1})", f"=SUM(F2:F{n + 1})",
                 "", f"=SUM(H2:H{n + 1})", "", f'=COUNTIF(J2:J{n + 1},"Reorder")'])
    return "inventory-valuation", "Inventory Valuation", rows


def payroll(rng):
    rows = [["Employee", "Department", "Basic pay", "Allowances", "Overtime hours", "Overtime pay", "Gross",
             "PAYE", "NSSF", "SHIF", "Net pay"]]
    depts = ["Sales", "Support", "Field", "Finance", "Store", "IT"]
    n = rng.randint(30, 60)
    for i in range(2, n + 2):
        rows.append([person(rng), rng.choice(depts), f"{rng.randint(25, 180) * 1000}", f"{rng.randint(0, 25) * 1000}",
                     str(rng.randint(0, 30)), f"=E{i}*C{i}/176*1.5", f"=C{i}+D{i}+F{i}",
                     f"=IF(G{i}>24000,(G{i}-24000)*0.3,0)", f"=MIN(G{i}*0.06,2160)", f"=G{i}*0.0275",
                     f"=G{i}-H{i}-I{i}-J{i}"])
    rows.append(totals_row("Total", 2, n + 1, 11, 2))
    rows.append([])
    rows.append(["Department", "Staff", "Total net pay"])
    for k, d in enumerate(depts, start=n + 5):
        rows.append([d, f'=COUNTIF(B2:B{n + 1},A{k})', f'=SUMIF(B2:B{n + 1},A{k},K2:K{n + 1})'])
    return "payroll", "Payroll", rows


def grades(rng):
    subjects = ["Maths", "English", "Kiswahili", "Biology", "Chemistry", "Physics", "History", "Computer"]
    rows = [["Student"] + subjects + ["Total", "Average", "Grade", "Rank"]]
    n = rng.randint(35, 55)
    last = col(len(subjects))
    for i in range(2, n + 2):
        tot, avg = col(len(subjects) + 1), col(len(subjects) + 2)
        rows.append([person(rng)] + [str(rng.randint(28, 99)) for _ in subjects] +
                    [f"=SUM(B{i}:{last}{i})", f"=AVERAGE(B{i}:{last}{i})",
                     f'=IF({avg}{i}>=80,"A",IF({avg}{i}>=65,"B",IF({avg}{i}>=50,"C",IF({avg}{i}>=40,"D","E"))))',
                     f"=RANK({tot}{i},{tot}$2:{tot}${n + 1})"])
    rows.append(totals_row("Class average", 2, n + 1, len(subjects) + 3, 1, "AVERAGE"))
    return "class-results", "Class Results", rows


def expenses(rng):
    cats = ["Fuel", "Meals", "Airtime", "Accommodation", "Parking", "Tools", "Office", "Client visit"]
    rows = [["Date", "Description", "Category", "Paid by", "Amount", "VAT", "Total", "Approved"]]
    n = rng.randint(50, 90)
    for i in range(2, n + 2):
        cat = rng.choice(cats)
        rows.append([f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}", f"{cat} - {rng.choice(['site', 'office', 'client', 'trip'])}",
                     cat, person(rng), money(rng, 150, 18000), f"=E{i}*0.16", f"=E{i}+F{i}", rng.choice(["Yes", "Yes", "No"])])
    rows.append(["", "Total", "", "", f"=SUM(E2:E{n + 1})", f"=SUM(F2:F{n + 1})", f"=SUM(G2:G{n + 1})",
                 f'=SUMIF(H2:H{n + 1},"Yes",G2:G{n + 1})'])
    rows.append([])
    rows.append(["Category", "Spent", "Count"])
    for k, c in enumerate(cats, start=n + 5):
        rows.append([c, f'=SUMIF(C2:C{n + 1},A{k},G2:G{n + 1})', f'=COUNTIF(C2:C{n + 1},A{k})'])
    return "expense-claims", "Expense Claims", rows


def tracker(rng):
    tasks = ["Survey site", "Order materials", "Lay duct", "Pull fibre", "Splice joints", "Install ONU",
             "Configure router", "Test speeds", "Customer sign-off", "Update records", "Invoice client",
             "Train staff", "Write report", "Review costs", "Close project"]
    rows = [["Task", "Owner", "Start", "Days", "End", "Progress %", "Budget", "Spent", "Remaining", "Status"]]
    for i, t in enumerate(tasks, start=2):
        rows.append([t, person(rng), f"2026-{rng.randint(1, 11):02d}-{rng.randint(1, 28):02d}", str(rng.randint(1, 20)),
                     f"=C{i}+D{i}", str(rng.choice([0, 10, 25, 50, 75, 90, 100])), money(rng, 5000, 120000),
                     money(rng, 0, 100000), f"=G{i}-H{i}",
                     f'=IF(F{i}=100,"Done",IF(I{i}<0,"Over budget",IF(F{i}=0,"Not started","In progress")))'])
    n = len(tasks)
    rows.append(["Total", "", "", f"=SUM(D2:D{n + 1})", "", f"=AVERAGE(F2:F{n + 1})", f"=SUM(G2:G{n + 1})",
                 f"=SUM(H2:H{n + 1})", f"=SUM(I2:I{n + 1})", f'=COUNTIF(J2:J{n + 1},"Done")'])
    return "project-tracker", "Project Tracker", rows


def customers(rng):
    counties = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Machakos", "Uasin Gishu", "Nyeri"]
    plans = [("Home 10 Mbps", 2500), ("Home 20 Mbps", 3500), ("Home 50 Mbps", 5500), ("Business 100 Mbps", 12000)]
    rows = [["Account", "Customer", "Phone", "Email", "County", "Plan", "Monthly fee", "Months active",
             "Total billed", "Paid", "Balance", "Status"]]
    n = rng.randint(60, 100)
    for i in range(2, n + 2):
        name = person(rng)
        plan, fee = rng.choice(plans)
        months = rng.randint(1, 24)
        paid = fee * months - rng.choice([0, 0, 0, fee, fee * 2])
        rows.append([f"ACC-{20000 + i * 13}", name, f"07{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}",
                     name.lower().replace(" ", ".") + "@mail.com", rng.choice(counties), plan, str(fee), str(months),
                     f"=G{i}*H{i}", str(paid), f"=I{i}-J{i}", f'=IF(K{i}>0,"Owes","Paid up")'])
    rows.append(["", "Total", "", "", "", "", f"=AVERAGE(G2:G{n + 1})", f"=SUM(H2:H{n + 1})", f"=SUM(I2:I{n + 1})",
                 f"=SUM(J2:J{n + 1})", f"=SUM(K2:K{n + 1})", f'=COUNTIF(L2:L{n + 1},"Owes")'])
    rows.append([])
    rows.append(["County", "Customers", "Billed", "Outstanding"])
    for k, c in enumerate(counties, start=n + 5):
        rows.append([c, f'=COUNTIF(E2:E{n + 1},A{k})', f'=SUMIF(E2:E{n + 1},A{k},I2:I{n + 1})',
                     f'=SUMIF(E2:E{n + 1},A{k},K2:K{n + 1})'])
    return "customer-register", "Customer Register", rows


MAKERS = [budget, sales, inventory, payroll, grades, expenses, tracker, customers]

# The data entry projects you can pick in the dashboard (fresh data every time)
CATALOG = {
    "monthly-budget": ("Monthly Budget", budget, "12 months of costs per category, totals, averages, shares"),
    "sales-report": ("Sales Report", sales, "Sales entries with revenue, discount, net and a region summary"),
    "inventory-valuation": ("Inventory Valuation", inventory, "Stock in/out, closing stock, value and reorder status"),
    "payroll": ("Payroll", payroll, "Staff pay with overtime, PAYE, NSSF, SHIF, net pay per department"),
    "class-results": ("Class Results", grades, "Marks per subject with totals, averages, grades and ranks"),
    "expense-claims": ("Expense Claims", expenses, "Expense entries with VAT, approvals and a category summary"),
    "project-tracker": ("Project Tracker", tracker, "Tasks with dates, progress, budget vs spent and status"),
    "customer-register": ("Customer Register", customers, "Customer records with plans, billing, balances per county"),
}


def list_sheet_projects():
    """[{name, title, desc}] - the ready-made ones plus your uploads."""
    out = [{"name": k, "title": t, "desc": d} for k, (t, _, d) in CATALOG.items()]
    for f in uploaded():
        out.append({"name": "upload:" + f, "title": os.path.splitext(f)[0], "desc": "Your uploaded workbook"})
    return out


def sheet_project(name, rng=None):
    """One data entry project by its name (fresh random data for the ready-made ones)."""
    if name.startswith("upload:"):
        return uploaded_project(name[len("upload:"):])
    title, make, _ = CATALOG[name]
    slug, title, rows = make(rng or random.Random())
    return {"name": slug, "title": title, "kind": "sheet", "files": [(f"{slug}.xlsx", rows)], "scaffold": [],
            "steps": [], "language": "spreadsheet", "records": [title]}


def generate(seed=None, count=None):
    rng = random.Random(seed)
    makers = MAKERS[:]
    rng.shuffle(makers)
    picked = makers[:count or rng.randint(1, 3)]
    files, titles = [], []
    for make in picked:
        slug, title, rows = make(rng)
        files.append((f"{slug}.xlsx", rows))
        titles.append(title)
    name = f"{picked[0](random.Random(0))[0]}-workbook"
    return {"name": name, "title": ", ".join(titles), "kind": "sheet", "files": files, "scaffold": [],
            "steps": [], "language": "spreadsheet", "records": titles}


# ------------------------------------------------------------- your own workbooks
UPLOADS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sheets")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
MAX_ROWS, MAX_COLS = 3000, 80


def uploaded():
    """Workbooks you uploaded (Projects > Upload Excel), newest first."""
    if not os.path.isdir(UPLOADS):
        return []
    files = [f for f in os.listdir(UPLOADS) if f.lower().endswith((".xlsx", ".csv")) and not f.startswith("~$")]
    return sorted(files, key=lambda f: -os.path.getmtime(os.path.join(UPLOADS, f)))


def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1, int(ref[len(letters):]) - 1


def read_rows(path):
    """Rows of cell texts from a .csv or the first sheet of an .xlsx (formulas as '=...')."""
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
            return [row[:MAX_COLS] for row in csv.reader(fh)][:MAX_ROWS]
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        sheets = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        if not sheets:
            return []
        root = ET.fromstring(z.read(sheets[0]))
    grid = {}
    for c in root.iter(f"{{{NS['m']}}}c"):
        ref = c.get("r")
        if not ref:
            continue
        col, row = _col_index(ref)
        if row >= MAX_ROWS or col >= MAX_COLS:
            continue
        f = c.find("m:f", NS)
        v = c.find("m:v", NS)
        if f is not None and f.text:
            text = "=" + f.text
        elif c.get("t") == "s" and v is not None:
            text = shared[int(v.text)]
        elif c.get("t") == "inlineStr":
            text = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
        elif c.get("t") == "b" and v is not None:
            text = "TRUE" if v.text == "1" else "FALSE"
        else:
            text = v.text if v is not None and v.text else ""
        if text:
            grid[(row, col)] = text
    if not grid:
        return []
    rows = []
    for r in range(max(k[0] for k in grid) + 1):
        width = max([k[1] + 1 for k in grid if k[0] == r] or [0])
        rows.append([grid.get((r, c), "") for c in range(width)])
    return rows


def uploaded_project(name):
    rows = read_rows(os.path.join(UPLOADS, name))
    stem = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(name)[0].lower()).strip("-") or "workbook"
    return {"name": f"{stem}-work", "title": os.path.splitext(name)[0], "kind": "sheet",
            "files": [(f"{stem}.xlsx", rows)], "scaffold": [], "steps": [], "language": "spreadsheet",
            "records": [name]}


def sheets_cycle(seed=None, selected=None):
    """Forever. With `selected` (names from list_sheet_projects): just those, in turn, with fresh
    data each round. Otherwise: your uploaded workbooks first, then a ready-made one, and round again."""
    rng = random.Random(seed)
    valid = {p["name"] for p in list_sheet_projects()}
    chosen = [n for n in (selected or []) if n in valid]
    while chosen:
        for name in chosen:
            try:
                project = sheet_project(name, random.Random(rng.random()))
            except (OSError, zipfile.BadZipFile, ET.ParseError, ValueError, KeyError):
                continue
            if project["files"][0][1]:
                yield project
    while True:
        for name in uploaded():
            try:
                project = uploaded_project(name)
            except (OSError, zipfile.BadZipFile, ET.ParseError, ValueError):
                continue
            if project["files"][0][1]:
                yield project
        yield generate(seed=rng.random())


def as_text(rows):
    """Rows as tab-separated text (the dashboard shows this while it's typed)."""
    return "\n".join("\t".join(r) for r in rows) + "\n"
