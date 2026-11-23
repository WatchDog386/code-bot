"""Spreadsheets in WPS Office (or Excel / LibreOffice Calc): create a workbook, open it in
the office app, and let the bot type cells, formulas and formatting into it like a person.

OfficeEditor has the same shape as the other editors (open / focus / region / begin_project
/ begin_file / end_file), so the bot's loop drives it the same way it drives VS Code.
"""

import glob
import os
import shutil
import subprocess
import sys
import time
import zipfile

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
           '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
    return xml, index


def _sheet_xml(look, index):
    from .sheets import col
    if not look:
        return _SHEET
    cols = "".join(f'<col min="{c + 1}" max="{c + 1}" width="{w}" customWidth="1"/>'
                   for c, w in sorted(look["widths"].items()))
    by_row = {}
    for (r, c), key in look["cells"].items():
        by_row.setdefault(r, []).append((c, index[key]))
    rows = "".join(f'<row r="{r + 1}">' + "".join(f'<c r="{col(c)}{r + 1}" s="{s}"/>' for c, s in sorted(cells)) + "</row>"
                   for r, cells in sorted(by_row.items()))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="15"/>'
            + (f"<cols>{cols}</cols>" if cols else "") + f"<sheetData>{rows}</sheetData></worksheet>")


def blank_xlsx(path, sheet="Sheet1", sheets=None, book=None):
    """An empty .xlsx with one sheet per name in `sheets` (or just `sheet`). With `book` (the rows
    the bot will type) every sheet is laid out in advance: column widths, number formats
    (money, %, dates), a styled header row per table and bold total rows."""
    looks = {}
    if book:
        from .books import sheet_looks
        looks = sheet_looks(book, default=sheet)
        sheets = list(looks)
    names = [n.replace("&", "and")[:31] for n in (sheets or [sheet])]
    keys = sorted({k for lk in looks.values() for k in lk["cells"].values()})
    styles_xml, index = _styles(keys)
    ct = _CT.replace('<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>',
                     "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                             for i in range(1, len(names) + 1)))
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' +
          "".join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(names, 1)) +
          "</sheets></workbook>")
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
        for i, n in enumerate(names, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", _sheet_xml(looks.get(n), index))
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
        self.keep_finished = True
        self._last_focus = 0.0

    def _title_match(self, title):
        stem = os.path.splitext(os.path.basename(self.current or ""))[0]
        return bool(stem) and stem in title

    def open(self):
        os.makedirs(self.ws, exist_ok=True)
        self.log(f"Spreadsheets will open in {self.name}")
        return True

    def is_active(self):
        title = active_window_title()
        if title is None:
            return None
        return self._title_match(title)

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
        dest = os.path.join(self.ws, name)
        n = 2
        while os.path.exists(dest) and not os.path.exists(os.path.join(dest, MARKER)):
            dest = os.path.join(self.ws, f"{name}-{n}")
            n += 1
        os.makedirs(dest, exist_ok=True)
        open(os.path.join(dest, MARKER), "w").close()
        self.project_dir = dest
        self.log(f"New spreadsheet project: {os.path.basename(dest)}")

    def begin_file(self, rel, show=True):
        path = os.path.join(self.project_dir, *rel.split("/"))
        title = os.path.splitext(os.path.basename(rel))[0].replace("-", " ").title()
        blank_xlsx(path, sheet=title[:31], book=getattr(self, "next_book", None) or None)
        self.next_book = None
        self.current = path
        self.open_file(path)
        return path

    def open_file(self, path):
        try:
            if self.command is None and IS_WIN:
                os.startfile(path)  # noqa: S606 - the user's own default app
            else:
                subprocess.Popen(self.command + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as exc:
            self.log(f"Couldn't open {path} in {self.name}: {exc}")
            return
        for _ in range(30):              # wait up to ~15 s for the window
            time.sleep(0.5)
            if not IS_WIN or self.focus(force=True):
                break
        time.sleep(2.0)
        self.focus(force=True)
        pyautogui.hotkey("ctrl", "home")  # start at A1

    def end_file(self, path, expected):
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

    def clear(self):
        pass
