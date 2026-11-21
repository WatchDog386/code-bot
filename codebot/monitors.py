"""List the physical monitors as rectangles in the same coordinates pyautogui uses."""

import re
import subprocess
import sys
from dataclasses import asdict, dataclass

import pyautogui  # imported first: on Windows it makes the process DPI-aware


@dataclass
class Monitor:
    index: int
    x: int
    y: int
    width: int
    height: int
    primary: bool = False
    # work area = monitor minus the taskbar / dock / menu bar
    wx: int = 0
    wy: int = 0
    wwidth: int = 0
    wheight: int = 0

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)

    @property
    def work(self):
        if self.wwidth and self.wheight:
            return (self.wx, self.wy, self.wwidth, self.wheight)
        return self.rect

    def label(self):
        pos = "left" if self.x < 0 else ("right" if self.x > 0 else "")
        return (f"Screen {self.index + 1}: {self.width}x{self.height}"
                + (" (main)" if self.primary else "") + (f" - {pos}" if pos and not self.primary else ""))

    def to_dict(self):
        d = asdict(self)
        d["label"] = self.label()
        return d


def _windows():
    import ctypes
    from ctypes import wintypes

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

    out = []
    proc = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HMONITOR, wintypes.HDC,
                              ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)

    def cb(hmon, hdc, rect, data):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))
        m, w = info.rcMonitor, info.rcWork
        out.append(Monitor(0, m.left, m.top, m.right - m.left, m.bottom - m.top,
                           bool(info.dwFlags & 1), w.left, w.top, w.right - w.left, w.bottom - w.top))
        return 1

    ctypes.windll.user32.EnumDisplayMonitors(None, None, proc(cb), 0)
    return out


def _mac():
    import Quartz  # ships with pyautogui on macOS (pyobjc-framework-Quartz)
    err, ids, count = Quartz.CGGetActiveDisplayList(16, None, None)
    main = Quartz.CGMainDisplayID()
    out = []
    for did in ids[:count]:
        b = Quartz.CGDisplayBounds(did)
        x, y, w, h = int(b.origin.x), int(b.origin.y), int(b.size.width), int(b.size.height)
        # leave room for the menu bar (main screen) / dock
        out.append(Monitor(0, x, y, w, h, did == main, x, y + 25, w, h - 25 - (70 if did == main else 0)))
    return out


def _linux():
    out = []
    try:
        txt = subprocess.run(["xrandr", "--query"], capture_output=True, text=True, timeout=3).stdout
        for line in txt.splitlines():
            m = re.search(r" connected( primary)? (\d+)x(\d+)\+(-?\d+)\+(-?\d+)", line)
            if m:
                w, h, x, y = map(int, m.group(2, 3, 4, 5))
                out.append(Monitor(0, x, y, w, h, bool(m.group(1))))
    except (OSError, subprocess.SubprocessError):
        pass
    return out


def get_monitors():
    try:
        if sys.platform.startswith("win"):
            mons = _windows()
        elif sys.platform == "darwin":
            mons = _mac()
        else:
            mons = _linux()
    except Exception:  # noqa: BLE001
        mons = []
    if not mons:
        w, h = pyautogui.size()
        mons = [Monitor(0, 0, 0, w, h, True)]
    if not any(m.primary for m in mons):
        for m in mons:
            m.primary = (m.x, m.y) == (0, 0)
    # number them left-to-right, like Windows display settings usually do
    mons.sort(key=lambda m: (m.x, m.y))
    for i, m in enumerate(mons):
        m.index = i
    return mons


def pick_monitor(index):
    """index -1 = auto: the right-most screen that isn't the main one (or the main one)."""
    mons = get_monitors()
    if 0 <= index < len(mons):
        return mons[index]
    others = [m for m in mons if not m.primary]
    return others[-1] if others else mons[0]
