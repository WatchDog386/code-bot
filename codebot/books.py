"""Advanced data entry workbooks: several sheets each (master lists, monthly / quarterly
entry sheets, a summary that pulls everything together with cross-sheet formulas) and a lot
of rows to type.

A workbook is a list of rows; a row [SHEET, "Name"] starts the next sheet. The bot types each
sheet cell by cell, then moves to the next sheet tab (Ctrl+PageDown).
"""

import random

from .sheets import MONTHS, col, money, person

SHEET = "\x00sheet"

REGIONS = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Nyeri", "Machakos"]
COUNTIES = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Machakos", "Uasin Gishu", "Nyeri"]
DEPTS = ["Sales", "Support", "Field", "Finance", "Store", "IT"]


def ref(sheet, cell):
    return f"'{sheet}'!{cell}"


def rng_rows(rng, lo, hi):
    return rng.randint(lo, hi)


def date(rng, month=None):
    return f"2026-{month or rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"


def sheet_names(rows):
    return [r[1] for r in rows if r and r[0] == SHEET]


# --------------------------------------------------------------------------- sales
def sales_book(rng):
    products = [("P-101", "Router AX3000", "Networking", 8500), ("P-102", "Switch 24-port", "Networking", 14500),
                ("P-103", "Fibre cable 1km", "Cabling", 32000), ("P-104", "Patch cord", "Cabling", 450),
                ("P-105", "Laptop 14in", "Computers", 68000), ("P-106", "Desktop i5", "Computers", 54000),
                ("P-107", "Smartphone", "Phones", 23000), ("P-108", "Feature phone", "Phones", 3200),
                ("P-109", "Printer laser", "Office", 27500), ("P-110", "Monitor 24in", "Computers", 16500),
                ("P-111", "Keyboard + mouse", "Office", 2800), ("P-112", "UPS 1kVA", "Power", 12500),
                ("P-113", "Solar kit 200W", "Power", 39000), ("P-114", "Access point", "Networking", 9800)]
    reps = sorted({person(rng) for _ in range(12)})[:10]
    rows = [[SHEET, "Products"], ["Code", "Product", "Category", "Unit price", "Units sold", "Revenue"]]
    np = len(products)
    quarters = ["Q1 Sales", "Q2 Sales", "Q3 Sales", "Q4 Sales"]
    for i, (code, name, cat, price) in enumerate(products, start=2):
        units = "+".join(f"SUMIF({ref(q, 'C:C')},A{i},{ref(q, 'E:E')})" for q in quarters)
        revenue = "+".join(f"SUMIF({ref(q, 'C:C')},A{i},{ref(q, 'G:G')})" for q in quarters)
        rows.append([code, name, cat, str(price), f"={units}", f"={revenue}"])
    rows.append(["", "Total", "", "", f"=SUM(E2:E{np + 1})", f"=SUM(F2:F{np + 1})"])
    for qi, q in enumerate(quarters):
        rows.append([SHEET, q])
        rows.append(["Date", "Region", "Product code", "Product", "Units", "Unit price", "Revenue",
                     "Discount", "Net", "Sales rep", "Target met"])
        n = rng_rows(rng, 90, 150)
        for i in range(2, n + 2):
            code = rng.choice(products)[0]
            rows.append([date(rng, qi * 3 + rng.randint(1, 3)), rng.choice(REGIONS), code,
                         f"=VLOOKUP(C{i},Products!$A$2:$D${np + 1},2,FALSE)", str(rng.randint(1, 40)),
                         f"=VLOOKUP(C{i},Products!$A$2:$D${np + 1},4,FALSE)", f"=E{i}*F{i}",
                         f"=IF(G{i}>100000,G{i}*0.05,IF(G{i}>50000,G{i}*0.02,0))", f"=G{i}-H{i}",
                         rng.choice(reps), f'=IF(I{i}>=60000,"Yes","No")'])
        rows.append(["Total", "", "", "", f"=SUM(E2:E{n + 1})", "", f"=SUM(G2:G{n + 1})",
                     f"=SUM(H2:H{n + 1})", f"=SUM(I2:I{n + 1})", "", f'=COUNTIF(K2:K{n + 1},"Yes")'])
    rows.append([SHEET, "Summary"])
    rows.append(["Region"] + quarters + ["Year total", "Share", "Rank"])
    nr = len(REGIONS)
    for k, r in enumerate(REGIONS, start=2):
        rows.append([r] + [f"=SUMIF({ref(q, 'B:B')},A{k},{ref(q, 'I:I')})" for q in quarters] +
                    [f"=SUM(B{k}:E{k})", f"=F{k}/F{nr + 2}", f"=RANK(F{k},$F$2:$F${nr + 1})"])
    rows.append(["Total"] + [f"=SUM({col(c)}2:{col(c)}{nr + 1})" for c in range(1, 6)] + ["=SUM(G2:G%d)" % (nr + 1)])
    rows.append([])
    rows.append(["Sales rep", "Orders", "Net sales", "Average order"])
    for k, rep in enumerate(reps, start=nr + 5):
        orders = "+".join(f"COUNTIF({ref(q, 'J:J')},A{k})" for q in quarters)
        net = "+".join(f"SUMIF({ref(q, 'J:J')},A{k},{ref(q, 'I:I')})" for q in quarters)
        rows.append([rep, f"={orders}", f"={net}", f"=IF(B{k}=0,0,C{k}/B{k})"])
    rows.append([])
    rows.append(["Best product", f"=INDEX(Products!B2:B{np + 1},MATCH(MAX(Products!F2:F{np + 1}),Products!F2:F{np + 1},0))"])
    rows.append(["Best region", f"=INDEX(A2:A{nr + 1},MATCH(MAX(F2:F{nr + 1}),F2:F{nr + 1},0))"])
    return "sales-report", "Sales Report", rows


