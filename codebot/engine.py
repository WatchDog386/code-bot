"""The bot: writes real projects file by file with human-like typing and mouse movement.

- Lives on one monitor (VS Code gets maximized there, the mouse never leaves it).
- Esc pressed twice quickly = kill switch. F9 = pause/resume.
- Notices when YOU use the mouse or keyboard, gets out of the way immediately and
  carries on after you've been idle for a while.
"""

import math
import os
import random
import shutil
import subprocess
import re
import sys
import threading
import time
from collections import deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field

import pyautogui

from . import human
from .editor import FocusedWindowEditor, NotepadEditor, VSCodeEditor, doc_end_keys
from .monitors import get_monitors, pick_monitor
from .gen import LANGUAGES as GEN_LANGUAGES, generated_cycle
from .projects import (explain_command, guess_wait, list_projects, localize_command, project_commands, project_cycle,
                       project_scaffold)
from .snippets import LANGUAGES, pick_pool

# No corner "fail-safe": you share the mouse, so your cursor resting in a screen corner must
# not end the run. The kill switch is Esc Esc (or Stop in the dashboard).
pyautogui.FAILSAFE = False
FailSafe = getattr(pyautogui, "FailSafeException", RuntimeError)
pyautogui.PAUSE = 0

NEIGHBORS = {
    "a": "qwsz", "b": "vghn", "c": "xdfv", "d": "serfcx", "e": "wsdr", "f": "drtgvc",
    "g": "ftyhbv", "h": "gyujnb", "i": "ujko", "j": "huikmn", "k": "jiolm", "l": "kop",
    "m": "njk", "n": "bhjm", "o": "iklp", "p": "ol", "q": "wa", "r": "edft", "s": "awedxz",
    "t": "rfgy", "u": "yhji", "v": "cfgb", "w": "qase", "x": "zsdc", "y": "tghu", "z": "asx",
}
SHIFTED = set('~!@#$%^&*()_+{}|:"<>?')
BLOCK_START = re.compile(
    r"^(def |class |func |function |export |public |private |protected |async |interface |"
    r"type |struct |impl |fn |@|const \w+ = \(|it\(|test\(|describe\()")
CONTROL = ("if ", "for ", "while ", "switch", "try", "return", "else", "elif ", "case ", "catch")
SNIPPET_EXT = {"python": "py", "javascript": "js", "typescript": "ts", "sql": "sql",
               "go": "go", "java": "java"}
DOUBLE_ESC_WINDOW = 0.6
IS_WIN = sys.platform.startswith("win")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")  # seconds between the two Esc presses


@dataclass
class Config:
    editor: str = "vscode"             # vscode | notepad | focused
    source: str = "projects"           # projects (the library) | spreadsheets (Excel) | mixed | generated | snippets | file
    gen_languages: list = field(default_factory=lambda: ["python", "go", "typescript"])
    projects: list = field(default_factory=list)   # empty = all
    workspace_dir: str = "~/dev-projects"
    keep_finished: bool = False        # False = workspace only ever holds the current project
    languages: list = field(default_factory=lambda: list(LANGUAGES))
    custom_file: str = ""
    monitor: int = -1                  # -1 = auto (a screen that isn't the main one)
    maximize: bool = True              # maximize the editor on that screen
    mode: str = "both"                 # both | mouse | type
    wpm: int = 34                      # raw typing speed (pauses come on top)
    think: float = 1.0                 # how long the "thinking" pauses are (0.5 - 3)
    typo_rate: float = 0.015
    mouse_min: float = 4.0
    mouse_max: float = 14.0
    scroll: bool = True
    review_moves: bool = True          # sometimes arrow up to "re-read" code, then back
    breaks: bool = False
    detect_user: bool = True           # step aside when you use the mouse/keyboard
    mouse_resume: float = 1.0          # take the mouse back this soon after you stop moving it
    background_typing: bool = True     # VS Code: if you take the keyboard, keep writing the file on disk
    terminal_after_project: bool = False   # off = only type the code in the editor (no terminal at all)
    serve_seconds: float = 45          # how long a started app is left running (and shown) before Ctrl+C
    terminal_timeout: float = 300      # seconds before a background command is stopped
    resume_after: float = 5.0          # keyboard: take it back after this many idle seconds (0 = never)
    clear_after_lines: int = 150       # Notepad only: wipe scratch every N lines
    auto_open_editor: bool = True
    keep_focus: bool = True
    minutes: float = 0
    schedule_enabled: bool = True      # start by itself every day at schedule_start
    schedule_start: str = "03:00"      # HH:MM, this computer's local time
    daily_hours: float = 10.0          # most hours it may run per day (0 = no limit)
    start_delay: float = 3.0

    @classmethod
    def from_dict(cls, d):
        base = asdict(cls())
        base.update({k: v for k, v in (d or {}).items() if k in base})
        c = cls(**base)
        c.wpm = max(5, min(200, int(c.wpm)))
        c.think = max(0.3, min(3.0, float(c.think)))
        c.mouse_min = max(0.5, float(c.mouse_min))
        c.mouse_max = max(c.mouse_min, float(c.mouse_max))
        c.typo_rate = max(0.0, min(0.3, float(c.typo_rate)))
        c.clear_after_lines = max(0, int(c.clear_after_lines))
        c.minutes = max(0.0, float(c.minutes))
        c.start_delay = max(0.0, float(c.start_delay))
        c.resume_after = max(0.0, float(c.resume_after))
        c.terminal_timeout = max(10.0, float(c.terminal_timeout))
        c.daily_hours = max(0.0, min(24.0, float(c.daily_hours)))
        try:
            hh, mm = (int(v) for v in str(c.schedule_start).split(":"))
            c.schedule_start = f"{max(0, min(23, hh)):02d}:{max(0, min(59, mm)):02d}"
        except ValueError:
            c.schedule_start = "03:00"
        c.mouse_resume = max(0.3, float(c.mouse_resume))
        c.serve_seconds = max(5.0, float(c.serve_seconds))
        c.monitor = int(c.monitor)
        if c.mode not in ("both", "mouse", "type"):
            c.mode = "both"
        if c.editor not in ("vscode", "notepad", "focused"):
            c.editor = "vscode"
        if c.source not in ("mixed", "generated", "spreadsheets", "projects", "snippets", "file"):
            c.source = "mixed"
        c.gen_languages = [l for l in c.gen_languages if l in GEN_LANGUAGES] or list(GEN_LANGUAGES)
        return c


