"""The bot: writes real projects file by file with human-like typing and mouse movement.

- Lives on one monitor (VS Code gets maximized there, the mouse never leaves it).
- Esc pressed twice quickly = kill switch. F9 = pause/resume.
- Notices when YOU use the mouse or keyboard, gets out of the way immediately and
  carries on after you've been idle for a while.
"""

import math
import os
import random
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
from .projects import list_projects, project_cycle
from .snippets import LANGUAGES, pick_pool

pyautogui.FAILSAFE = True  # mouse into a corner of the main screen = emergency stop
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
DOUBLE_ESC_WINDOW = 0.6  # seconds between the two Esc presses


@dataclass
class Config:
    editor: str = "vscode"             # vscode | notepad | focused
    source: str = "projects"           # projects | snippets | file
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
    detect_user: bool = True           # pause when you use the mouse/keyboard
    resume_after: float = 20.0         # resume after this many idle seconds (0 = stay paused)
    clear_after_lines: int = 150       # Notepad only: wipe scratch every N lines
    auto_open_editor: bool = True
    keep_focus: bool = True
    minutes: float = 0
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
        c.monitor = int(c.monitor)
        if c.mode not in ("both", "mouse", "type"):
            c.mode = "both"
        if c.editor not in ("vscode", "notepad", "focused"):
            c.editor = "vscode"
        if c.source not in ("projects", "snippets", "file"):
            c.source = "projects"
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
        self._reset_stats()

    # ------------------------------------------------------------ utilities
    def log(self, msg):
        line = time.strftime("%H:%M:%S ") + str(msg)
        self.logs.append(line)
        print(line, flush=True)

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
                "events": [e for e in self.events if e["id"] > since]}

    def _reset_stats(self):
        self.stats = {"chars": 0, "lines": 0, "files": 0, "projects": 0, "mouse_moves": 0,
                      "typos": 0, "scrolls": 0, "breaks": 0, "takeovers": 0,
                      "verified": 0, "mismatched": 0,
                      "project": "", "file": "", "line": 0, "lines_total": 0,
                      "file_index": 0, "files_total": 0, "started_at": None, "ends_at": None,
                      "resume_in": 0}

    def _halt(self):
        """Stop requested, or paused (for any reason) - used to abort mouse moves instantly."""
        return self._stop.is_set() or not self._run.is_set()

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
        return ok

    # ------------------------------------------------------------- controls
    def start(self, cfg_dict=None):
        if self.running:
            return False, "already running"
        self.cfg = Config.from_dict(cfg_dict)
        self.make_editor()
        self._stop.clear()
        self._run.set()
        self._user_paused = False
        self._reset_stats()
        self.live = {"project": "", "files": [], "done": [], "file": "", "text": ""}
        self.state = "starting"
        t = threading.Thread(target=self._main, daemon=True, name="codebot-main")
        self._threads = [t]
        t.start()
        return True, "started"

    def stop(self):
        if self.running:
            self.log("Stopping...")
        self._stop.set()
        self._run.set()
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
        if self.running and not self._run.is_set():
            self._user_paused = False
            self._need_refocus = True
            self._run.set()
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
            if pressed and not (injected and flag_reliable):
                self._user_input("mouse")  # the bot never clicks

        def on_scroll(x, y, dx, dy, injected=None):
            if not injected and not self._acting and time.time() - self._act_end > 0.3:
                self._user_input("mouse")

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
        self._last_user = time.time()
        if not (self.running and self.cfg.detect_user):
            return
        if self.state == "running":
            self._run.clear()
            self._need_refocus = True
            self.state = "you"
            self.stats["takeovers"] += 1
            after = (f"resumes after {self.cfg.resume_after:.0f}s idle" if self.cfg.resume_after
                     else "press Resume / F9 to continue")
            self.log(f"You took over the {what} - bot paused ({after})")
            self.event("you", f"You took over the {what}", after)

    def _check_auto_resume(self):
        if (self.state == "you" and self.cfg.resume_after and not self._user_paused
                and time.time() - self._last_user >= self.cfg.resume_after):
            self._need_refocus = True
            self.state = "running"
            self._run.set()
            self.log("You've been idle - bot continues")

    def _refocus_if_needed(self):
        """After a pause, bring the editor back and put the caret back at the end."""
        if self._need_refocus and self.editor and self.editor.kind != "focused":
            self._need_refocus = False
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
                    self.log("Editor could not be opened - stopping.")
                    return
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
        try:
            fn()
        except pyautogui.FailSafeException:
            self.log("Fail-safe triggered (mouse in a corner of the main screen)")
            self._stop.set()
            self._run.set()
        except Exception as exc:  # noqa: BLE001
            self.log(f"Error in {fn.__name__}: {exc!r}")
            self._stop.set()
            self._run.set()

    # ---------------------------------------------------------------- mouse
    def _mouse_loop(self):
        while self._gate():
            r = random.random()
            with self._act():  # all pyautogui calls stay under the lock (X11 isn't thread-safe)
                if self._halt():
                    continue
                l, t, w, h = self.editor.region() if self.editor else human.bounds()
                if r < 0.45:
                    human.micro_drift(stop=self._halt)
                elif r < 0.68:
                    human.read_lines((l, t, w, h), stop=self._halt)
                elif r < 0.80:  # glance at the file explorer / sidebar
                    human.move_to(l + w * random.uniform(0.04, 0.16), t + h * random.uniform(0.15, 0.7),
                                  stop=self._halt)
                elif r < 0.92 and self.cfg.scroll:
                    human.move_to(l + w * random.uniform(0.3, 0.7), t + h * random.uniform(0.3, 0.7),
                                  stop=self._halt)
                    for _ in range(random.randint(1, 4)):
                        if self._halt():
                            break
                        pyautogui.scroll(random.choice([-3, -2, -1, 1, 2]))
                        time.sleep(random.uniform(0.1, 0.4))
                    self.stats["scrolls"] += 1
                else:  # somewhere else on this screen
                    bx, by, bw, bh = human.bounds()
                    human.move_to(bx + random.uniform(0.1, 0.9) * bw, by + random.uniform(0.1, 0.9) * bh,
                                  stop=self._halt)
            self.stats["mouse_moves"] += 1
            if not self._wait(random.uniform(self.cfg.mouse_min, self.cfg.mouse_max)):
                return

    # ------------------------------------------------------------- sources
    def _jobs(self):
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

    def _type_text(self, text, base):
        cfg = self.cfg
        i = 0
        while i < len(text):
            if self._stop.is_set():
                return False
            if not self._run.is_set():
                if not self._gate():
                    return False
                self._refocus_if_needed()  # you may have clicked elsewhere meanwhile
            ch = text[i]
            if cfg.typo_rate and i > 0 and ch.lower() in NEIGHBORS and random.random() < cfg.typo_rate:
                wrong = random.choice(NEIGHBORS[ch.lower()])
                pyautogui.write(wrong.upper() if ch.isupper() else wrong)
                time.sleep(base * random.uniform(2, 5))
                pyautogui.press("backspace")
                time.sleep(base * random.uniform(1, 2.5))
                self.stats["typos"] += 1
            pyautogui.write(ch)
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
        return True

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
            if self._halt():
                break
            pyautogui.press("up")
            time.sleep(random.uniform(0.1, 0.35))
        time.sleep(random.uniform(1.0, 3.0))
        for _ in range(k):
            pyautogui.press("down")
            time.sleep(random.uniform(0.06, 0.2))
        pyautogui.hotkey(*doc_end_keys())

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
            with self._act():
                if not self._gate():
                    return False
                self._refocus_if_needed()
                if cfg.keep_focus and self.editor.kind != "focused":
                    self.editor.focus()
                    pyautogui.hotkey(*doc_end_keys())  # caret back to end, whatever happened
                for _ in range(indent):
                    pyautogui.press("space")
                    time.sleep(base * random.uniform(0.15, 0.35))
                self.live["text"] += " " * indent
                self.activity = "typing"
                if not self._type_text(stripped, base):
                    return False
                if idx < len(lines) - 1 or ends_with_newline:
                    pyautogui.press("enter")
                    self.live["text"] += "\n"
            self.stats["lines"] += 1
            self.stats["line"] = idx + 1
            lines_since_clear += 1
            if (self.editor.kind == "notepad" and cfg.clear_after_lines
                    and lines_since_clear >= cfg.clear_after_lines):
                with self._act():
                    self.editor.clear()
                self.live["text"] = ""
                lines_since_clear = 0
            if cfg.review_moves and self.editor.kind != "focused" and stripped and random.random() < 0.03:
                with self._act():
                    if not self._halt():
                        self._review()
            elif random.random() < 0.02:
                with self._act():
                    if not self._halt():
                        pyautogui.hotkey("command" if sys.platform == "darwin" else "ctrl", "s")
        return True

    def _type_loop(self):
        for project, files in self._jobs():
            if not self._gate():
                return
            with self._act():
                if self.cfg.maximize and self.monitor:
                    self.editor.place(self.monitor.work)
                self.editor.begin_project(project)
            self.stats.update(project=project, files_total=len(files), file_index=0)
            self.stats["projects"] += 1
            self.live.update(project=project, files=[r for r, _ in files], done=[], file="", text="")
            self.event("plan", f"Planned {project}", f"{len(files)} files: " +
                       ", ".join(r for r, _ in files[:6]) + (" ..." if len(files) > 6 else ""))
            for i, (rel, content) in enumerate(files, 1):
                if not self._gate():
                    return
                self.stats.update(file=rel, file_index=i, line=0)
                self.live.update(file=rel, text="")
                self.event("create", f"Created {rel}", f"{content.count(chr(10)) + 1} lines")
                self.log(f"Writing {project}/{rel}")
                with self._act():
                    path = self.editor.begin_file(rel)
                    self._need_refocus = False
                if not self._type_document(content):
                    return
                with self._act():
                    ok = self.editor.end_file(path, content)
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
            if not self._wait(random.uniform(25, 60) * self.cfg.think):
                return

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