# ------------------------------------------------------------------------- payroll
def payroll_book(rng):
    n = rng_rows(rng, 40, 70)
    staff = [(f"EMP-{100 + i}", person(rng), rng.choice(DEPTS), rng.randint(25, 180) * 1000) for i in range(n)]
    rows = [[SHEET, "Staff"], ["Staff no", "Name", "Department", "Basic pay", "Bank", "Account no", "Start date"]]
    for i, (no, name, dept, basic) in enumerate(staff, start=2):
        rows.append([no, name, dept, str(basic), rng.choice(["KCB", "Equity", "Co-op", "NCBA", "Absa"]),
                     str(rng.randint(10 ** 9, 10 ** 10 - 1)), date(rng)])
    months = ["January", "February", "March", "April", "May", "June"]
    for m in months:
        rows.append([SHEET, m])
        rows.append(["Staff no", "Name", "Department", "Basic pay", "Allowances", "Overtime hours", "Overtime pay",
                     "Gross", "PAYE", "NSSF", "SHIF", "Housing levy", "Net pay"])
        last = n + 1
        for i, (no, *_rest) in enumerate(staff, start=2):
            rows.append([no, f"=VLOOKUP(A{i},Staff!$A$2:$D${last},2,FALSE)",
                         f"=VLOOKUP(A{i},Staff!$A$2:$D${last},3,FALSE)", f"=VLOOKUP(A{i},Staff!$A$2:$D${last},4,FALSE)",
                         str(rng.randint(0, 25) * 1000), str(rng.randint(0, 30)), f"=F{i}*D{i}/176*1.5",
                         f"=D{i}+E{i}+G{i}", f"=IF(H{i}>24000,(H{i}-24000)*0.3,0)", f"=MIN(H{i}*0.06,2160)",
                         f"=H{i}*0.0275", f"=H{i}*0.015", f"=H{i}-I{i}-J{i}-K{i}-L{i}"])
        rows.append(["Total", "", ""] + [f"=SUM({col(c)}2:{col(c)}{last})" for c in range(3, 13)])
    rows.append([SHEET, "Summary"])
    rows.append(["Department", "Staff"] + months + ["Six months"])
    for k, d in enumerate(DEPTS, start=2):
        rows.append([d, f"=COUNTIF(Staff!C:C,A{k})"] +
                    [f"=SUMIF({ref(m, 'C:C')},A{k},{ref(m, 'M:M')})" for m in months] + [f"=SUM(C{k}:H{k})"])
    nd = len(DEPTS)
    rows.append(["Total", f"=SUM(B2:B{nd + 1})"] + [f"=SUM({col(c)}2:{col(c)}{nd + 1})" for c in range(2, 9)])
    rows.append([])
    rows.append(["Month", "Gross", "PAYE", "Net pay"])
    for k, m in enumerate(months, start=nd + 5):
        rows.append([m, f"=SUM({ref(m, 'H2:H%d' % (n + 1))})", f"=SUM({ref(m, 'I2:I%d' % (n + 1))})",
                     f"=SUM({ref(m, 'M2:M%d' % (n + 1))})"])
    return "payroll", "Payroll", rows


