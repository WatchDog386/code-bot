"""Open a dedicated scratch file in Notepad (or the OS equivalent) and keep it focused.

The bot only ever types into its own scratch file, so it never touches your real notes.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time

SCRATCH_NAME = "scratch_main.py"


def scratch_path():
    d = os.path.join(tempfile.gettempdir(), "code-bot")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, SCRATCH_NAME)
    if not os.path.exists(p):
        open(p, "w").close()  # Notepad asks "create new file?" if it doesn't exist
    return p


class Editor:
    def __init__(self, log=print):
        self.log = log
        self.path = scratch_path()
        self.proc = None
        self.name = None
        self._last_focus = 0.0

    # ------------------------------------------------------------------ open
    def open(self):
        if self.is_open():
            self.focus(force=True)
            return True
        try:
            if sys.platform.startswith("win"):
                self.name = "Notepad"
                self.proc = subprocess.Popen(["notepad.exe", self.path])
            elif sys.platform == "darwin":
                self.name = "TextEdit"
                subprocess.Popen(["open", "-a", "TextEdit", self.path])
            else:
                for ed in ("gedit", "gnome-text-editor", "mousepad", "xed",
                           "pluma", "kate", "leafpad", "featherpad"):
                    if shutil.which(ed):
                        self.name = ed
                        self.proc = subprocess.Popen([ed, self.path],
                                                     stdout=subprocess.DEVNULL,
                                                     stderr=subprocess.DEVNULL)
                        break
                else:
                    self.log("No text editor found (install gedit or mousepad).")
                    return False
        except Exception as exc:  # noqa: BLE001
            self.log(f"Could not open editor: {exc}")
            return False
        self.log(f"Opened {self.name} with {self.path}")
        # wait for the window to appear
        for _ in range(20):
            time.sleep(0.25)
            if self._find_window_windows() or not sys.platform.startswith("win"):
                break
        time.sleep(0.8)
        self.focus(force=True)
        return True

    def is_open(self):
        if sys.platform.startswith("win"):
            return self._find_window_windows() is not None
        if self.proc is not None:
            return self.proc.poll() is None
        if sys.platform == "darwin" and self.name:
            r = subprocess.run(["pgrep", "-x", "TextEdit"], capture_output=True)
            return r.returncode == 0
        return False

    # ----------------------------------------------------------------- focus
    def focus(self, force=False):
        """Bring the scratch window to the front. Cheap to call often."""
        now = time.time()
        try:
            if sys.platform.startswith("win"):
                return self._focus_windows()
            # osascript / xdotool are slow -> throttle to once a second
            if not force and now - self._last_focus < 1.0:
                return True
            self._last_focus = now
            if sys.platform == "darwin":
                script = (
                    'tell application "TextEdit"\n'
                    '  activate\n'
                    f'  try\n    set index of (first window whose name contains "{SCRATCH_NAME}") to 1\n  end try\n'
                    'end tell'
                )
                subprocess.run(["osascript", "-e", script], capture_output=True, timeout=3)
            elif shutil.which("xdotool"):
                subprocess.run(["xdotool", "search", "--name", SCRATCH_NAME,
                                "windowactivate"], capture_output=True, timeout=3)
            elif shutil.which("wmctrl"):
                subprocess.run(["wmctrl", "-a", SCRATCH_NAME], capture_output=True, timeout=3)
            return True
        except Exception:  # noqa: BLE001
            return False

    # ------------------------------------------------------ windows helpers
    def _find_window_windows(self):
        if not sys.platform.startswith("win"):
            return None
        try:
            import pygetwindow as gw
            stem = os.path.splitext(SCRATCH_NAME)[0]
            for w in gw.getAllWindows():
                if stem in w.title and "Notepad" in w.title:
                    return w
        except Exception:  # noqa: BLE001
            pass
        return None

    def _focus_windows(self):
        import pygetwindow as gw
        w = self._find_window_windows()
        if w is None:
            return False
        active = gw.getActiveWindow()
        if active is not None and active.title == w.title:
            return True
        try:
            if w.isMinimized:
                w.restore()
            import pyautogui
            pyautogui.press("alt")  # lets Windows allow SetForegroundWindow
            w.activate()
        except Exception:  # noqa: BLE001  (pygetwindow sometimes raises on success)
            pass
        return True
