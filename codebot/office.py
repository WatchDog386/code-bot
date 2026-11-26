"""Spreadsheets in WPS Office (or Excel / LibreOffice Calc): create a workbook, open it in
the office app, and let the bot type cells, formulas and formatting into it like a person.

OfficeEditor has the same shape as the other editors (open / focus / region / begin_project
/ begin_file / end_file), so the bot's loop drives it the same way it drives VS Code.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import date
from xml.sax.saxutils import escape, quoteattr

import pyautogui

from .editor import MARKER, _WindowsFocus, active_window_title, place_window

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"


# ------------------------------------------------------------------- blank workbook
_CT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>"""
_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
_WB = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="{name}" sheetId="1" r:id="rId1"/></sheets></workbook>"""
_WB_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""
_SHEET = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>"""
_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


_NUMFMT = {"gen": 0, "money": 4, "int": 3, "pct": 165, "date": 164, "dec": 166}


def _styles(keys):
    """styles.xml with one cell format per (fmt, role) in `keys`; returns (xml, {key: index})."""
    xfs = ['<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>']
    index = {}
    for fmt, role in keys:
        font, fill, border = {"head": (1, 2, 1), "total": (1, 0, 2)}.get(role, (0, 0, 0))
        xfs.append(f'<xf numFmtId="{_NUMFMT[fmt]}" fontId="{font}" fillId="{fill}" borderId="{border}" xfId="0" '
                   'applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1"/>')
        index[(fmt, role)] = len(xfs) - 1
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<numFmts count="3"><numFmt numFmtId="164" formatCode="yyyy-mm-dd"/>'
           '<numFmt numFmtId="165" formatCode="0.0%"/><numFmt numFmtId="166" formatCode="0.0"/></numFmts>'
           '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
           '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
           '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
           '<fill><patternFill patternType="solid"><fgColor rgb="FFDDEBF7"/><bgColor indexed="64"/></patternFill></fill></fills>'
           '<borders count="3"><border><left/><right/><top/><bottom/><diagonal/></border>'
           '<border><left/><right/><top/><bottom style="thin"><color rgb="FF8EA9DB"/></bottom><diagonal/></border>'
           '<border><left/><right/><top style="thin"><color auto="1"/></top><bottom/><diagonal/></border></borders>'
           '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
           f'<cellXfs count="{len(xfs)}">' + "".join(xfs) + '</cellXfs>'
           '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
           '<dxfs count="3">'
           '<dxf><font><b/><color rgb="FF9C0006"/></font><fill><patternFill patternType="solid"><fgColor rgb="FFFFC7CE"/></patternFill></fill></dxf>'
           '<dxf><font><b/><color rgb="FF9C6500"/></font><fill><patternFill patternType="solid"><fgColor rgb="FFFFEB9C"/></patternFill></fill></dxf>'
           '<dxf><font><b/><color rgb="FF006100"/></font><fill><patternFill patternType="solid"><fgColor rgb="FFC6EFCE"/></patternFill></fill></dxf>'
           '</dxfs></styleSheet>')
    return xml, index