# ----------------------------------------------------------------------- inventory
def inventory_book(rng):
    items = ["Fibre cable 1km", "ONU device", "Patch cord", "Splitter 1x8", "Router AX3000", "Switch 24-port",
             "Cable ties (100)", "Wall box", "Connector SC/APC", "Drop cable 100m", "Power adapter", "Ladder",
             "Splice tray", "Pole bracket", "Duct 50m", "Label printer", "Crimping tool", "Fibre cleaver",
             "Optical meter", "Cabinet 9U"]
    rows = [[SHEET, "Items"], ["SKU", "Item", "Unit", "Unit cost", "Reorder level", "Opening stock"]]
    ni = len(items)
    for i, it in enumerate(items, start=2):
        rows.append([f"SKU-{1000 + i * 7}", it, rng.choice(["pcs", "roll", "box", "set"]), money(rng, 50, 25000),
                     str(rng.randint(5, 40)), str(rng.randint(10, 200))])
    stores = ["Main store", "Site A", "Site B", "Van 1", "Van 2"]
    for name, verb in (("Receipts", "Supplier"), ("Issues", "Issued to")):
        rows.append([SHEET, name])
        rows.append(["Date", "Ref no", "SKU", "Item", "Quantity", "Unit cost", "Value", verb, "Store"])
        n = rng_rows(rng, 100, 170)
        for i in range(2, n + 2):
            sku = f"SKU-{1000 + rng.randint(2, ni + 1) * 7}"
            who = rng.choice(["Safaricom Ltd", "Huawei Ke", "Tech Supplies", "Cable World"]) if name == "Receipts" \
                else person(rng)
            rows.append([date(rng), f"{name[:3].upper()}-{3000 + i}", sku,
                         f"=VLOOKUP(C{i},Items!$A$2:$D${ni + 1},2,FALSE)", str(rng.randint(1, 30 if name == 'Issues' else 60)),
                         f"=VLOOKUP(C{i},Items!$A$2:$D${ni + 1},4,FALSE)", f"=E{i}*F{i}", who, rng.choice(stores)])
        rows.append(["Total", "", "", "", f"=SUM(E2:E{n + 1})", "", f"=SUM(G2:G{n + 1})"])
    rows.append([SHEET, "Stock"])
    rows.append(["SKU", "Item", "Opening", "Received", "Issued", "Closing", "Unit cost", "Stock value", "Reorder level", "Status"])
    for i in range(2, ni + 2):
        rows.append([f"=Items!A{i}", f"=Items!B{i}", f"=Items!F{i}", f"=SUMIF(Receipts!C:C,A{i},Receipts!E:E)",
                     f"=SUMIF(Issues!C:C,A{i},Issues!E:E)", f"=C{i}+D{i}-E{i}", f"=Items!D{i}", f"=F{i}*G{i}",
                     f"=Items!E{i}", f'=IF(F{i}<0,"Check count",IF(F{i}<=I{i},"Reorder","OK"))'])
    rows.append(["", "Total", f"=SUM(C2:C{ni + 1})", f"=SUM(D2:D{ni + 1})", f"=SUM(E2:E{ni + 1})",
                 f"=SUM(F2:F{ni + 1})", "", f"=SUM(H2:H{ni + 1})", "", f'=COUNTIF(J2:J{ni + 1},"Reorder")'])
    rows.append([SHEET, "Summary"])
    rows.append(["Store", "Received value", "Issued value", "Issues count"])
    for k, s in enumerate(stores, start=2):
        rows.append([s, f"=SUMIF(Receipts!I:I,A{k},Receipts!G:G)", f"=SUMIF(Issues!I:I,A{k},Issues!G:G)",
                     f"=COUNTIF(Issues!I:I,A{k})"])
    rows.append(["Total", f"=SUM(B2:B{len(stores) + 1})", f"=SUM(C2:C{len(stores) + 1})", f"=SUM(D2:D{len(stores) + 1})"])
    rows.append([])
    rows.append(["Stock value", f"=Stock!H{ni + 2}"])
    rows.append(["Items to reorder", f"=Stock!J{ni + 2}"])
    rows.append(["Most issued item", f"=INDEX(Stock!B2:B{ni + 1},MATCH(MAX(Stock!E2:E{ni + 1}),Stock!E2:E{ni + 1},0))"])
    return "inventory-valuation", "Inventory Valuation", rows


