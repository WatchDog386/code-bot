"""Editors the bot can type into.

VSCodeEditor  - opens a real workspace folder in its own VS Code window, creates each
                project file on disk, opens it as a tab and types it out. A workspace
                settings file turns off auto-closing brackets, auto-indent, IntelliSense,
                Copilot etc. so the typed code comes out exactly like the source.
NotepadEditor - types into a dedicated scratch file in Notepad / TextEdit / gedit.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import pyautogui

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
    "editor.quickSuggestions": {"other": "off", "comments": "off", "strings": "off"},
    "editor.suggestOnTriggerCharacters": False,
    "editor.acceptSuggestionOnEnter": "off",
    "editor.acceptSuggestionOnCommitCharacter": False,
    "editor.wordBasedSuggestions": "off",
    "editor.snippetSuggestions": "none",
    "editor.tabCompletion": "off",
    "editor.parameterHints.enabled": False,
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
    "github.copilot.enable": {"*": False},
    "github.copilot.editor.enableAutoCompletions": False,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1500,
    "workbench.editor.enablePreview": False,
    "workbench.startupEditor": "none",
    "explorer.autoReveal": True,
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


def place_window(rect, win_match=None, x_name=None, mac_process=None, mac_contains=None):
    """Move a window onto the monitor `rect` (x, y, w, h) and maximize it there."""
    x, y, w, h = rect
    try:
        if IS_WIN and win_match:
            win = _WindowsFocus.find(win_match)
            if win is None:
                return False
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

    def begin_project(self, name, interactive=True):
        if interactive:
            self.focus(force=True)
            mod = "command" if IS_MAC else "ctrl"
            pyautogui.hotkey(mod, "k")         # Close all editors (Ctrl+K Ctrl+W)
            pyautogui.hotkey(mod, "w")
            time.sleep(0.5)
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
        self._run_cli(path)
        time.sleep(1.6)
        self.focus(force=True)
        time.sleep(0.3)

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

    def open_terminal(self):
        """Focus VS Code's integrated terminal (creates one if needed)."""
        self.focus(force=True)
        mod = "command" if IS_MAC else "ctrl"
        pyautogui.hotkey(mod, "shift", "p")
        time.sleep(0.7)
        pyautogui.write("Terminal: Focus Terminal", interval=0.03)
        time.sleep(0.6)
        pyautogui.press("enter")
        time.sleep(2.0)

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

    def focus(self, force=False):
        return "ok"

    def clear(self):
        pass