def _sheet_xml(look, index, rows=None):
    from .sheets import col
    if not look:
        look = {"cells": {}, "widths": {}}
    cols = "".join(f'<col min="{c + 1}" max="{c + 1}" width="{w}" customWidth="1"/>'
                   for c, w in sorted(look["widths"].items()))
    by_row = {}
    for (r, c), key in look["cells"].items():
        by_row.setdefault(r, {})[c] = (index[key], "", key[0])
    if rows is not None:
        for r, values in enumerate(rows):
            for c, value in enumerate(values):
                value = str(value or "")
                if value == "":
                    continue
                key = look["cells"].get((r, c))
                by_row.setdefault(r, {})[c] = (index.get(key, 0), value, key[0] if key else "gen")

    def cell_xml(r, c, entry):
        style, value, fmt = entry
        ref = f"{col(c)}{r + 1}"
        style_attr = f' s="{style}"' if style else ""
        if not value:
            return f'<c r="{ref}"{style_attr}/>'
        if value.startswith("="):
            return f'<c r="{ref}"{style_attr}><f>{escape(value[1:])}</f><v></v></c>'
        if fmt == "date":
            try:
                serial = (date.fromisoformat(value) - date(1899, 12, 30)).days
                return f'<c r="{ref}"{style_attr}><v>{serial}</v></c>'
            except ValueError:
                try:
                    return f'<c r="{ref}"{style_attr}><v>{float(value)}</v></c>'
                except ValueError:
                    pass
        if fmt in ("money", "int", "pct", "dec"):
            try:
                number = float(value.replace(",", ""))
                numeric = str(int(number)) if number.is_integer() else repr(number)
                return f'<c r="{ref}"{style_attr}><v>{numeric}</v></c>'
            except ValueError:
                pass
        return (f'<c r="{ref}"{style_attr} t="inlineStr"><is><t xml:space="preserve">'
                f'{escape(value)}</t></is></c>')

    sheet_rows = "".join(
        f'<row r="{r + 1}">' + "".join(cell_xml(r, c, entry) for c, entry in sorted(cells.items())) + "</row>"
        for r, cells in sorted(by_row.items()))
    freeze_rows = int(look.get("freeze_rows", 0) or 0)
    if freeze_rows:
        active = f"A{freeze_rows + 1}"
        views = (f'<sheetViews><sheetView workbookViewId="0"><pane ySplit="{freeze_rows}" '
                 f'topLeftCell="{active}" activePane="bottomLeft" state="frozen"/>'
                 f'<selection pane="bottomLeft" activeCell="{active}" sqref="{active}"/></sheetView></sheetViews>')
    else:
        views = '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
    auto_filter = (f'<autoFilter ref="{escape(look["filter_ref"])}"/>'
                   if look.get("filter_ref") else "")
    conditional = []
    for group in look.get("conditional", []):
        rules = []
        for priority, rule in enumerate(group["rules"], 1):
            cell = f'${group["column"]}{group["first_row"]}'
            formula = f'AND({cell}="{rule["value"]}",{cell}<>"")'
            formula_xml = escape(formula).replace('"', '&quot;')
            rules.append(f'<cfRule type="expression" dxfId="{int(rule["style"])}" priority="{priority}">'
                         f'<formula>{formula_xml}</formula></cfRule>')
        conditional.append(f'<conditionalFormatting sqref="{escape(group["ref"])}">'
                           + "".join(rules) + '</conditionalFormatting>')
    validations = []
    for validation in look.get("validations", []):
        formula = '"' + ",".join(validation["values"]) + '"'
        formula_xml = escape(formula).replace('"', '&quot;')
        validations.append(f'<dataValidation type="list" allowBlank="1" showErrorMessage="1" '
                           f'errorStyle="stop" sqref="{escape(validation["ref"])}">'
                           f'<formula1>{formula_xml}</formula1></dataValidation>')
    dvs = (f'<dataValidations count="{len(validations)}">' + "".join(validations) + '</dataValidations>'
           if validations else "")
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            + views + '<sheetFormatPr defaultRowHeight="15"/>'
            + (f"<cols>{cols}</cols>" if cols else "") + f"<sheetData>{sheet_rows}</sheetData>"
            + auto_filter + "".join(conditional) + dvs + "</worksheet>")


def _clean_sheet_names(names):
    """Excel-safe, unique sheet names (<=31 chars, no []:*?/\\ characters)."""
    out, seen = [], set()
    for name in names:
        text = re.sub(r"[\[\]:*?/\\]", " ", str(name or "")).strip() or "Sheet"
        text = text[:31]
        base, suffix = text, 2
        while text.casefold() in seen:
            tail = f" ({suffix})"
            text = base[:31 - len(tail)] + tail
            suffix += 1
        seen.add(text.casefold())
        out.append(text)
    return out


def blank_xlsx(path, sheet="Sheet1", sheets=None, book=None, populate=False):
    """An empty .xlsx with one sheet per name in `sheets` (or just `sheet`). With `book` (the rows
    the bot will type) every sheet is laid out in advance: column widths, number formats
    (money, %, dates), a styled header row per table and bold total rows. `populate=True` writes
    the cells and formulas directly, which lets spreadsheet projects finish while the user has
    the keyboard in another application."""
    looks = {}
    sheet_rows = {}
    if book:
        from .books import sheet_looks, split_sheets
        looks = sheet_looks(book, default=sheet)
        sheets = list(looks)
        if populate:
            sheet_rows = dict(split_sheets(book, default=sheet))
    raw_names = list(sheets or [sheet])
    names = _clean_sheet_names(raw_names)
    keys = sorted({k for lk in looks.values() for k in lk["cells"].values()})
    styles_xml, index = _styles(keys)
    ct = _CT.replace('<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>',
                     "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                             for i in range(1, len(names) + 1)))
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' +
          "".join(f'<sheet name={quoteattr(n)} sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(names, 1)) +
          '</sheets><calcPr calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/></workbook>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
            "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
                    for i in range(1, len(names) + 1)) +
            f'<Relationship Id="rId{len(names) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            "</Relationships>")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        for i, (raw, n) in enumerate(zip(raw_names, names), 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml",
                       _sheet_xml(looks.get(raw), index, sheet_rows.get(raw) if populate else None))
        z.writestr("xl/styles.xml", styles_xml)
    return path


