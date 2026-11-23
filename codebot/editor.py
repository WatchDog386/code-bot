"""Editors the bot can type into.

VSCodeEditor  - opens a real workspace folder in its own VS Code window, creates each
                project file on disk, opens it as a tab and types it out. A workspace
                settings file turns off auto-closing brackets, auto-indent, IntelliSense,
                Copilot etc. so the typed code comes out exactly like the source.
NotepadEditor - types into a dedicated scratch file in Notepad / TextEdit / gedit.
"""

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time

import pyautogui

from . import human

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
MARKER = ".codebot"

# Everything that would make VS Code insert or change text while we type.
_EDITOR_CLEAN = {
    "editor.autoClosingBrackets": "never",
    "editor.autoClosingQuotes": "never",
    "editor.autoClosingComments": "never",
    "editor.autoClosingOvertype": "never",
    "editor.autoClosingDelete": "never",
    "editor.autoSurround": "never",
    "editor.autoIndent": "none",
    "editor.formatOnType": False,
    "editor.formatOnSave": False,
    "editor.formatOnPaste": False,
    "editor.codeActionsOnSave": {},
    # autocomplete pops up while typing (looks real) but can never be accepted:
    # Enter, Tab and commit characters like ( . ; don't accept a suggestion
    "editor.quickSuggestions": {"other": "on", "comments": "off", "strings": "off"},
    "editor.quickSuggestionsDelay": 10,
    "editor.suggestOnTriggerCharacters": True,
    "editor.wordBasedSuggestions": "matchingDocuments",
    "editor.parameterHints.enabled": True,
    "editor.acceptSuggestionOnEnter": "off",
    "editor.acceptSuggestionOnCommitCharacter": False,
    "editor.tabCompletion": "off",
    "editor.snippetSuggestions": "none",
    "editor.suggest.preview": False,
    "editor.inlineSuggest.enabled": False,
    "editor.linkedEditing": False,
    "editor.detectIndentation": False,
    "editor.insertSpaces": True,
    "editor.tabSize": 4,
    "files.insertFinalNewline": False,
    "files.trimTrailingWhitespace": False,
    "files.trimFinalNewlines": False,
}

WORKSPACE_SETTINGS = {
    **_EDITOR_CLEAN,
    # language extensions ship their own per-language defaults, which beat plain
    # settings, so repeat everything for each language
    "[python][go][javascript][javascriptreact][typescript][typescriptreact][json][jsonc]"
    "[markdown][html][css][scss][yaml][sql][java][rust][plaintext][go.mod]": dict(_EDITOR_CLEAN),
    "html.autoClosingTags": False,
    "javascript.autoClosingTags": False,
    "typescript.autoClosingTags": False,
    "emmet.showExpandedAbbreviation": "never",
    "emmet.triggerExpansionOnTab": False,
    "python.analysis.autoIndent": False,
    "python.analysis.autoFormatStrings": False,
    "github.copilot.enable": {"*": False},
    "github.copilot.editor.enableAutoCompletions": False,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1500,
    "workbench.editor.enablePreview": False,
    "workbench.startupEditor": "none",
    "explorer.autoReveal": True,            # each new file shows up highlighted in the explorer
    "workbench.sideBar.location": "left",
    "chat.disableAIFeatures": True,         # no Copilot chat panel popping open
    "python.terminal.activateEnvironment": False,   # extensions must not open terminals
    "python.createEnvironment.trigger": "off",
    "task.allowAutomaticTasks": "off",
    "npm.autoDetect": "off",
    "terminal.integrated.enablePersistentSessions": False,   # no old terminals / "History restored"
    "terminal.integrated.persistentSessionReviveProcess": "never",
    "terminal.integrated.hideOnStartup": "always",
    "editor.stickyScroll.enabled": False,   # no lines pinned at the top of the editor
    "editor.mouseWheelZoom": False,         # Ctrl + mouse wheel never changes the font size
    "workbench.tips.enabled": False,
    "workbench.secondarySideBar.defaultVisibility": "hidden",
    "chat.commandCenter.enabled": False,
    "workbench.editor.restoreViewState": True,
    "explorer.confirmDelete": False,
    "git.openRepositoryInParentFolders": "never",
    "extensions.ignoreRecommendations": True,
    "files.exclude": {"**/.codebot": True, ".vscode": True},
    "codebot.managed": True,
}