# ------------------------------------------------------------------- class results
def grades_book(rng):
    subjects = ["Maths", "English", "Kiswahili", "Biology", "Chemistry", "Physics", "History", "Computer"]
    n = rng_rows(rng, 40, 60)
    students = [(f"ADM-{2400 + i}", person(rng), rng.choice(["Form 3 East", "Form 3 West", "Form 3 North"]))
                for i in range(n)]
    rows = [[SHEET, "Students"], ["Adm no", "Name", "Stream", "Gender", "Parent phone"]]
    for no, name, stream in students:
        rows.append([no, name, stream, rng.choice(["F", "M"]), f"07{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}"])
    terms = ["Term 1", "Term 2", "Term 3"]
    ns = len(subjects)
    tot, avg, grd, rnk = col(ns + 2), col(ns + 3), col(ns + 4), col(ns + 5)
    for t in terms:
        rows.append([SHEET, t])
        rows.append(["Adm no", "Name"] + subjects + ["Total", "Average", "Grade", "Rank"])
        for i, (no, *_r) in enumerate(students, start=2):
            rows.append([no, f"=VLOOKUP(A{i},Students!$A$2:$B${n + 1},2,FALSE)"] +
                        [str(rng.randint(25, 99)) for _ in subjects] +
                        [f"=SUM(C{i}:{col(ns + 1)}{i})", f"=AVERAGE(C{i}:{col(ns + 1)}{i})",
                         f'=IF({avg}{i}>=80,"A",IF({avg}{i}>=65,"B",IF({avg}{i}>=50,"C",IF({avg}{i}>=40,"D","E"))))',
                         f"=RANK({tot}{i},{tot}$2:{tot}${n + 1})"])
        rows.append(["", "Subject mean"] + [f"=AVERAGE({col(c)}2:{col(c)}{n + 1})" for c in range(2, ns + 4)])
    rows.append([SHEET, "Summary"])
    rows.append(["Adm no", "Name"] + [f"{t} average" for t in terms] + ["Year average", "Trend", "Year rank"])
    for i, (no, *_r) in enumerate(students, start=2):
        rows.append([no, f"=Students!B{i}"] + [f"={ref(t, avg + str(i))}" for t in terms] +
                    [f"=AVERAGE(C{i}:E{i})", f'=IF(E{i}>C{i},"Improving",IF(E{i}<C{i},"Dropping","Steady"))',
                     f"=RANK(F{i},$F$2:$F${n + 1})"])
    rows.append([])
    rows.append(["Grade", "Term 1", "Term 2", "Term 3"])
    for k, g in enumerate("ABCDE", start=n + 4):
        rows.append([g] + [f"=COUNTIF({ref(t, grd + ':' + grd)},A{k})" for t in terms])
    return "class-results", "Class Results", rows