class Bot:
    def __init__(self):
        self.cfg = Config()
        self.state = "idle"     # idle | starting | running | paused | you | break | stopped
        self._stop = threading.Event()
        self._run = threading.Event()
        self._lock = threading.Lock()
        self._threads = []
        self._user_paused = False
        self.logs = deque(maxlen=300)
        self.editor = None
        self.monitor = None
        self._energy = 1.0
        # input tracking
        self._acting = False
        self._act_end = 0.0
        self._last_user = 0.0
        self._last_esc = 0.0
        self._need_refocus = False
        self._listeners = []
        human.on_interfere = lambda: self._user_input("mouse")
        # live mirror of the work, for the dashboard's editor / agent panels
        self.events = deque(maxlen=200)
        self._event_id = 0
        self.activity = ""
        self.live = {"project": "", "files": [], "done": [], "file": "", "text": ""}
        self.terminal = deque(maxlen=400)   # output of commands the bot ran
        self.current_files = {}             # rel path -> source of the project being written
        self.stop_reason = ""               # why the last run ended
        self.started_by = ""                # "user" or "schedule"
        self._job_iter = None               # the never-ending project rotation
        self._need_caret = False            # the bot clicked in the code: caret back to the end
        # _hands set = the bot may send keystrokes (cleared when you type, or click into
        # another window); _mouse set = the bot may move the mouse (cleared while you move it)
        self._hands = threading.Event()
        self._hands.set()
        self._mouse = threading.Event()
        self._mouse.set()
        self._last_mouse = 0.0
        self._clicked = 0.0         # time of your last click (focus may have moved)
        self._click_seen = 0.0
        self._bg_ready = False      # first disk write after a takeover waits for VS Code's autosave
        self._cur_path = None       # file being written (VS Code)
        self._proc = None           # running background command
        self._reset_stats()

    # ------------------------------------------------------------ utilities
    def log(self, msg):
        line = time.strftime("%H:%M:%S ") + str(msg)
        self.logs.append(line)
        print(line, flush=True)
        # also to a file: when it starts by itself at login / 3 AM there's no window to read
        try:
            path = os.path.join(LOG_DIR, "invotech360.log")
            os.makedirs(LOG_DIR, exist_ok=True)
            if os.path.exists(path) and os.path.getsize(path) > 2_000_000:
                os.replace(path, path + ".old")
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(time.strftime("%Y-%m-%d ") + line + "\n")
        except OSError:
            pass

    def event(self, kind, title, detail=""):
        """A step for the dashboard's agent timeline (plan, create, write, verify, ...)."""
        self._event_id += 1
        self.events.append({"id": self._event_id, "t": time.time(), "kind": kind,
                            "title": title, "detail": detail})

    def live_status(self, since=0):
        lv = self.live
        return {"project": lv["project"], "files": lv["files"], "done": lv["done"],
                "file": lv["file"], "text": lv["text"], "activity": self.activity,
                "line": self.stats["line"], "lines_total": self.stats["lines_total"],
                "hands": self._hands.is_set(), "mouse": self._mouse.is_set(),
                "background": self._background(),
                "terminal": list(self.terminal)[-200:],
                "events": [e for e in self.events if e["id"] > since]}

    def _reset_stats(self):
        self.stats = {"chars": 0, "lines": 0, "files": 0, "projects": 0, "mouse_moves": 0,
                      "typos": 0, "scrolls": 0, "breaks": 0, "takeovers": 0,
                      "verified": 0, "mismatched": 0, "commands": 0,
                      "project": "", "file": "", "line": 0, "lines_total": 0,
                      "file_index": 0, "files_total": 0, "started_at": None, "ends_at": None,
                      "resume_in": 0}

    def _halt(self):
        """Stop, pause, or you grabbed the mouse - aborts the bot's mouse moves instantly."""
        return self._stop.is_set() or not self._run.is_set() or not self._mouse.is_set()

    def _halt_keys(self):
        return self._stop.is_set() or not self._run.is_set() or not self._hands.is_set()

    def _background(self):
        """True while you have the keyboard/mouse but the bot keeps writing on disk."""
        return self.running and self.state == "you" and not self._hands.is_set()

    def _can_background(self):
        return (self.cfg.background_typing and self.cfg.mode != "mouse" and self.editor is not None
                and self.editor.kind == "vscode")

    def _gate_mouse(self):
        while self._gate() and not self._mouse.is_set():
            self._stop.wait(0.1)
        return not self._stop.is_set()

    def _gate_hands(self):
        """Wait until the bot may use the mouse/keyboard (or stop)."""
        while self._gate() and not self._hands.is_set():
            self._stop.wait(0.25)
        return not self._stop.is_set()

    @contextmanager
    def _act(self):
        """Hold this while sending any mouse/keyboard input (one sender at a time;
        also lets the input listener tell the bot's events apart from yours)."""
        with self._lock:
            self._acting = True
            try:
                yield
            finally:
                self._acting = False
                self._act_end = time.time()

    def _wait(self, seconds):
        end = time.time() + seconds
        while not self._stop.is_set():
            if not self._run.is_set():
                self._run.wait(0.2)
                end += 0.2
                continue
            left = end - time.time()
            if left <= 0:
                return True
            self._stop.wait(min(left, 0.2))
        return False

    def _gate(self):
        while not self._stop.is_set() and not self._run.is_set():
            self._run.wait(0.2)
        return not self._stop.is_set()

    @property
    def running(self):
        return any(t.is_alive() for t in self._threads)

    def make_editor(self, cfg=None):
        cfg = cfg or self.cfg
        if cfg.source == "spreadsheets":            # Excel projects: Excel (or WPS) instead of VS Code
            from .office import OfficeEditor
            if not isinstance(self.editor, OfficeEditor):
                self.editor = OfficeEditor(cfg.workspace_dir, log=self.log)
            return self.editor
        if cfg.editor == "vscode":
            ws = os.path.abspath(os.path.expanduser(cfg.workspace_dir))
            if not (isinstance(self.editor, VSCodeEditor) and self.editor.ws == ws):
                self.editor = VSCodeEditor(cfg.workspace_dir, log=self.log)
            self.editor.keep_finished = cfg.keep_finished
        elif cfg.editor == "notepad":
            if not isinstance(self.editor, NotepadEditor) or self.editor.kind != "notepad":
                self.editor = NotepadEditor(log=self.log)
        else:
            self.editor = FocusedWindowEditor(log=self.log)
        return self.editor

    def setup_screen(self, cfg=None):
        """Pick the monitor, confine the mouse to it and place the editor there."""
        cfg = cfg or self.cfg
        self.monitor = pick_monitor(cfg.monitor)
        human.set_bounds(self.monitor.rect)
        if self.editor is not None:
            self.editor.screen = self.monitor.work
        return self.monitor

    def open_editor(self, cfg=None):
        cfg = cfg or self.cfg
        self.make_editor(cfg)
        self.setup_screen(cfg)
        ok = self.editor.open()
        if ok and cfg.maximize:
            self.editor.place(self.monitor.work)
        if ok and hasattr(self.editor, "clean_start"):
            with self._act():
                self.editor.clean_start()       # no old files, terminals or side bars
        return ok

    # ------------------------------------------------------------- controls
    def start(self, cfg_dict=None):
        if self.running:
            return False, "already running"
        self.cfg = Config.from_dict(cfg_dict)
        self.stop_reason = ""
        self.started_by = "user"
        self.make_editor()
        self._stop.clear()
        self._run.set()
        self._user_paused = False
        self._reset_stats()
        self.live = {"project": "", "files": [], "done": [], "file": "", "text": ""}
        self.terminal.clear()
        self._job_iter = None
        self._hands.set()
        self._mouse.set()
        self._bg_ready = False
        self.state = "starting"
        t = threading.Thread(target=self._main, daemon=True, name="codebot-main")
        self._threads = [t]
        t.start()
        return True, "started"

    def stop(self, reason="user"):
        """reason: "user" (Stop / Esc Esc - stays stopped until the next scheduled start)
        or "schedule" (the daily window ended or the daily limit was reached)."""
        self.stop_reason = reason
        if self.running:
            self.log("Stopping..." if reason == "user" else f"Stopping ({reason})")
        self._stop.set()
        self._run.set()
        self._hands.set()
        self._mouse.set()
        proc = self._proc
        if proc and proc.poll() is None:
            self._kill(proc)
        self.state = "stopped"
        return True, "stopped"

    def pause(self):
        if self.running and self.state in ("running", "you", "break"):
            self._user_paused = True
            self._run.clear()
            self.state = "paused"
            self.log("Paused")
            self.event("pause", "Paused", "")
        return True, self.state

    def resume(self):
        if self.running and self._run.is_set() and not self._hands.is_set():
            self._take_back()
            self.state = "running"
            self.log("Resumed - bot has the keyboard and mouse again")
            self.event("resume", "Took the keyboard back", "")
            return True, self.state
        if self.running and not self._run.is_set():
            self._user_paused = False
            self._need_refocus = True
            self._run.set()
            self._take_back()
            self._mouse.set()
            self.state = "running"
            self.log("Resumed")
            self.event("resume", "Resumed", "")
        return True, self.state

    def toggle_pause(self):
        return self.resume() if not self._run.is_set() else self.pause()

    def status(self):
        s = dict(self.stats)
        s["uptime"] = int(time.time() - s["started_at"]) if s["started_at"] else 0
        if self.state == "you" and self.cfg.resume_after:
            s["resume_in"] = max(0, int(self.cfg.resume_after - (time.time() - self._last_user)))
        state = self.state
        if not self.running and state not in ("idle", "stopped"):
            state = "stopped"
        return {"state": state, "running": self.running, "config": asdict(self.cfg),
                "stats": s, "logs": list(self.logs)[-60:],
                "editor": self.editor.name if self.editor and self.editor.name else "",
                "monitor": self.monitor.label() if self.monitor else "",
                "projects": list_projects()}

    # ------------------------------------------------- keyboard / mouse watch
    def start_listeners(self):
        """Global hotkeys (Esc Esc = stop, F9 = pause) and 'you took over' detection."""
        if self._listeners:
            return True
        try:
            from pynput import keyboard, mouse
        except ImportError:
            self.log("pynput not installed: no Esc-Esc kill switch or takeover detection")
            return False

        # Windows and macOS mark synthetic input reliably; on Linux/X11 pynput reports
        # every key as "not injected", so there we go by timing instead.
        flag_reliable = sys.platform.startswith("win") or sys.platform == "darwin"

        def on_press(key, injected=None):
            if injected:
                return
            if not flag_reliable:
                injected = None
            if key == keyboard.Key.esc:
                now = time.time()
                if now - self._last_esc < DOUBLE_ESC_WINDOW:
                    self._last_esc = 0
                    if self.running:
                        self.log("Esc Esc - kill switch")
                        self.stop()
                    return
                self._last_esc = now
            elif key == keyboard.Key.f9:
                self.toggle_pause()
                return
            if injected is None and (self._acting or time.time() - self._act_end < 0.3):
                return  # can't tell, probably our own keystroke
            self._user_input("keyboard")

        def on_move(x, y, injected=None):
            if injected:
                return
            lp = human.last_pos
            d = math.hypot(x - lp[0], y - lp[1]) if lp else 999
            busy = self._acting or time.time() - max(self._act_end, human.last_move_time) < 0.5
            if d > (60 if busy else 6):
                self._user_input("mouse")

        def on_click(x, y, button, pressed, injected=None):
            if not pressed or (injected and flag_reliable):
                return
            if not flag_reliable and (self._acting or time.time() - self._act_end < 0.3):
                return  # the bot's own click (it only clicks while holding the controls)
            self._user_input("click")

        def on_scroll(x, y, dx, dy, injected=None):
            if not injected and not self._acting and time.time() - self._act_end > 0.3:
                self._user_input("scroll")

        try:
            kl = keyboard.Listener(on_press=on_press)
            ml = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
            for listener in (kl, ml):
                listener.daemon = True
                listener.start()
            self._listeners = [kl, ml]
            return True
        except Exception as exc:  # noqa: BLE001
            self.log(f"Input listener failed ({exc}); Esc-Esc / takeover detection off")
            return False

    def _user_input(self, what):
        """what: mouse | click | scroll | keyboard."""
        now = time.time()
        self._last_user = now
        if what != "keyboard":
            self._last_mouse = now
        if not (self.running and self.cfg.detect_user) or self.state not in ("running", "you"):
            return
        if what != "keyboard":
            # sharing the mouse: let go of it, keep typing in VS Code (moving the mouse
            # doesn't change which window gets the keystrokes)
            if self._mouse.is_set():
                self._mouse.clear()
                self.stats["takeovers"] += 1
                self.log("You're using the mouse - bot let go of it and keeps typing")
            if what == "click":
                self._clicked = now   # checked before the next keystroke: did focus leave VS Code?
            return
        self._lose_keys("You're typing")

    def _lose_keys(self, why):
        """Stop sending keystrokes (they'd land wherever you are)."""
        self._last_user = time.time()          # counts as you being busy: no instant take-back
        if not self._hands.is_set() or self.state not in ("running", "you"):
            return
        after = (f"takes it back after {self.cfg.resume_after:.0f}s idle" if self.cfg.resume_after
                 else "press Resume / F9 to give it back")
        self._need_refocus = True
        self.stats["takeovers"] += 1
        if self._can_background():
            self._hands.clear()
            self._bg_ready = False
            self.state = "you"
            self.log(f"{why} - bot let go of the keyboard, keeps writing the file in the background ({after})")
            self.event("you", f"{why} - keyboard is yours", "the code keeps being written in the background · " + after)
        else:
            self._hands.clear()
            self._run.clear()
            self.state = "you"
            self.log(f"{why} - bot paused ({after})")
            self.event("you", f"{why} - bot paused", after)

    def _check_click(self):
        """After you click: if VS Code is no longer the active window, stop sending keys.
        A click inside VS Code just means the caret moved - put it back at the end."""
        if self._clicked <= self._click_seen:
            return self._hands.is_set()
        self._click_seen = self._clicked
        time.sleep(0.12)  # let the window manager switch focus
        active = self.editor.is_active() if self.editor and hasattr(self.editor, "is_active") else None
        if active is False or (active is None and self.editor and self.editor.kind != "focused"):
            self._lose_keys("You clicked into another window")
            return False
        self._need_refocus = True
        return self._hands.is_set()

    def _take_back(self):
        if not self._hands.is_set():
            self._need_refocus = True
            self._hands.set()

    def _check_auto_resume(self):
        now = time.time()
        if (not self._mouse.is_set() and self._run.is_set() and self.state in ("running", "you")
                and now - self._last_mouse >= self.cfg.mouse_resume):
            self._mouse.set()   # you stopped moving the mouse: the bot takes it right back
        if (self.state == "you" and self.cfg.resume_after and not self._user_paused
                and now - self._last_user >= self.cfg.resume_after):
            self._need_refocus = True
            self._take_back()
            self._mouse.set()
            self.state = "running"
            self._run.set()
            self.log("You've been idle - bot takes the keyboard back")
            self.event("resume", "You're idle - back to typing in VS Code", "")

    def _refocus_if_needed(self):
        """After a pause, bring the editor back and put the caret back at the end."""
        if self._need_refocus and self.editor and self.editor.kind != "focused":
            self._need_refocus = False
            if self._cur_path and hasattr(self.editor, "show_file"):
                self.editor.show_file(self._cur_path)   # its tab, freshly reloaded from disk
            else:
                self.editor.focus(force=True)
            time.sleep(0.25)
            pyautogui.hotkey(*doc_end_keys())
            time.sleep(0.15)

    # ------------------------------------------------------------ main loop
    def _main(self):
        cfg = self.cfg
        try:
            self.start_listeners()
            self.setup_screen()
            self.log(f"Using {self.monitor.label()}")
            if cfg.auto_open_editor and cfg.mode != "mouse":
                if not self.open_editor():
                    self.log("Editor could not be opened yet - carrying on, will try again with each file")
            if cfg.start_delay:
                self.log(f"Starting in {cfg.start_delay:.0f}s...")
                if not self._wait(cfg.start_delay):
                    return
            self.stats["started_at"] = time.time()
            if cfg.minutes:
                self.stats["ends_at"] = time.time() + cfg.minutes * 60
            self.state = "running"
            self.log(f"Running: {cfg.mode}, {cfg.source} -> {self.editor.name}, {cfg.wpm} wpm")
            self.log("Kill switch: press Esc twice. F9 pauses.")
            self.event("start", "Agent started", f"{cfg.mode} · {cfg.source} -> {self.editor.name or self.editor.kind} · {cfg.wpm} wpm")

            workers = []
            if cfg.mode in ("both", "mouse"):
                workers.append(threading.Thread(target=self._safe, args=(self._mouse_loop,), daemon=True))
            if cfg.mode in ("both", "type"):
                workers.append(threading.Thread(target=self._safe, args=(self._type_loop,), daemon=True))
            if cfg.breaks:
                workers.append(threading.Thread(target=self._safe, args=(self._break_loop,), daemon=True))
            self._threads.extend(workers)
            for w in workers:
                w.start()

            while not self._stop.is_set():
                if self.stats["ends_at"] and time.time() >= self.stats["ends_at"]:
                    self.log("Time limit reached")
                    self.stop_reason = "time limit"
                    self._stop.set()
                    self._run.set()
                self._check_auto_resume()
                time.sleep(0.25)
            for w in workers:
                w.join(timeout=3)
        finally:
            self.state = "stopped"
            self.activity = ""
            self.log("Stopped")
            self.event("stop", "Agent stopped", "")

    def _safe(self, fn):
        """Run a worker forever: if it hits an error (or ever runs out of work) it starts
        again after a short pause. Only Stop / Esc Esc / the time limit end the run."""
        failures = 0
        while not self._stop.is_set():
            try:
                fn()
                if self._stop.is_set():
                    return
                self.log(f"{fn.__name__.strip('_').replace('_', ' ')} finished - starting the next round")
                failures = 0
                delay = 3
            except FailSafe:
                # your cursor is in a screen corner: treat it as "you have the mouse"
                self._last_mouse = time.time()
                self._mouse.clear()
                delay = 1
            except Exception as exc:  # noqa: BLE001
                failures += 1
                delay = min(60, 5 * failures)
                self.log(f"Problem in {fn.__name__}: {exc!r} - recovering, carrying on in {delay}s")
                self.event("warn", "Recovered from a problem", f"{exc!r} · carrying on in {delay}s")
            self._need_refocus = True
            if not self._wait(delay):
                return

    # ---------------------------------------------------------------- mouse
    def _mouse_loop(self):
        """The hand on the mouse. In VS Code every move has a reason that fits what the bot
        is doing: resting by the line being typed, placing the caret, reading and hovering
        code while thinking, scrolling back over a finished file, watching the terminal,
        looking at the running app next to the code."""
        while self._gate_mouse():
            did_move = False
            with self._act():                     # one sender at a time (X11 isn't thread-safe)
                if self._halt():
                    continue
                layout = None
                if self.editor is not None and self.editor.kind == "vscode" and hasattr(self.editor, "layout"):
                    try:
                        layout = self.editor.layout()
                    except Exception:  # noqa: BLE001
                        layout = None
                if layout is not None:
                    did_move = self._purposeful_move(layout)
                else:
                    did_move = self._idle_move()
            if did_move:
                self.stats["mouse_moves"] += 1
            if not self._wait(random.uniform(self.cfg.mouse_min, self.cfg.mouse_max)):
                return

    def _vscode_in_front(self):
        """Clicks and scrolls only when VS Code is the window you'd hit (never yours)."""
        if not self._hands.is_set():
            return False
        active = self.editor.is_active() if hasattr(self.editor, "is_active") else None
        return active is True

    def _purposeful_move(self, layout):
        from .vscode_ui import point_in
        act, stop, r = self.activity, self._halt, random.random()
        text = layout.editor_text()
        front = self._vscode_in_front()
        if act == "typing":
            # the hand rests near where the code is growing (the caret is low in the view)
            if r < 0.55:
                human.move_to(*point_in(text, fx=random.uniform(0.25, 0.6), fy=random.uniform(0.62, 0.9)),
                              speed=0.7, stop=stop)
            elif r < 0.8:
                human.micro_drift(stop=stop)
            else:   # follow the last few lines that were written
                human.read_lines(text, stop=stop)
            return True
        if act == "thinking":
            if r < 0.45:
                human.read_lines(text, stop=stop)                     # eyes follow the code up the screen
            elif r < 0.75 or not front:
                # hover a name to see its definition / type pop-up
                human.move_to(*point_in(text, fx=random.uniform(0.05, 0.35), fy=random.uniform(0.2, 0.85)),
                              speed=0.8, stop=stop)
                time.sleep(random.uniform(0.8, 2.0))
            else:
                # click at the end of the code to put the caret where the next line goes
                human.move_to(*point_in(text, fx=random.uniform(0.35, 0.7), fy=random.uniform(0.75, 0.92)), stop=stop)
                if not stop():
                    time.sleep(random.uniform(0.1, 0.3))
                    pyautogui.click()
                    self._need_caret = True
            return True
        if act == "reviewing":
            # scroll back over the file that was just written, read it, come back down
            human.move_to(*point_in(text), stop=stop)
            if front and self.cfg.scroll and not stop():
                notches = random.randint(3, 8)
                for _ in range(notches):
                    if stop():
                        break
                    pyautogui.scroll(random.choice([2, 3]))
                    time.sleep(random.uniform(0.25, 0.7))
                    self.stats["scrolls"] += 1
                human.read_lines(text, stop=stop)
                for _ in range(notches):
                    if stop():
                        break
                    pyautogui.scroll(-3)
                    time.sleep(random.uniform(0.1, 0.3))
            else:
                human.read_lines(text, stop=stop)
            return True
        if act == "terminal":
            # watch the command's output in the terminal panel
            human.move_to(*point_in(layout.panel(), fx=random.uniform(0.1, 0.6), fy=random.uniform(0.2, 0.9)),
                          speed=0.7, stop=stop)
            if r < 0.3:
                human.micro_drift(stop=stop)
            return True
        if act == "serving":
            # look at the running app in the browser next to the code
            side = layout.side()
            human.move_to(*point_in(side), stop=stop)
            if front and self.cfg.scroll and r < 0.6 and not stop():
                for _ in range(random.randint(1, 3)):
                    pyautogui.scroll(random.choice([-3, -2, 2]))
                    time.sleep(random.uniform(0.4, 1.0))
                self.stats["scrolls"] += 1
            return True
        # between projects / starting up: look over the explorer and the code
        if r < 0.5:
            human.move_to(*point_in(text), stop=stop)
        else:
            human.micro_drift(stop=stop)
        return True

    def _idle_move(self):
        """Notepad / focused window: no VS Code layout to work with."""
        r = random.random()
        l, t, w, h = self.editor.region() if self.editor else human.bounds()
        if r < 0.5:
            human.micro_drift(stop=self._halt)
        elif r < 0.85:
            human.read_lines((l, t, w, h), stop=self._halt)
        else:
            bx, by, bw, bh = human.bounds()
            human.move_to(bx + random.uniform(0.1, 0.9) * bw, by + random.uniform(0.1, 0.9) * bh, stop=self._halt)
        return True

    # ------------------------------------------------------------- sources
    def _jobs(self):
        """Yield (project, files, meta) forever. meta: scaffold files + terminal steps."""
        cfg = self.cfg
        if cfg.source == "spreadsheets":
            from .sheets import sheets_cycle
            for p in sheets_cycle():
                self.log(f"New Excel project: {p['title']}")
                yield p["name"], p["files"], p
            return
        if cfg.source in ("generated", "mixed"):
            # never ends: a new project, then (mixed) the next library project, and so on
            library = project_cycle(cfg.projects) if cfg.source == "mixed" and list_projects() else None
            for p in generated_cycle(only=cfg.gen_languages):
                self.log(f"New project idea: {p['name']} - {p['title']} in {p['language']}, "
                         f"{len(p['records'])} record types, "
                         f"{sum(t.count(chr(10)) for _, t in p['files']):,} lines")
                yield p["name"], p["files"], p
                if library is not None:
                    name, files = next(library)
                    yield name, files, {"scaffold": project_scaffold(name, [r for r, _ in files])}
            return
        for job in self._library_jobs():
            if len(job) == 2:
                name, files = job
                yield name, files, {"scaffold": project_scaffold(name, [r for r, _ in files])
                                    if cfg.source == "projects" else []}
            else:
                yield job

    def _library_jobs(self):
        cfg = self.cfg
        if cfg.source == "file" and cfg.custom_file:
            try:
                with open(cfg.custom_file, encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
                name = os.path.basename(cfg.custom_file)
                while True:
                    yield os.path.splitext(name)[0], [(name, content)]
            except OSError as exc:
                self.log(f"Can't read {cfg.custom_file}: {exc} - using projects instead")
        if cfg.source in ("projects", "file"):
            got_any = False
            for job in project_cycle(cfg.projects):
                got_any = True
                yield job
            if not got_any:
                self.log("No projects found in ./projects - using snippets")
        n = 0
        pool = pick_pool(cfg.languages)
        while True:
            files = []
            for lang, snippet in random.sample(pool, min(4, len(pool))):
                n += 1
                files.append((f"snippet_{n:02d}.{SNIPPET_EXT.get(lang, 'txt')}", snippet))
            yield "sandbox", files

    # --------------------------------------------------------------- typing
    def _char_delay(self, ch, base):
        if ch == " ":
            d = base * random.uniform(1.0, 1.8)
        elif ch.isupper() or ch in SHIFTED:
            d = base * random.uniform(1.3, 2.2)
        elif ch.isdigit():
            d = base * random.uniform(1.0, 1.6)
        elif ch.isalpha():
            d = base * random.uniform(0.5, 1.2)
        else:
            d = base * random.uniform(1.1, 1.8)
        if random.random() < 0.03:
            d += random.uniform(0.2, 0.8) * self.cfg.think  # micro-hesitation
        return d

    def _in_front(self):
        """Is the bot's window the one that will receive the keys? If not: stop typing."""
        if self.editor is None or self.editor.kind not in ("vscode", "office"):
            return True
        if self.editor.is_active() is False:
            self._lose_keys("VS Code isn't the window in front")
            return False
        return self._modifiers_clear() or (self._lose_keys("A Ctrl/Alt/Win key is held down") or False)

    def _modifiers_clear(self, wait=2.0):
        """True when no Ctrl / Alt / Windows key is physically held (Windows; elsewhere
        pynput's takeover detection covers it). Waits up to `wait` seconds for a release."""
        if not IS_WIN:
            return True
        try:
            import ctypes
            state = ctypes.windll.user32.GetAsyncKeyState
        except Exception:  # noqa: BLE001
            return True
        end = time.time() + wait
        while True:
            if not any(state(vk) & 0x8000 for vk in (0x11, 0x12, 0x5B, 0x5C)):   # Ctrl, Alt, LWin, RWin
                return True
            if time.time() > end:
                return False
            time.sleep(0.05)

    def _type_text(self, text, base, mirror=True):
        """Type with real keystrokes. Returns how many characters were typed (fewer if you
        took the keyboard mid-way), or None if the bot was stopped."""
        cfg = self.cfg
        i = 0
        while i < len(text):
            if self._stop.is_set():
                return None
            if not self._run.is_set():
                if not self._gate():
                    return None
            if not self._hands.is_set() or not self._check_click():
                return i
            self._refocus_if_needed()  # you may have clicked elsewhere meanwhile
            # a Ctrl / Alt / Win key held down (by you, anywhere) would turn the bot's letters
            # into shortcuts (zoom out, open panels...): wait until it's released
            if not self._modifiers_clear():
                self._lose_keys("A Ctrl/Alt/Win key is held down")
                return i
            # never type into another window
            every = 1 if IS_WIN else 40        # Windows: checked before every single key
            if i % every == 0 and self.editor is not None and self.editor.kind in ("vscode", "office") \
                    and self.editor.is_active() is False:
                self._lose_keys("VS Code isn't the window in front")
                return i
            ch = text[i]
            if cfg.typo_rate and i > 0 and ch.lower() in NEIGHBORS and random.random() < cfg.typo_rate:
                wrong = random.choice(NEIGHBORS[ch.lower()])
                pyautogui.write(wrong.upper() if ch.isupper() else wrong)
                time.sleep(base * random.uniform(2, 5))
                pyautogui.press("backspace")
                time.sleep(base * random.uniform(1, 2.5))
                self.stats["typos"] += 1
            pyautogui.write(ch)
            if mirror:
                self.live["text"] += ch
                self.stats["chars"] += 1
            time.sleep(self._char_delay(ch, base))
            # hesitation: back up over the last few characters and retype them
            if ch == " " and i > 4 and random.random() < cfg.typo_rate * 0.6:
                k = random.randint(2, min(4, i))
                time.sleep(random.uniform(0.3, 0.8))
                for _ in range(k):
                    pyautogui.press("backspace")
                    time.sleep(base * random.uniform(0.7, 1.1))
                for c in text[i - k + 1:i + 1]:
                    pyautogui.write(c)
                    time.sleep(self._char_delay(c, base))
            i += 1
        return i

    # ------------------------------------------------- background (on disk)
    def _flush_disk(self):
        if not self._cur_path:
            return
        try:
            with open(self._cur_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(self.live["text"])
        except OSError as exc:
            self.log(f"Can't write {self._cur_path}: {exc}")

    def _bg_write(self, full, pos, base):
        """You have the keyboard: keep writing straight into the file, character by character
        at the same pace (VS Code shows the file growing). Returns the new position as soon as
        the bot gets the keyboard back, or None if stopped."""
        if not self._bg_ready:
            # give VS Code's autosave (1.5s) time to save what was typed with keystrokes,
            # so the editor tab isn't "dirty" when the file changes underneath it
            if not self._wait(1.8):
                return None
            self._bg_ready = True
        self.activity = "background"
        while pos < len(full):
            if self._hands.is_set():
                return pos
            if not self._gate():
                return None
            ch = full[pos]
            if not self._wait(self._char_delay(ch, base)):
                return None
            self.live["text"] += ch
            self.stats["chars"] += 1
            pos += 1
            self._flush_disk()
        return pos

    def _line_pause(self, line):
        s = line.strip()
        k = self.cfg.think
        if random.random() < 0.035:
            return random.uniform(5, 14) * k      # stops to think / read docs
        if not s:
            return random.uniform(0.5, 1.8) * k
        if BLOCK_START.match(s):
            return random.uniform(1.8, 5.0) * k   # planning the next function/class
        if s.startswith(("#", "//", "/*", "*", "--", '"""')):
            return random.uniform(1.0, 2.8) * k
        if s.startswith(CONTROL):
            return random.uniform(0.6, 2.0) * k
        return random.uniform(0.2, 1.1) * k

    def _review(self):
        """Arrow up a few lines as if re-reading, then come back."""
        k = random.randint(2, 8)
        for _ in range(k):
            if self._halt_keys():
                break
            pyautogui.press("up")
            time.sleep(random.uniform(0.1, 0.35))
        time.sleep(random.uniform(1.0, 3.0))
        for _ in range(k):
            pyautogui.press("down")
            time.sleep(random.uniform(0.06, 0.2))
        pyautogui.hotkey(*doc_end_keys())

    def _type_line(self, full, pos, indent, base):
        """Type `full` (indent + code + newline) from `pos` with keystrokes, exactly like a
        person: indent, the code with its typos and hesitations, Enter. Returns the new
        position (early if you took the keyboard), or None if stopped."""
        if not self._in_front():
            return pos
        while pos < indent:
            if not self._hands.is_set() or not self._check_click():
                return pos
            pyautogui.press("space")
            self.live["text"] += " "
            pos += 1
            time.sleep(base * random.uniform(0.15, 0.35))
        body_end = len(full) - (1 if full.endswith("\n") else 0)
        if pos < body_end:
            n = self._type_text(full[pos:body_end], base)
            if n is None:
                return None
            pos += n
            if pos < body_end:
                return pos
        if pos < len(full) and self._hands.is_set() and self._in_front():
            pyautogui.press("enter")
            self.live["text"] += "\n"
            pos += 1
        return pos

    def _type_document(self, content):
        cfg = self.cfg
        content = content.replace("\r\n", "\n").expandtabs(4)
        ends_with_newline = content.endswith("\n")
        lines = content.split("\n")
        if ends_with_newline:
            lines = lines[:-1]
        self.stats["lines_total"] = len(lines)
        lines_since_clear = 0
        for idx, line in enumerate(lines):
            if not self._gate():
                return False
            # energy drifts slowly over the session (focused vs tired)
            self._energy = min(1.25, max(0.75, self._energy + random.uniform(-0.03, 0.03)))
            pause = self._line_pause(line) / self._energy
            self.activity = "thinking" if pause > 1.5 else "typing"
            if pause > 5:
                self.event("think", "Thinking", f"{pause:.0f}s before line {idx + 1}")
            if not self._wait(pause):
                return False
            base = 60.0 / (cfg.wpm * 5) / self._energy * random.lognormvariate(0, 0.12)
            stripped = line.lstrip(" ")
            indent = len(line) - len(stripped)
            nl = "\n" if (idx < len(lines) - 1 or ends_with_newline) else ""
            full = " " * indent + stripped + nl
            pos = 0          # how much of `full` is written so far
            while pos < len(full):
                if not self._gate():
                    return False
                if self._hands.is_set():
                    with self._act():
                        if not self._hands.is_set() or not self._check_click():
                            continue
                        self._refocus_if_needed()
                        if self._need_caret and self.editor.kind != "focused":
                            pyautogui.hotkey(*doc_end_keys())
                            self._need_caret = False
                        if pos == 0 and cfg.keep_focus and self.editor.kind != "focused":
                            self.editor.focus()
                            pyautogui.hotkey(*doc_end_keys())  # caret back to end, whatever happened
                        self.activity = "typing"
                        pos = self._type_line(full, pos, indent, base)
                        if pos is None:
                            return False
                elif self._can_background() and self._cur_path:
                    pos = self._bg_write(full, pos, base)
                    if pos is None:
                        return False
                elif not self._gate_hands():
                    return False
            self.stats["lines"] += 1
            self.stats["line"] = idx + 1
            lines_since_clear += 1
            if (self.editor.kind == "notepad" and cfg.clear_after_lines
                    and lines_since_clear >= cfg.clear_after_lines):
                with self._act():
                    self.editor.clear()
                self.live["text"] = ""
                lines_since_clear = 0
            if not self._hands.is_set():
                continue
            if cfg.review_moves and self.editor.kind != "focused" and stripped and random.random() < 0.03:
                with self._act():
                    if not self._halt_keys():
                        self._review()
            elif random.random() < 0.02:
                with self._act():
                    if not self._halt_keys():
                        pyautogui.hotkey("command" if sys.platform == "darwin" else "ctrl", "s")
        return True

    # ----------------------------------------------------------- spreadsheets
    def _type_sheet(self, rows):
        """Type a table into Excel: a cell, Tab, the next cell... Enter at the end of a row
        (Excel goes back to column A). Then the header row is made bold."""
        base = 60.0 / (self.cfg.wpm * 5)
        self.stats["lines_total"] = len(rows)
        for idx, row in enumerate(rows):
            if not self._gate_hands():
                return False
            self._energy = min(1.25, max(0.75, self._energy + random.uniform(-0.03, 0.03)))
            pause = random.uniform(0.3, 1.6) * self.cfg.think if row else 0.3
            self.activity = "thinking" if pause > 1.2 else "typing"
            if not self._wait(pause):
                return False
            with self._act():
                if not self._hands.is_set():
                    continue
                if self.editor.is_active() is False:
                    self.editor.focus(force=True)
                    time.sleep(0.4)
                    if self.editor.is_active() is False:
                        continue                         # Excel isn't in front: don't type anywhere
                self.activity = "typing"
                for c, cell in enumerate(row):
                    if cell:
                        if self._type_text(str(cell), base / self._energy) is None:
                            return False
                        if not cell.startswith("=") and not re.fullmatch(r"-?[\d.,]+", cell):
                            pyautogui.press("delete")       # drop any AutoComplete suggestion
                    if c < len(row) - 1:
                        pyautogui.press("tab")
                        self.live["text"] += "\t"
                        time.sleep(base * random.uniform(0.8, 2.0))
                pyautogui.press("enter")
                self.live["text"] += "\n"
            self.stats["lines"] += 1
            self.stats["line"] = idx + 1
        with self._act():
            if self._hands.is_set() and self.editor.is_active() is not False:
                pyautogui.hotkey("ctrl", "home")
                pyautogui.hotkey("shift", "space")          # the header row
                pyautogui.hotkey("ctrl", "b")
                time.sleep(0.3)
                pyautogui.hotkey("ctrl", "home")
        return True

    def _type_loop(self):
        if self._job_iter is None:          # one rotation per run: survives recoveries
            self._job_iter = self._jobs()
        for project, files, meta in self._job_iter:
            if not self._gate():
                return
            with self._act():
                hands = self._hands.is_set()
                if self.cfg.maximize and self.monitor and hands:
                    self.editor.place(self.monitor.work)
                self.editor.begin_project(project, interactive=hands)
                self._write_scaffold(meta.get("scaffold") or [])
            self.stats.update(project=project, files_total=len(files), file_index=0)
            self.stats["projects"] += 1
            self.live.update(project=project, files=[r for r, _ in files], done=[], file="", text="")
            self.current_files = dict(files)
            self.current_files.update(dict(meta.get("scaffold") or []))
            self.event("plan", f"Planned {project}", f"{len(files)} files: " +
                       ", ".join(r for r, _ in files[:6]) + (" ..." if len(files) > 6 else ""))
            for i, (rel, content) in enumerate(files, 1):
                if not self._gate():
                    return
                self.stats.update(file=rel, file_index=i, line=0)
                self.live.update(file=rel, text="")
                self.event("create", f"Created {rel}", f"{len(content)} rows" if isinstance(content, list)
                           else f"{content.count(chr(10)) + 1} lines")
                self.log(f"Writing {project}/{rel}")
                with self._act():
                    hands = self._hands.is_set()
                    # while you're busy: just create the file (VS Code's explorer shows it);
                    # its tab opens when the bot gets the keyboard back
                    path = self.editor.begin_file(rel, show=hands)
                    self._cur_path = path
                    if hands:
                        self._bg_ready = False
                    self._need_refocus = not hands
                done = self._type_sheet(content) if isinstance(content, list) else self._type_document(content)
                if not done:
                    return
                with self._act():
                    if self._hands.is_set():
                        ok = self.editor.end_file(path, content)
                    else:
                        self._flush_disk()
                        ok = self.editor.verify(path, content) if hasattr(self.editor, "verify") else None
                self.stats["files"] += 1
                self.live["done"].append(rel)
                if ok is True:
                    self.stats["verified"] += 1
                    self.event("verify", f"Verified {rel}", "saved file matches the source")
                elif ok is False:
                    self.event("warn", f"{rel} differs", "you typed in it, or the editor changed something")
                    self.stats["mismatched"] += 1
                    self.log(f"  {rel}: saved file differs from source (you typed in it, or the editor changed something)")
                self.activity = "reviewing"
                if not self._wait(random.uniform(6, 20) * self.cfg.think):   # between files
                    return
            self.log(f"Finished project {project}")
            self.event("done", f"Finished {project}", f"{len(files)} files written")
            if self.cfg.terminal_after_project and not self._run_commands(project, meta.get("steps")):
                return
            if not self._wait(random.uniform(25, 60) * self.cfg.think):
                return

    # -------------------------------------------------------------- preview
    _shot = (0.0, None)

    def screenshot_jpeg(self, max_width=1280, quality=70):
        """A JPEG of the bot's screen (VS Code), for the dashboard's live preview."""
        now = time.time()
        if now - self._shot[0] < 0.6 and self._shot[1]:
            return self._shot[1]
        mon = self.monitor or pick_monitor(self.cfg.monitor)
        x, y, w, h = mon.rect
        img = None
        try:
            from PIL import ImageGrab
            kw = {"all_screens": True} if sys.platform.startswith("win") else {}
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h), **kw)
        except Exception:  # noqa: BLE001
            try:
                img = pyautogui.screenshot(region=(x, y, w, h))
            except Exception:  # noqa: BLE001
                return None
        import io
        img = img.convert("RGB")
        if img.width > max_width:
            img = img.resize((max_width, round(img.height * max_width / img.width)))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality)
        data = buf.getvalue()
        self._shot = (now, data)
        return data

    # ------------------------------------------------------------- terminal
    def _term(self, line):
        self.terminal.append(line)

    def _write_scaffold(self, scaffold):
        """Small files a project needs but nobody types (go.mod, package.json, README...)."""
        project_dir = getattr(self.editor, "project_dir", None)
        if not project_dir or not scaffold:
            return
        for rel, text in scaffold:
            path = os.path.join(project_dir, *rel.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        self.log(f"Set up {len(scaffold)} project file(s): " + ", ".join(r for r, _ in scaffold))

    def _run_commands(self, project, steps=None):
        """Build / test / run the project like a developer: with the keyboard, the bot opens
        VS Code's terminal, cd's into the project and types each command; an app started with
        `serve:` is left running and opened in VS Code's built-in browser, then stopped with
        Ctrl+C. While you have the keyboard, the same steps run in the background and the
        output goes to the dashboard."""
        project_dir = getattr(self.editor, "project_dir", None)
        steps = steps or project_commands(project)
        if not steps or not project_dir or not os.path.isdir(project_dir):
            return True
        self.event("plan", "Opening the terminal", " · ".join(s["cmd"] for s in steps))
        term_open = False   # a VS Code terminal in the project folder exists
        for step in steps:
            if not self._wait(random.uniform(3, 8) * self.cfg.think):
                return False
            cmd = localize_command(step["cmd"])
            self.stats["commands"] += 1
            ok = None
            if self._hands.is_set() and self.editor.kind == "vscode":
                ok = self._vscode_command(cmd, step, project_dir, term_open)
                if ok is None:
                    return False
                term_open = term_open or ok
            if not ok:   # you have the keyboard (or no VS Code): run it in the background
                if not self._run_background(cmd, project_dir, step):
                    return False
        if self.editor.kind == "vscode" and term_open and self._hands.is_set():
            with self._act():
                self.editor.focus_editor()
        self._need_caret = True
        self._need_refocus = True
        return True

    def _vscode_command(self, cmd, step, project_dir, term_open):
        """Type one command into VS Code's terminal. True = done there, False = you grabbed
        the keyboard before it was sent (run it in the background instead), None = stopped."""
        base = 60.0 / (self.cfg.wpm * 5)
        self.activity = "terminal"
        with self._act():
            if not self._hands.is_set() or not self._check_click():
                return False
            mouse = self._mouse.is_set()
            if not term_open:
                how = self.editor.open_terminal_ui(use_mouse=mouse, stop=self._halt)
                self.event("term", "Opened a terminal",
                           "Terminal > New Terminal (clicked in the menu bar)" if how == "menu"
                           else "Terminal: Create New Terminal")
                self._term(f"(VS Code terminal) $ cd \"{project_dir}\"")
                n = self._type_text(f'cd "{project_dir}"', base, mirror=False)
                if n is None:
                    return None
                pyautogui.press("enter")
                time.sleep(random.uniform(0.8, 1.6))
            else:
                self.editor.click_terminal(use_mouse=mouse, stop=self._halt)
            # first say in plain words what's about to happen, then run it
            note = explain_command(cmd, step["serve"])
            if self._type_text(f'echo "{note}"', base, mirror=False) is None:
                return None
            pyautogui.press("enter")
            time.sleep(random.uniform(0.6, 1.2))
            n = self._type_text(cmd, base, mirror=False)
            if n is None:
                return None
            if n < len(cmd):
                return False
            pyautogui.press("enter")
        self._term(f"(VS Code terminal) $ {cmd}")
        if not step["serve"]:
            self.event("term", f"$ {cmd}", explain_command(cmd))
            # the bot can't read VS Code's terminal, so give the command a realistic time
            return True if self._wait((step["wait"] or guess_wait(cmd)) * random.uniform(0.9, 1.3)) else None
        self.event("term", f"$ {cmd}", "starting the app in the VS Code terminal")
        self.activity = "serving"
        if not self._wait(step["wait"] or random.uniform(6, 10)):
            return None
        if step["open"] and self._gate_hands():
            with self._act():
                if self._hands.is_set():
                    self.editor.open_browser(step["open"], beside=True)
                    self.event("term", f"Opened {step['open']}", "in VS Code's browser, next to the code")
        if not self._wait(self.cfg.serve_seconds * random.uniform(0.8, 1.2)):
            return None
        # stop the app: back to its terminal, Ctrl+C
        if not self._gate_hands():
            return None
        with self._act():
            self.editor.click_terminal(use_mouse=self._mouse.is_set(), stop=self._halt)
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.8)
            pyautogui.hotkey("ctrl", "c")
        self.activity = "terminal"
        self._term("(VS Code terminal) ^C")
        self.event("term", "Stopped the app", "Ctrl+C")
        return True

    def _run_background(self, cmd, cwd, step=None):
        serve = bool(step and step["serve"])
        self.activity = "terminal"
        self.event("term", f"$ {cmd}", "starting the app in the background" if serve else "running in the background")
        self._term(f"$ {cmd}")
        started = time.time()
        win = sys.platform.startswith("win")
        try:
            kw = {"creationflags": 0x08000000} if win else {"start_new_session": True}
            self._proc = proc = subprocess.Popen(
                cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", **kw)
        except OSError as exc:
            self._term(f"could not start: {exc}")
            self.event("warn", f"{cmd} failed to start", str(exc))
            return True

        def pump():
            for line in proc.stdout:
                self._term(line.rstrip("\n"))
        reader = threading.Thread(target=pump, daemon=True)
        reader.start()
        limit = self.cfg.serve_seconds if serve else self.cfg.terminal_timeout
        opened = False
        while proc.poll() is None:
            if self._stop.is_set():
                self._kill(proc)
                return False
            if serve and step["open"] and not opened and time.time() - started > 6:
                opened = True
                self._term(f"GET {step['open']} -> {self._probe(step['open'])}")
            if time.time() - started > limit:
                self._kill(proc)
                self._term("^C" if serve else f"(stopped after {limit:.0f}s)")
                break
            time.sleep(0.2)
        reader.join(timeout=2)
        code = proc.returncode
        self._proc = None
        took = time.time() - started
        self._term(f"[exit {code} · {took:.1f}s]")
        if serve:
            self.event("term", "Stopped the app", f"ran {took:.0f}s")
        elif code == 0:
            self.event("verify", f"{cmd} passed", f"exit 0 in {took:.1f}s")
        else:
            self.event("warn", f"{cmd} exited with {code}", "see the Terminal tab")
        return True

    @staticmethod
    def _probe(url):
        import urllib.request
        try:
            with urllib.request.urlopen(url, timeout=4) as r:
                return f"{r.status} {r.reason}"
        except Exception as exc:  # noqa: BLE001
            return f"no answer ({exc.__class__.__name__})"

    @staticmethod
    def _kill(proc):
        """Stop the command and everything it started (servers spawn children)."""
        try:
            if sys.platform.startswith("win"):
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=10)
            else:
                import signal
                os.killpg(proc.pid, signal.SIGINT)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
        except (OSError, subprocess.SubprocessError):
            try:
                proc.kill()
            except OSError:
                pass

    # --------------------------------------------------------------- breaks
    def _break_loop(self):
        while self._wait(random.uniform(180, 480)):
            if self.state != "running":
                continue
            dur = random.uniform(20, 90)
            self.log(f"Taking a {dur:.0f}s break")
            self.event("break", "Short break", f"{dur:.0f}s")
            self.stats["breaks"] += 1
            self._run.clear()
            self.state = "break"
            end = time.time() + dur
            while time.time() < end and not self._stop.is_set():
                time.sleep(0.2)
            if self._stop.is_set():
                return
            if self.state == "break":
                self._need_refocus = True
                self._run.set()
                self.state = "running"
                self.log("Back from break")


def monitors_info():
    return [m.to_dict() for m in get_monitors()]
