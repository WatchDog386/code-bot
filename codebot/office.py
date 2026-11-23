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
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">{views}{cols}<sheetData/></worksheet>"""
_FREEZE = ('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" '
           'state="frozen"/><selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>')


def column_widths(rows):
    """A good width for every column, from what will be typed into it (formulas ~ 12)."""
    widths = []
    for row in rows:
        for c, cell in enumerate(row):
            text = str(cell)
            size = 12 if text.startswith("=") else len(text)
            while len(widths) <= c:
                widths.append(8)
            widths[c] = max(widths[c], min(45, size + 2))
    return widths
_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def blank_xlsx(path, sheet="Sheet1", rows=None):
    """Write an empty, valid .xlsx workbook (no extra libraries needed). With `rows`, the
    columns are already as wide as what will be typed, and the header row is frozen."""
    cols = ""
    if rows:
        cols = "<cols>" + "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>'
                                  for i, w in enumerate(column_widths(rows))) + "</cols>"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CT)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("xl/workbook.xml", _WB.format(name=sheet[:31].replace("&", "and")))
        z.writestr("xl/_rels/workbook.xml.rels", _WB_RELS)
        z.writestr("xl/worksheets/sheet1.xml", _SHEET.format(views=_FREEZE if rows else "", cols=cols))
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

    def begin_file(self, rel, show=True, rows=None):
        path = os.path.join(self.project_dir, *rel.split("/"))
        title = os.path.splitext(os.path.basename(rel))[0].replace("-", " ").title()
        blank_xlsx(path, sheet=title[:31], rows=rows)
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
        time.sleep(0.4)
        if self.is_active() is not False:
            pyautogui.hotkey("ctrl", "home")  # start at A1

    def end_file(self, path, expected):
        self.focus(force=True)
        time.sleep(0.3)
        if self.is_active() is False:
            return None                   # not in front: never press keys elsewhere
        pyautogui.hotkey("command" if IS_MAC else "ctrl", "s")
        time.sleep(1.5)
        if self.is_active() is not False:
            pyautogui.press("enter")      # a "keep this format?" prompt: Enter keeps xlsx
        time.sleep(0.5)
        return None

    def close_file(self):
        """Close the finished workbook (it was saved) so its folder can be removed."""
        if self.is_active() is not False:
            pyautogui.hotkey("ctrl", "w")
            time.sleep(1.0)

    def clear(self):
        pass