# -------------------------------------------------------------------------- budget
def budget_book(rng):
    cats = ["Rent", "Salaries", "Electricity", "Water", "Internet", "Transport", "Marketing", "Stock purchases",
            "Insurance", "Repairs", "Stationery", "Bank charges", "Licences", "Security", "Cleaning", "Training"]
    nc = len(cats)
    plan = {c: rng.uniform(2000, 90000) for c in cats}
    rows = []
    for name, spread in (("Budget", (0.95, 1.05)), ("Actual", (0.75, 1.3))):
        rows.append([SHEET, name])
        rows.append(["Category"] + MONTHS + ["Total"])
        for i, c in enumerate(cats, start=2):
            rows.append([c] + [f"{plan[c] * rng.uniform(*spread):.0f}" for _ in MONTHS] + [f"=SUM(B{i}:M{i})"])
        rows.append(["Total"] + [f"=SUM({col(k)}2:{col(k)}{nc + 1})" for k in range(1, 14)])
    rows.append([SHEET, "Variance"])
    rows.append(["Category"] + MONTHS + ["Total", "Variance %", "Status"])
    for i in range(2, nc + 3):
        rows.append([f"=Budget!A{i}"] + [f"=Actual!{col(k)}{i}-Budget!{col(k)}{i}" for k in range(1, 14)] +
                    [f"=IF(Budget!N{i}=0,0,N{i}/Budget!N{i})", f'=IF(O{i}>0.05,"Over",IF(O{i}<-0.05,"Under","On track"))'])
    rows.append([SHEET, "Payments"])
    rows.append(["Date", "Voucher", "Category", "Paid to", "Amount", "Method", "Month"])
    n = rng_rows(rng, 120, 180)
    for i in range(2, n + 2):
        m = rng.randint(1, 12)
        rows.append([date(rng, m), f"PV-{5000 + i}", rng.choice(cats), person(rng), money(rng, 500, 60000),
                     rng.choice(["M-Pesa", "Bank transfer", "Cheque", "Cash"]), MONTHS[m - 1]])
    rows.append(["Total", "", "", "", f"=SUM(E2:E{n + 1})"])
    rows.append([SHEET, "Summary"])
    rows.append(["Category", "Budget", "Actual", "Variance", "Payments logged", "Payments value"])
    for i, c in enumerate(cats, start=2):
        rows.append([c, f"=Budget!N{i}", f"=Actual!N{i}", f"=C{i}-B{i}", f"=COUNTIF(Payments!C:C,A{i})",
                     f"=SUMIF(Payments!C:C,A{i},Payments!E:E)"])
    rows.append(["Total"] + [f"=SUM({col(k)}2:{col(k)}{nc + 1})" for k in range(1, 6)])
    rows.append([])
    rows.append(["Biggest overspend", f"=INDEX(A2:A{nc + 1},MATCH(MAX(D2:D{nc + 1}),D2:D{nc + 1},0))"])
    rows.append(["Categories over budget", f'=COUNTIF(Variance!P2:P{nc + 1},"Over")'])
    return "monthly-budget", "Monthly Budget", rows


