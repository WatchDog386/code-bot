"""Where VS Code's parts are on screen, so the mouse can work with a purpose.

The menu bar (File Edit Selection View Go Run Terminal Help) is found by looking at a
screenshot of the title bar: the labels are the first eight runs of text after the logo.
Nothing is clicked unless the labels look right (8 of them, "Selection" and "Terminal"
wider than "Go") and a dropdown really opened - otherwise the caller falls back to the
command palette, so a missed click never does anything unexpected.

Everything else (editor text, explorer, terminal panel, a browser opened beside the code)
is worked out from the window rectangle and the screen scaling.
"""

import random
import sys
import time

import pyautogui

from . import human

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
MENUS = ["File", "Edit", "Selection", "View", "Go", "Run", "Terminal", "Help"]


def grab(box):
    """Screenshot of (x, y, w, h) as a PIL image, or None."""
    x, y, w, h = (int(v) for v in box)
    if w <= 0 or h <= 0:
        return None
    try:
        from PIL import ImageGrab
        kw = {"all_screens": True} if IS_WIN else {}
        return ImageGrab.grab(bbox=(x, y, x + w, y + h), **kw)
    except Exception:  # noqa: BLE001
        try:
            return pyautogui.screenshot(region=(x, y, w, h))
        except Exception:  # noqa: BLE001
            return None


def screen_scale():
    """Windows display scaling (1.0 = 100 %). Other systems report logical points."""
    if IS_WIN:
        try:
            import ctypes
            return max(1.0, ctypes.windll.user32.GetDpiForSystem() / 96.0)
        except Exception:  # noqa: BLE001
            return 1.0
    return 1.0


def _runs(flags, min_gap):
    """[(start, end)] of consecutive True values, merging gaps shorter than min_gap."""
    runs, start, last = [], None, None
    for i, on in enumerate(flags):
        if on:
            if start is None:
                start = i
            elif i - last > min_gap:
                runs.append((start, last + 1))
                start = i
            last = i
    if start is not None:
        runs.append((start, last + 1))
    return runs