def _old_blank_xlsx(path, sheet="Sheet1"):
    """Write an empty, valid .xlsx workbook (no extra libraries needed)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CT)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("xl/workbook.xml", _WB.format(name=sheet[:31].replace("&", "and")))
        z.writestr("xl/_rels/workbook.xml.rels", _WB_RELS)
        z.writestr("xl/worksheets/sheet1.xml", _SHEET)
        z.writestr("xl/styles.xml", _STYLES)
    return path


# -------------------------------------------------------------------- office apps
def find_office():
    """(name, command list) of the spreadsheet app to use: WPS Office first, then Excel."""
    if IS_WIN:
        roots = [os.environ.get(v, "") for v in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)")]
        for root in filter(None, roots):
            for pattern in ("Kingsoft/WPS Office/*/office6/et.exe", "Kingsoft/WPS Office/ksolaunch.exe",
                            "WPS Office/*/office6/et.exe", "Kingsoft/WPS Office/*/office6/wps.exe"):
                hits = sorted(glob.glob(os.path.join(root, *pattern.split("/"))), reverse=True)
                if hits:
                    return "WPS Spreadsheets", [hits[0]]
        for root in filter(None, roots[1:]):
            for pattern in ("Microsoft Office/root/Office*/EXCEL.EXE", "Microsoft Office/Office*/EXCEL.EXE"):
                hits = sorted(glob.glob(os.path.join(root, *pattern.split("/"))), reverse=True)
                if hits:
                    return "Excel", [hits[0]]
        for root in filter(None, roots[1:]):
            for pattern in ("LibreOffice/program/scalc.exe",):
                hits = glob.glob(os.path.join(root, *pattern.split("/")))
                if hits:
                    return "LibreOffice Calc", [hits[0]]
        return "default spreadsheet app", None        # let Windows pick (os.startfile)
    if IS_MAC:
        for app, name in (("/Applications/wpsoffice.app", "WPS Office"), ("/Applications/Microsoft Excel.app", "Excel"),
                          ("/Applications/LibreOffice.app", "LibreOffice Calc")):
            if os.path.exists(app):
                return name, ["open", "-a", app]
        return "default spreadsheet app", ["open"]
    for exe, name in (("et", "WPS Spreadsheets"), ("wps", "WPS Office"), ("libreoffice", "LibreOffice Calc"),
                      ("localc", "LibreOffice Calc"), ("soffice", "LibreOffice Calc")):
        path = shutil.which(exe)
        if path:
            return name, [path] + (["--calc"] if exe in ("libreoffice", "soffice") else [])
    return "default spreadsheet app", ["xdg-open"]


class OfficeEditor:
    """Works in spreadsheets: one .xlsx per 'file', typed cell by cell."""
    kind = "office"
    verifies = False

    def __init__(self, workspace_dir, log=print):
        self.log = log
        self.ws = os.path.abspath(os.path.expanduser(workspace_dir))
        self.name, self.command = find_office()
        self.project_dir = None
        self.screen = None
        self.current = None
        self.open_current = False
        self.background_complete = False
        self.keep_project = False
        self.keep_finished = True
        self._last_focus = 0.0
        self._last_open_failed = 0.0

    def _title_match(self, title):
        if not self.current:
            return False
        stem = os.path.splitext(os.path.basename(self.current))[0]
        if not stem:
            return False
        caption = (title or "").casefold()
        wanted = stem.casefold()
        if wanted in caption:
            return True
        return len(wanted) > 24 and wanted[:24] in caption

    def open(self):
        os.makedirs(self.ws, exist_ok=True)
        self.log(f"Spreadsheets will open in {self.name}")
        return True

    def is_active(self):
        title = active_window_title()
        if title is None:
            return None
        return self._title_match(title)

    def handle_popup(self):
        """Cancel an owned modal dialog without sending keys to another app."""
        return _WindowsFocus.dismiss_owned_dialog(self._title_match)

    def focus(self, force=False):
        try:
            if IS_WIN:
                w = _WindowsFocus.find(self._title_match)
                return _WindowsFocus.activate(w) if w else False
            now = time.time()
            if not force and now - self._last_focus < 1.5:
                return "ok"
            self._last_focus = now
            stem = os.path.splitext(os.path.basename(self.current or ""))[0]
            if IS_MAC:
                subprocess.run(["osascript", "-e", f'tell application "System Events" to set frontmost of '
                                f'(first process whose name contains "{self.name.split()[0]}") to true'],
                               capture_output=True, timeout=3)
            elif shutil.which("xdotool") and stem:
                subprocess.run(["xdotool", "search", "--name", stem, "windowactivate"], capture_output=True, timeout=3)
            return "ok"
        except Exception:  # noqa: BLE001
            return False

    def region(self):
        if IS_WIN:
            w = _WindowsFocus.find(self._title_match)
            if w is not None and w.width > 200:
                return (w.left, w.top, w.width, w.height)
        if self.screen:
            return self.screen
        sw, sh = pyautogui.size()
        return (0, 0, sw, sh)

    def place(self, rect):
        stem = os.path.splitext(os.path.basename(self.current or ""))[0]
        if stem:
            place_window(rect, win_match=self._title_match, x_name=stem)

    def begin_project(self, name, interactive=True):
        self.keep_project = False
        dest = os.path.join(self.ws, name)
        n = 2
        while os.path.exists(dest):
            dest = os.path.join(self.ws, f"{name}-{n}")
            n += 1
        os.makedirs(dest, exist_ok=True)
        open(os.path.join(dest, MARKER), "w").close()
        self.project_dir = dest
        self.log(f"New spreadsheet project: {os.path.basename(dest)}")

    def begin_file(self, rel, show=True):
        path = os.path.join(self.project_dir, *rel.split("/"))
        title = os.path.splitext(os.path.basename(rel))[0].replace("-", " ").title()
        book = getattr(self, "next_book", None) or None
        blank_xlsx(path, sheet=title[:31], book=book, populate=not show)
        self.next_book = None
        self.current = path
        self.open_current = False
        self.background_complete = not show
        if show:
            if time.monotonic() - self._last_open_failed < 60 and self._last_open_failed:
                opened = False
            else:
                opened = self.open_file(path)
            self.open_current = opened
            if not opened and book:
                path = self.complete_in_background(path, book)
                self.background_complete = True
                self.log("The spreadsheet window was unavailable; saved the complete workbook on disk")
        return path

    def complete_in_background(self, path, book):
        """Write a complete workbook beside an open, partially typed workbook.

        Keeping the finished copy separate avoids racing Excel/WPS over a file that is
        currently open in the user's session.
        """
        stem, ext = os.path.splitext(path)
        target = stem + "-complete" + ext
        n = 2
        while os.path.exists(target):
            target = f"{stem}-complete-{n}{ext}"
            n += 1
        title = os.path.basename(stem).replace("-", " ").title()
        blank_xlsx(target, sheet=title[:31], book=book, populate=True)
        self.background_complete = True
        self.keep_project = self.open_current
        self.log(f"Finished {os.path.basename(target)} in the background")
        return target

    def open_file(self, path):
        try:
            if self.command is None and IS_WIN:
                os.startfile(path)  # noqa: S606 - the user's own default app
            else:
                subprocess.Popen(self.command + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            self._last_open_failed = time.monotonic()
            self.log(f"Couldn't open {path} in {self.name}: {exc}")
            return False
        ready = False
        for _ in range(30):              # wait up to ~15 s for the window
            time.sleep(0.5)
            focused = self.focus(force=True)
            if focused and self.is_active() is not False:
                ready = True
                break
        if not ready:
            self._last_open_failed = time.monotonic()
            self.log(f"Couldn't focus {os.path.basename(path)} in {self.name}")
            return False
        time.sleep(2.0)
        if not self.focus(force=True) or self.is_active() is False:
            self._last_open_failed = time.monotonic()
            return False
        pyautogui.hotkey("ctrl", "home")  # start at A1
        self._last_open_failed = 0.0
        return True

    def end_file(self, path, expected):
        if self.background_complete:
            self.background_complete = False
            return None
        pyautogui.hotkey("command" if IS_MAC else "ctrl", "s")
        time.sleep(1.5)
        pyautogui.press("enter")          # "keep this format?" prompts: keep the default
        time.sleep(0.5)
        return None

    def close_file(self):
        """Close the finished workbook (it was saved) so its folder can be removed."""
        if self.is_active() is not False:
            pyautogui.hotkey("ctrl", "w")
            time.sleep(1.0)
            self.open_current = False

    def clear(self):
        pass