# ------------------------------------------------------------------------ expenses
def expenses_book(rng):
    cats = ["Fuel", "Meals", "Airtime", "Accommodation", "Parking", "Tools", "Office", "Client visit"]
    staff = sorted({person(rng) for _ in range(16)})[:12]
    rows = [[SHEET, "Staff"], ["Name", "Department", "Monthly limit"]]
    for s in staff:
        rows.append([s, rng.choice(DEPTS), str(rng.choice([15000, 20000, 30000, 50000]))])
    ns = len(staff)
    months = ["January", "February", "March", "April"]
    for mi, m in enumerate(months, start=1):
        rows.append([SHEET, m])
        rows.append(["Date", "Claim no", "Staff", "Department", "Category", "Description", "Amount", "VAT", "Total", "Approved"])
        n = rng_rows(rng, 70, 120)
        for i in range(2, n + 2):
            cat = rng.choice(cats)
            rows.append([date(rng, mi), f"CL-{mi}{1000 + i}", rng.choice(staff),
                         f"=VLOOKUP(C{i},Staff!$A$2:$B${ns + 1},2,FALSE)", cat,
                         f"{cat} - {rng.choice(['site visit', 'office', 'client meeting', 'trip', 'install'])}",
                         money(rng, 150, 18000), f"=G{i}*0.16", f"=G{i}+H{i}", rng.choice(["Yes", "Yes", "Yes", "No"])])
        rows.append(["Total", "", "", "", "", "", f"=SUM(G2:G{n + 1})", f"=SUM(H2:H{n + 1})", f"=SUM(I2:I{n + 1})",
                     f'=COUNTIF(J2:J{n + 1},"Yes")'])
    rows.append([SHEET, "Summary"])
    rows.append(["Staff"] + months + ["Total", "Limit (4 months)", "Over limit"])
    for k, s in enumerate(staff, start=2):
        rows.append([s] + [f'=SUMIFS({ref(m, "I:I")},{ref(m, "C:C")},A{k},{ref(m, "J:J")},"Yes")' for m in months] +
                    [f"=SUM(B{k}:E{k})", f"=VLOOKUP(A{k},Staff!$A$2:$C${ns + 1},3,FALSE)*4", f'=IF(F{k}>G{k},"Yes","No")'])
    rows.append([])
    rows.append(["Category"] + months + ["Total"])
    for k, c in enumerate(cats, start=ns + 4):
        rows.append([c] + [f"=SUMIF({ref(m, 'E:E')},A{k},{ref(m, 'I:I')})" for m in months] + [f"=SUM(B{k}:E{k})"])
    return "expense-claims", "Expense Claims", rows