def doc_end_keys():
    return ("command", "down") if IS_MAC else ("ctrl", "end")


def _norm(text):
    return "\n".join(l.expandtabs(4).rstrip() for l in text.replace("\r\n", "\n").split("\n")).strip("\n")


def find_code_cli():
    found = shutil.which("code")
    if found:
        return found
    candidates = []
    if IS_WIN:
        for base in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles", ""),
                     os.environ.get("ProgramFiles(x86)", "")):
            candidates.append(os.path.join(base, "Programs", "Microsoft VS Code", "bin", "code.cmd"))
            candidates.append(os.path.join(base, "Microsoft VS Code", "bin", "code.cmd"))
    elif IS_MAC:
        candidates.append("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code")
        candidates.append(os.path.expanduser(
            "~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"))
    else:
        candidates += ["/usr/bin/code", "/snap/bin/code", "/usr/share/code/bin/code"]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


class _WindowsFocus:
    """Find + activate a window by title on Windows (pygetwindow ships with pyautogui)."""

    @staticmethod
    def find(match):
        try:
            import pygetwindow as gw
            for w in gw.getAllWindows():
                if match(w.title):
                    return w
        except Exception:  # noqa: BLE001
            pass
        return None

    @staticmethod
    def activate(w):
        import pygetwindow as gw
        active = gw.getActiveWindow()
        if active is not None and active.title == w.title:
            return "ok"
        try:
            if w.isMinimized:
                w.restore()
            pyautogui.press("alt")  # lets Windows allow SetForegroundWindow
            w.activate()
        except Exception:  # noqa: BLE001  (pygetwindow sometimes raises on success)
            pass
        return "refocused"


def active_window_title():
    """Title of the window that has keyboard focus, or None if we can't tell."""
    try:
        if IS_WIN:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value or None          # no title: can't tell, don't block typing
        if IS_MAC:
            script = ('tell application "System Events" to set p to first application process whose frontmost is true\n'
                      'tell application "System Events" to tell p\n'
                      '  set t to name of p\n'
                      '  try\n    set t to t & " | " & (name of front window)\n  end try\n'
                      'end tell\nreturn t')
            out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            return out.stdout.strip() if out.returncode == 0 else None
        if shutil.which("xdotool"):
            out = subprocess.run(["xdotool", "getactivewindow", "getwindowname"],
                                 capture_output=True, text=True, timeout=2)
            return out.stdout.strip() if out.returncode == 0 else None
    except Exception:  # noqa: BLE001
        pass
    return None


def place_window(rect, win_match=None, x_name=None, mac_process=None, mac_contains=None):
    """Move a window onto the monitor `rect` (x, y, w, h) and maximize it there."""
    x, y, w, h = rect
    try:
        if IS_WIN and win_match:
            win = _WindowsFocus.find(win_match)
            if win is None:
                return False
            if win.isMaximized and x <= win.left + 20 < x + w and y <= win.top + 20 < y + h:
                return True                 # already maximized on the right screen: leave it alone
            if win.isMaximized or win.isMinimized:
                win.restore()
                time.sleep(0.3)
            win.moveTo(x + 40, y + 40)
            win.resizeTo(max(600, w - 80), max(400, h - 80))
            time.sleep(0.2)
            win.maximize()          # maximizes on the monitor the window is on
            return True
        if IS_MAC and mac_process:
            script = (f'tell application "System Events" to tell process "{mac_process}"\n'
                      f'  set win to (first window whose name contains "{mac_contains}")\n'
                      f'  set position of win to {{{x}, {y}}}\n'
                      f'  set size of win to {{{w}, {h}}}\n'
                      'end tell')
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
            return True
        if x_name and shutil.which("xdotool"):
            ids = subprocess.run(["xdotool", "search", "--name", x_name], capture_output=True,
                                 text=True, timeout=3).stdout.split()
            for wid in ids:
                if shutil.which("wmctrl"):
                    subprocess.run(["wmctrl", "-i", "-r", wid, "-b", "remove,maximized_vert,maximized_horz"],
                                   capture_output=True, timeout=3)
                subprocess.run(["xdotool", "windowmove", wid, str(x), str(y)], capture_output=True, timeout=3)
                subprocess.run(["xdotool", "windowsize", wid, str(w), str(h)], capture_output=True, timeout=3)
                if shutil.which("wmctrl"):
                    subprocess.run(["wmctrl", "-i", "-r", wid, "-b", "add,maximized_vert,maximized_horz"],
                                   capture_output=True, timeout=3)
            return bool(ids)
    except Exception:  # noqa: BLE001
        pass
    return False