def find_menu_labels(img, scale=1.0):
    """{label: (x, y)} centres of the menu labels inside a title-bar screenshot, or {}."""
    if img is None:
        return {}
    g = img.convert("L")
    w, h = g.size
    px = g.load()
    hist = g.histogram()
    bg = max(range(256), key=lambda v: hist[v])          # title bar colour
    limit = min(w, int(w * 0.5))

    def ink(i, j):
        return abs(px[i, j] - bg) > 55

    # the text row: rows with ink where File..Terminal are (left of the back/forward arrows
    # and the search box that newer VS Code puts in the title bar)
    probe = range(int(40 * scale), min(limit, int(300 * scale)), 2)
    rows = [sum(1 for i in probe if ink(i, j)) > 2 for j in range(h)]
    bands = [b for b in _runs(rows, 1) if 6 * scale <= b[1] - b[0] <= 22 * scale]
    if not bands:
        return {}
    top, bottom = bands[0]
    cols = [any(ink(i, j) for j in range(top, bottom)) for i in range(limit)]
    words = [r for r in _runs(cols, max(3, int(5 * scale))) if r[1] - r[0] >= 3 and r[0] > 30 * scale]
    # the menu ends at the first wide gap (then come the arrows / search box / title)
    first = []
    for a, b in words:
        if first and a - first[-1][1] > 40 * scale:
            break
        first.append((a, b))
    if len(first) < 8:
        return {}
    first = first[:8]
    widths = [b - a for a, b in first]
    if not (widths[2] > widths[4] and widths[6] > widths[4] and widths[2] > widths[0]):
        return {}                                        # doesn't look like VS Code's menu
    yc = (top + bottom) // 2
    return {name: ((a + b) // 2, yc) for name, (a, b) in zip(MENUS, first)}


class Layout:
    """VS Code's regions inside the window rectangle (x, y, w, h)."""

    def __init__(self, rect, scale=None):
        self.rect = tuple(int(v) for v in rect)
        self.s = scale or screen_scale()
        self._menu = None
        self._menu_rect = None

    def _px(self, v):
        return int(round(v * self.s))

    @property
    def title(self):
        x, y, w, _ = self.rect
        return (x, y, w, self._px(38))

    def editor_text(self):
        """The code itself: right of the line numbers, left of the minimap. Works whether the
        activity bar is on the left or on top of the side bar, and for side bars 160-350 px."""
        x, y, w, h = self.rect
        left = x + max(int(w * 0.24), self._px(420))
        top = y + self._px(35 + 35 + 22 + 20)
        right = x + w - self._px(130)
        bottom = y + h - self._px(24 + 40)
        return (left, top, max(50, right - left), max(50, bottom - top))

    def explorer(self):
        """The file tree (kept inside the narrowest side bar)."""
        x, y, w, h = self.rect
        return (x + self._px(60), y + self._px(35 + 70), self._px(90), max(50, int(h * 0.3)))

    def panel(self):
        """The terminal panel (bottom part of the editor column once a terminal is open)."""
        ex, ey, ew, eh = self.editor_text()
        x, y, w, h = self.rect
        top = y + int(h * 0.68)
        return (ex - self._px(40), top, ew, max(40, y + h - self._px(30) - top))

    def side(self):
        """The right-hand editor group (where the app's page is shown)."""
        ex, ey, ew, eh = self.editor_text()
        return (ex + ew // 2 + self._px(20), ey, ew // 2 - self._px(20), int(eh * 0.6))

    # ---------------------------------------------------------------- menus
    def menu_labels(self):
        if IS_MAC:
            return {}                                    # macOS: menus live in the system bar
        if self._menu is None or self._menu_rect != self.rect:
            img = grab(self.title)
            found = find_menu_labels(img, self.s)
            self._menu = {k: (self.title[0] + x, self.title[1] + y) for k, (x, y) in found.items()}
            self._menu_rect = self.rect
        return self._menu


def point_in(box, fx=None, fy=None):
    x, y, w, h = box
    fx = random.uniform(0.2, 0.8) if fx is None else fx
    fy = random.uniform(0.2, 0.8) if fy is None else fy
    return x + w * fx, y + h * fy


def changed(before, after, threshold=6.0):
    """Did the picture change (e.g. a dropdown appeared)?"""
    if before is None or after is None:
        return False
    try:
        from PIL import ImageChops, ImageStat
        diff = ImageChops.difference(before.convert("L"), after.convert("L"))
        return ImageStat.Stat(diff).mean[0] > threshold
    except Exception:  # noqa: BLE001
        return False


def dropdown_top(before, after, threshold=40):
    """First row (in the region) where the picture changed a lot, or None."""
    try:
        from PIL import ImageChops
        diff = ImageChops.difference(before.convert("L"), after.convert("L"))
        w, h = diff.size
        px = diff.load()
        for j in range(h):
            if sum(1 for i in range(0, w, 3) if px[i, j] > threshold) > w // 12:
                return j
    except Exception:  # noqa: BLE001
        pass
    return None


def click_menu(layout, menu, item=0, stop=None):
    """Click a menu in VS Code's menu bar, then its `item`-th entry (0 = first).
    Returns True if it clearly worked; False = nothing (harmful) happened, use the palette."""
    labels = layout.menu_labels()
    if menu not in labels:
        return False
    mx, my = labels[menu]
    s = layout.s
    below = (mx - int(30 * s), my + int(12 * s), int(300 * s), int(260 * s))
    before = grab(below)
    human.move_to(mx + random.randint(-3, 3), my + random.randint(-2, 2), stop=stop)
    if stop is not None and stop():
        return False
    time.sleep(random.uniform(0.15, 0.4))
    pyautogui.click()
    time.sleep(random.uniform(0.5, 0.8))
    after = grab(below)
    if not changed(before, after):
        pyautogui.press("escape")                         # nothing opened (or not sure): back out
        return False
    top = dropdown_top(before, after)
    if top is None:
        pyautogui.press("escape")
        return False
    item_y = below[1] + top + int((6 + 13 + 26 * item) * s)
    item_x = mx - int(10 * s) + int(random.uniform(40, 90) * s)
    human.move_to(item_x, item_y, speed=0.8, stop=stop)
    time.sleep(random.uniform(0.2, 0.45))
    pyautogui.click()
    time.sleep(0.6)
    return True