# ------------------------------------------------------------------ project tracker
def tracker_book(rng):
    tasks = ["Survey site", "Order materials", "Lay duct", "Pull fibre", "Splice joints", "Install ONU",
             "Configure router", "Test speeds", "Customer sign-off", "Update records", "Invoice client",
             "Train staff", "Write report", "Review costs", "Close project", "Permit application",
             "Trench digging", "Pole installation"]
    team = sorted({person(rng) for _ in range(10)})[:8]
    rows = [[SHEET, "Tasks"], ["Task ID", "Task", "Owner", "Start", "Days", "End", "Budget", "Hours logged",
                               "Cost so far", "Remaining", "Progress %", "Status"]]
    nt = len(tasks)
    for i, t in enumerate(tasks, start=2):
        rows.append([f"T-{i - 1:02d}", t, rng.choice(team), date(rng, rng.randint(1, 10)), str(rng.randint(1, 20)),
                     f"=D{i}+E{i}", money(rng, 20000, 250000), f"=SUMIF(Timesheet!C:C,A{i},Timesheet!E:E)",
                     f"=SUMIF(Timesheet!C:C,A{i},Timesheet!G:G)+SUMIF(Costs!C:C,A{i},Costs!F:F)", f"=G{i}-I{i}",
                     str(rng.choice([0, 10, 25, 50, 75, 90, 100])),
                     f'=IF(K{i}=100,"Done",IF(J{i}<0,"Over budget",IF(K{i}=0,"Not started","In progress")))'])
    rows.append(["", "Total", "", "", f"=SUM(E2:E{nt + 1})", "", f"=SUM(G2:G{nt + 1})", f"=SUM(H2:H{nt + 1})",
                 f"=SUM(I2:I{nt + 1})", f"=SUM(J2:J{nt + 1})", f"=AVERAGE(K2:K{nt + 1})", f'=COUNTIF(L2:L{nt + 1},"Done")'])
    rows.append([SHEET, "Team"])
    rows.append(["Name", "Role", "Hourly rate"])
    for p in team:
        rows.append([p, rng.choice(["Technician", "Engineer", "Supervisor", "Driver"]), str(rng.choice([450, 600, 850, 1200]))])
    nm = len(team)
    rows.append([SHEET, "Timesheet"])
    rows.append(["Date", "Person", "Task ID", "Task", "Hours", "Rate", "Cost", "Notes"])
    n = rng_rows(rng, 140, 200)
    for i in range(2, n + 2):
        rows.append([date(rng, rng.randint(1, 10)), rng.choice(team), f"T-{rng.randint(1, nt):02d}",
                     f"=VLOOKUP(C{i},Tasks!$A$2:$B${nt + 1},2,FALSE)", str(rng.choice([1, 2, 3, 4, 6, 8])),
                     f"=VLOOKUP(B{i},Team!$A$2:$C${nm + 1},3,FALSE)", f"=E{i}*F{i}",
                     rng.choice(["", "on site", "waiting for parts", "done", "rework", "with client"])])
    rows.append(["Total", "", "", "", f"=SUM(E2:E{n + 1})", "", f"=SUM(G2:G{n + 1})"])
    rows.append([SHEET, "Costs"])
    rows.append(["Date", "Item", "Task ID", "Supplier", "Quantity", "Amount"])
    n = rng_rows(rng, 60, 100)
    for i in range(2, n + 2):
        rows.append([date(rng, rng.randint(1, 10)), rng.choice(["Cable", "Ducts", "Connectors", "Transport", "Hire",
                     "Fuel", "Permits", "Meals"]), f"T-{rng.randint(1, nt):02d}",
                     rng.choice(["Cable World", "Tech Supplies", "Hardware Ltd", "County office"]),
                     str(rng.randint(1, 20)), money(rng, 300, 40000)])
    rows.append(["Total", "", "", "", "", f"=SUM(F2:F{n + 1})"])
    rows.append([SHEET, "Summary"])
    rows.append(["Person", "Hours", "Cost", "Tasks owned"])
    for k, p in enumerate(team, start=2):
        rows.append([p, f"=SUMIF(Timesheet!B:B,A{k},Timesheet!E:E)", f"=SUMIF(Timesheet!B:B,A{k},Timesheet!G:G)",
                     f"=COUNTIF(Tasks!C:C,A{k})"])
    rows.append(["Total", f"=SUM(B2:B{nm + 1})", f"=SUM(C2:C{nm + 1})", f"=SUM(D2:D{nm + 1})"])
    rows.append([])
    rows.append(["Project budget", f"=Tasks!G{nt + 2}"])
    rows.append(["Spent so far", f"=Tasks!I{nt + 2}"])
    rows.append(["Budget used", f"=B{nm + 5}/B{nm + 4}"])
    rows.append(["Tasks over budget", f'=COUNTIF(Tasks!L2:L{nt + 1},"Over budget")'])
    return "project-tracker", "Project Tracker", rows