# =============================================================================
class VSCodeEditor:
    kind = "vscode"
    verifies = True

    def __init__(self, workspace_dir, log=print):
        self.log = log
        self.ws = os.path.abspath(os.path.expanduser(workspace_dir))
        self.root_name = os.path.basename(self.ws.rstrip("\\/"))
        self.name = "VS Code"
        self.cli = find_code_cli()
        self.project_dir = None
        self.screen = None          # (x, y, w, h) of the monitor we live on
        self.keep_finished = False  # False = only the current project stays in the workspace
        self._launched = False
        self._last_focus = 0.0

    # ------------------------------------------------------------ helpers
    def _run_cli(self, *args):
        cmd = [self.cli, *args]
        kw = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if IS_WIN:
            cmd = ["cmd", "/c", *cmd]
            kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        subprocess.Popen(cmd, **kw)

    def _title_match(self, title):
        return "Visual Studio Code" in title and f"{self.root_name} - " in title + " - "

    def _write_settings(self):
        vs = os.path.join(self.ws, ".vscode")
        os.makedirs(vs, exist_ok=True)
        path = os.path.join(vs, "settings.json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    if '"codebot.managed"' not in fh.read():
                        self.log(f"WARNING: {path} isn't ours - leaving it alone. "
                                 "Pick an empty workspace folder for clean typing.")
                        return
            except OSError:
                return
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(WORKSPACE_SETTINGS, fh, indent=2)

    # --------------------------------------------------------------- open
    def is_open(self):
        if IS_WIN:
            return _WindowsFocus.find(self._title_match) is not None
        return self._launched

    def open(self):
        if not self.cli:
            self.log("VS Code command line not found. Install VS Code (and on macOS run "
                     "'Shell Command: Install code command in PATH'), or switch to Notepad.")
            return False
        os.makedirs(self.ws, exist_ok=True)
        self._write_settings()
        if self.is_open():
            self.focus(force=True)
            return True
        self.log(f"Opening VS Code workspace {self.ws}")
        self._run_cli("-n", self.ws)
        self._launched = True
        for _ in range(40):  # wait up to ~20s for the window
            time.sleep(0.5)
            if not IS_WIN or self.is_open():
                break
        time.sleep(4 if not IS_WIN else 2.5)
        self.focus(force=True)
        return True

    # -------------------------------------------------------------- focus
    def focus(self, force=False):
        try:
            if IS_WIN:
                w = _WindowsFocus.find(self._title_match)
                return _WindowsFocus.activate(w) if w else False
            now = time.time()
            if not force and now - self._last_focus < 1.5:
                return "ok"
            self._last_focus = now
            if IS_MAC:
                script = (
                    'tell application "Visual Studio Code" to activate\n'
                    'tell application "System Events" to tell process "Code"\n'
                    f'  try\n    perform action "AXRaise" of (first window whose name contains "{self.root_name}")\n  end try\n'
                    'end tell')
                subprocess.run(["osascript", "-e", script], capture_output=True, timeout=3)
            elif shutil.which("xdotool"):
                subprocess.run(["xdotool", "search", "--name", f"{self.root_name} - Visual Studio Code",
                                "windowactivate"], capture_output=True, timeout=3)
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
        if place_window(rect, win_match=self._title_match,
                        x_name=f"{self.root_name} - Visual Studio Code",
                        mac_process="Code", mac_contains=self.root_name):
            time.sleep(0.4)

    # ------------------------------------------------------------ project
    def _manifest_path(self):
        return os.path.join(self.ws, ".vscode", "codebot-projects.json")

    def _manifest(self):
        try:
            with open(self._manifest_path(), encoding="utf-8") as fh:
                return [n for n in json.load(fh) if isinstance(n, str)]
        except (OSError, ValueError):
            return []

    def _save_manifest(self, names):
        os.makedirs(os.path.dirname(self._manifest_path()), exist_ok=True)
        with open(self._manifest_path(), "w", encoding="utf-8") as fh:
            json.dump(sorted(set(names)), fh, indent=2)

    def _ours(self):
        """Folders in the workspace that the bot created (manifest + old-style markers)."""
        names = set(self._manifest())
        try:
            for d in os.listdir(self.ws):
                if os.path.exists(os.path.join(self.ws, d, MARKER)):
                    names.add(d)
        except OSError:
            pass
        return {n for n in names if "/" not in n and "\\" not in n and n not in ("", ".", "..", ".vscode")}

    def cleanup(self, keep=()):
        """Delete bot-created project folders (never anything else)."""
        ours = self._ours()
        for name in ours - set(keep):
            path = os.path.join(self.ws, name)
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
        self._save_manifest([n for n in ours if n in keep and os.path.isdir(os.path.join(self.ws, n))])

    def tidy(self):
        """The code + the file explorer on the left, nothing else: normal zoom, no terminal
        panel, no chat/secondary side bar. Then the keyboard goes back into the code."""
        for command in ("View: Reset Zoom", "View: Hide Secondary Side Bar", "View: Hide Panel",
                        "View: Show Explorer"):
            self._palette(command, settle=0.5)
            human.press_esc()               # close the palette if that command doesn't exist
        self.focus_editor()

    def clean_start(self):
        """Right after VS Code opens: close the files and terminals it restored from last
        time, the side bars and the panel - only if VS Code is really in front."""
        self.focus(force=True)
        time.sleep(0.6)
        if self.is_active() is False:
            return
        mod = "command" if IS_MAC else "ctrl"
        pyautogui.hotkey(mod, "k")
        pyautogui.hotkey(mod, "w")              # close all editors
        time.sleep(0.4)
        self._palette("Terminal: Kill All Terminals", settle=0.5)
        human.press_esc()
        self.tidy()

    def begin_project(self, name, interactive=True):
        if interactive:
            self.focus(force=True)
            mod = "command" if IS_MAC else "ctrl"
            pyautogui.hotkey(mod, "k")         # Close all editors (Ctrl+K Ctrl+W)
            pyautogui.hotkey(mod, "w")
            time.sleep(0.5)
            self.tidy()
        ours = self._ours()
        keep = [n for n in ours if n != name] if self.keep_finished else []
        self.cleanup(keep=keep)            # workspace = just the project being written
        dest = os.path.join(self.ws, name)
        if os.path.exists(dest):            # a folder we didn't create: never touch it
            n = 2
            while os.path.exists(f"{dest}-{n}"):
                n += 1
            dest = f"{dest}-{n}"
        os.makedirs(dest, exist_ok=True)
        self._save_manifest(keep + [os.path.basename(dest)])
        self.project_dir = dest
        self.log(f"New project: {os.path.basename(dest)}")
        time.sleep(1.0)

    def begin_file(self, rel, show=True):
        path = os.path.join(self.project_dir, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").close()
        if show:
            self.show_file(path)
        return path

    def show_file(self, path):
        """Open (or switch to) the file's tab. VS Code shows what's on disk."""
        self.current_file = path
        self._run_cli(path)
        time.sleep(1.6)
        self.focus(force=True)
        time.sleep(0.3)
        if self.is_active() is not False:
            self.focus_editor()

    def end_file(self, path, expected):
        pyautogui.hotkey("command" if IS_MAC else "ctrl", "s")
        time.sleep(1.0)
        return self.verify(path, expected)

    def verify(self, path, expected):
        try:
            with open(path, encoding="utf-8") as fh:
                typed = fh.read()
        except OSError:
            return None
        return _norm(typed) == _norm(expected)

    def is_active(self):
        """Is the bot's VS Code window the one getting keystrokes? None = can't tell
        (then typing carries on). Only a clearly different window counts as False."""
        title = active_window_title()
        if not title:
            return None
        if self.root_name in title:
            return True
        current = os.path.basename(getattr(self, "current_file", "") or "")
        if current and current in title and ("Visual Studio Code" in title or IS_MAC):
            return True
        return False

    def _palette(self, command, settle=1.0):
        """Run a VS Code command through the command palette, typed like a person."""
        mod = "command" if IS_MAC else "ctrl"
        pyautogui.hotkey(mod, "shift", "p")
        time.sleep(random.uniform(0.5, 0.9))
        for ch in command:
            pyautogui.write(ch)
            time.sleep(random.uniform(0.03, 0.09))
        time.sleep(random.uniform(0.4, 0.8))
        pyautogui.press("enter")
        time.sleep(settle)

    def new_terminal(self):
        """Open a fresh integrated terminal (Ctrl+Shift+`) - starts in the workspace folder."""
        self.focus(force=True)
        self._palette("Terminal: Create New Terminal", settle=2.5)

    def open_terminal(self):
        """Focus VS Code's integrated terminal (creates one if needed)."""
        self.focus(force=True)
        self._palette("Terminal: Focus Terminal", settle=1.2)

    def layout(self):
        """Where the editor, explorer, terminal panel... are on screen right now."""
        from .vscode_ui import Layout
        rect = self.region()
        if getattr(self, "_layout", None) is None or self._layout.rect != tuple(int(v) for v in rect):
            self._layout = Layout(rect)
        return self._layout

    def open_terminal_ui(self, use_mouse=True, stop=None):
        """Terminal > New Terminal with the mouse (menu bar), like a person would. Falls back
        to the command palette if the menu can't be found or didn't open. Returns how."""
        from .vscode_ui import click_menu
        self.focus(force=True)
        how = "palette"
        if use_mouse and click_menu(self.layout(), "Terminal", 0, stop=stop):
            how = "menu"
            time.sleep(2.0)
        else:
            self._palette("Terminal: Create New Terminal", settle=2.5)
        self.click_terminal(use_mouse, stop)
        return how

    def click_terminal(self, use_mouse=True, stop=None):
        """Click into the terminal panel, then make sure the terminal really has the focus
        (so a command can never end up typed into the code)."""
        from . import human
        from .vscode_ui import point_in
        if use_mouse:
            x, y = point_in(self.layout().panel(), fx=random.uniform(0.15, 0.5), fy=random.uniform(0.45, 0.8))
            human.move_to(x, y, stop=stop)
            if not (stop and stop()):
                time.sleep(random.uniform(0.15, 0.35))
                pyautogui.click()
                time.sleep(0.3)
        self._palette("Terminal: Focus Terminal", settle=0.8)

    def open_browser(self, url, beside=True):
        """Show the running app inside VS Code (Simple Browser), next to the code."""
        self.focus(force=True)
        self._palette("Simple Browser: Show", settle=1.0)
        for ch in url:
            pyautogui.write(ch)
            time.sleep(random.uniform(0.03, 0.08))
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(2.0)
        if beside:   # into a group of its own on the right: code left, app right
            self._palette("View: Move Editor into Next Group", settle=1.5)

    def focus_editor(self):
        """Keyboard into the code editor (never the explorer or a terminal)."""
        pyautogui.hotkey("command" if IS_MAC else "ctrl", "1")
        time.sleep(0.3)

    def clear(self):
        pass


# =============================================================================
SCRATCH_NAME = "scratch_main.py"


def scratch_path():
    d = os.path.join(tempfile.gettempdir(), "code-bot")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, SCRATCH_NAME)
    if not os.path.exists(p):
        open(p, "w").close()  # Notepad asks "create new file?" if it doesn't exist
    return p


class NotepadEditor:
    kind = "notepad"
    verifies = False

    def __init__(self, log=print):
        self.log = log
        self.path = scratch_path()
        self.proc = None
        self.name = None
        self.screen = None
        self._last_focus = 0.0

    def _title_match(self, title):
        return os.path.splitext(SCRATCH_NAME)[0] in title and "Notepad" in title

    def is_open(self):
        if IS_WIN:
            return _WindowsFocus.find(self._title_match) is not None
        if self.proc is not None:
            return self.proc.poll() is None
        return False

    def open(self):
        if self.is_open():
            self.focus(force=True)
            return True
        try:
            if IS_WIN:
                self.name = "Notepad"
                self.proc = subprocess.Popen(["notepad.exe", self.path])
            elif IS_MAC:
                self.name = "TextEdit"
                subprocess.Popen(["open", "-a", "TextEdit", self.path])
            else:
                for ed in ("gedit", "gnome-text-editor", "mousepad", "xed", "pluma", "kate",
                           "leafpad", "featherpad"):
                    if shutil.which(ed):
                        self.name = ed
                        self.proc = subprocess.Popen([ed, self.path], stdout=subprocess.DEVNULL,
                                                     stderr=subprocess.DEVNULL)
                        break
                else:
                    self.log("No text editor found (install gedit or mousepad).")
                    return False
        except Exception as exc:  # noqa: BLE001
            self.log(f"Could not open editor: {exc}")
            return False
        self.log(f"Opened {self.name} with {self.path}")
        for _ in range(20):
            time.sleep(0.25)
            if not IS_WIN or self.is_open():
                break
        time.sleep(0.8)
        self.focus(force=True)
        return True

    def focus(self, force=False):
        try:
            if IS_WIN:
                w = _WindowsFocus.find(self._title_match)
                return _WindowsFocus.activate(w) if w else False
            now = time.time()
            if not force and now - self._last_focus < 1.5:
                return "ok"
            self._last_focus = now
            if IS_MAC:
                script = ('tell application "TextEdit"\n  activate\n'
                          f'  try\n    set index of (first window whose name contains "{SCRATCH_NAME}") to 1\n  end try\n'
                          'end tell')
                subprocess.run(["osascript", "-e", script], capture_output=True, timeout=3)
            elif shutil.which("xdotool"):
                subprocess.run(["xdotool", "search", "--name", SCRATCH_NAME, "windowactivate"],
                               capture_output=True, timeout=3)
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
        place_window(rect, win_match=self._title_match, x_name=SCRATCH_NAME,
                     mac_process="TextEdit", mac_contains=SCRATCH_NAME)

    def is_active(self):
        title = active_window_title()
        if title is None:
            return None
        return os.path.splitext(SCRATCH_NAME)[0] in title

    def begin_project(self, name, interactive=True):
        self.log(f"New project: {name}")

    def begin_file(self, rel, show=True):
        if show:
            self.clear()
        return None

    def end_file(self, path, expected):
        pyautogui.hotkey("command" if IS_MAC else "ctrl", "s")
        return None

    def clear(self):
        self.focus(force=True)
        pyautogui.hotkey("command" if IS_MAC else "ctrl", "a")
        pyautogui.press("backspace")


class FocusedWindowEditor(NotepadEditor):
    """Types into whatever window has focus (no auto-open)."""
    kind = "focused"

    def open(self):
        self.name = "focused window"
        return True

    def place(self, rect):
        pass

    def is_active(self):
        return None   # whatever window you choose is the target

    def focus(self, force=False):
        return "ok"

    def clear(self):
        pass