# ---------------------------------------------------------------- customer register
def customers_book(rng):
    plans = [("Home 10 Mbps", 2500), ("Home 20 Mbps", 3500), ("Home 50 Mbps", 5500), ("Business 100 Mbps", 12000)]
    rows = [[SHEET, "Plans"], ["Plan", "Monthly fee", "Customers", "Monthly revenue"]]
    for k, (p, fee) in enumerate(plans, start=2):
        rows.append([p, str(fee), f"=COUNTIF(Customers!F:F,A{k})", f"=B{k}*C{k}"])
    np = len(plans)
    rows.append([SHEET, "Customers"])
    rows.append(["Account", "Customer", "Phone", "Email", "County", "Plan", "Monthly fee", "Joined",
                 "Months active", "Total billed", "Paid", "Balance", "Status"])
    n = rng_rows(rng, 120, 180)
    accounts = []
    for i in range(2, n + 2):
        name = person(rng)
        acc = f"ACC-{20000 + i * 13}"
        accounts.append(acc)
        rows.append([acc, name, f"07{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}",
                     name.lower().replace(" ", ".") + f"{rng.randint(1, 99)}@mail.com", rng.choice(COUNTIES),
                     rng.choice(plans)[0], f"=VLOOKUP(F{i},Plans!$A$2:$B${np + 1},2,FALSE)",
                     date(rng, rng.randint(1, 10)), str(rng.randint(1, 12)), f"=G{i}*I{i}",
                     f"=SUMIF(Payments!B:B,A{i},Payments!D:D)", f"=J{i}-K{i}",
                     f'=IF(L{i}>G{i},"Disconnect",IF(L{i}>0,"Owes","Paid up"))'])
    rows.append(["", "Total", "", "", "", "", f"=AVERAGE(G2:G{n + 1})", "", f"=SUM(I2:I{n + 1})",
                 f"=SUM(J2:J{n + 1})", f"=SUM(K2:K{n + 1})", f"=SUM(L2:L{n + 1})", f'=COUNTIF(M2:M{n + 1},"Owes")'])
    rows.append([SHEET, "Payments"])
    rows.append(["Date", "Account", "Customer", "Amount", "Method", "Receipt no"])
    m = rng_rows(rng, 180, 260)
    for i in range(2, m + 2):
        rows.append([date(rng, rng.randint(1, 11)), rng.choice(accounts),
                     f"=VLOOKUP(B{i},Customers!$A$2:$B${n + 1},2,FALSE)", str(rng.choice([2500, 3500, 5500, 7000, 12000])),
                     rng.choice(["M-Pesa", "M-Pesa", "Bank", "Card"]), f"RC{rng.randint(100000, 999999)}"])
    rows.append(["Total", "", "", f"=SUM(D2:D{m + 1})"])
    rows.append([SHEET, "Summary"])
    rows.append(["County", "Customers", "Billed", "Paid", "Outstanding", "To disconnect"])
    for k, c in enumerate(COUNTIES, start=2):
        rows.append([c, f"=COUNTIF(Customers!E:E,A{k})", f"=SUMIF(Customers!E:E,A{k},Customers!J:J)",
                     f"=SUMIF(Customers!E:E,A{k},Customers!K:K)", f"=SUMIF(Customers!E:E,A{k},Customers!L:L)",
                     f'=COUNTIFS(Customers!E:E,A{k},Customers!M:M,"Disconnect")'])
    nc = len(COUNTIES)
    rows.append(["Total"] + [f"=SUM({col(k)}2:{col(k)}{nc + 1})" for k in range(1, 6)])
    rows.append([])
    rows.append(["Payment method", "Payments", "Amount"])
    for k, meth in enumerate(["M-Pesa", "Bank", "Card"], start=nc + 5):
        rows.append([meth, f"=COUNTIF(Payments!E:E,A{k})", f"=SUMIF(Payments!E:E,A{k},Payments!D:D)"])
    return "customer-register", "Customer Register", rows


BOOKS = {
    "monthly-budget": ("Monthly Budget", budget_book,
                       "Budget and Actual for 16 categories x 12 months, Variance sheet, 120-180 payments, Summary"),
    "sales-report": ("Sales Report", sales_book,
                     "Products list, four quarterly sales sheets (90-150 entries each), Summary by region and rep"),
    "inventory-valuation": ("Inventory Valuation", inventory_book,
                            "Items list, Receipts and Issues logs (100-170 entries each), Stock valuation, Summary"),
    "payroll": ("Payroll", payroll_book,
                "Staff list (40-70), six monthly payroll sheets with PAYE/NSSF/SHIF/housing levy, Summary"),
    "class-results": ("Class Results", grades_book,
                      "Students list (40-60), three term sheets with 8 subjects, grades, ranks, year Summary"),
    "expense-claims": ("Expense Claims", expenses_book,
                       "Staff limits, four monthly claim sheets (70-120 claims each), Summary per staff and category"),
    "project-tracker": ("Project Tracker", tracker_book,
                        "Tasks, Team rates, Timesheet (140-200 entries), Costs log, Summary with budget used"),
    "customer-register": ("Customer Register", customers_book,
                          "Plans, 120-180 customers, 180-260 payments, balances and a county Summary"),
}
