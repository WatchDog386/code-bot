"""The bot itself: mouse movement + human-like typing, with pause/stop and live stats."""

import random
import string
import sys
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field

import pyautogui

from .editor import Editor
from .snippets import LANGUAGES, chunk_file, pick_pool

pyautogui.FAILSAFE = True  # mouse into the top-left corner = emergency stop
pyautogui.PAUSE = 0

# keys next to each other on a QWERTY keyboard, used for realistic typos
NEIGHBORS = {
    "a": "qwsz", "b": "vghn", "c": "xdfv", "d": "serfcx", "e": "wsdr", "f": "drtgvc",
    "g": "ftyhbv", "h": "gyujnb", "i": "ujko", "j": "huikmn", "k": "jiolm", "l": "kop",
    "m": "njk", "n": "bhjm", "o": "iklp", "p": "ol", "q": "wa", "r": "edft", "s": "awedxz",
    "t": "rfgy", "u": "yhji", "v": "cfgb", "w": "qase", "x": "zsdc", "y": "tghu", "z": "asx",
}


@dataclass
class Config:
    mode: str = "both"                 # both | mouse | type
    wpm: int = 55
    languages: list = field(default_factory=lambda: list(LANGUAGES))
    custom_file: str = ""              # type this file instead of built-ins
    mouse_min: float = 2.0             # seconds between mouse moves
    mouse_max: float = 6.0
    typo_rate: float = 0.02            # chance per letter of a typo + correction
    scroll: bool = True                # random scroll wheel moves
    breaks: bool = False               # occasional 20-90s idle "coffee" breaks
    clear_after_lines: int = 150       # wipe scratch file after N lines (0 = never)
    strip_indent: bool = False         # True for editors that auto-indent (VS Code)
    auto_open_editor: bool = True      # open Notepad/TextEdit/gedit on start
    keep_focus: bool = True            # keep the scratch window in front
    minutes: float = 0                 # auto-stop after N minutes (0 = never)
    start_delay: float = 3.0

    @classmethod
    def from_dict(cls, d):
        base = asdict(cls())
        base.update({k: v for k, v in (d or {}).items() if k in base})
        c = cls(**base)
        c.wpm = max(5, min(300, int(c.wpm)))
        c.mouse_min = max(0.2, float(c.mouse_min))
        c.mouse_max = max(c.mouse_min, float(c.mouse_max))
        c.typo_rate = max(0.0, min(0.3, float(c.typo_rate)))
        c.clear_after_lines = max(0, int(c.clear_after_lines))
        c.minutes = max(0.0, float(c.minutes))
        c.start_delay = max(0.0, float(c.start_delay))
        if c.mode not in ("both", "mouse", "type"):
            c.mode = "both"
        return c


class Bot:
    def __init__(self):
        self.cfg = Config()
        self.state = "idle"            # idle | starting | running | paused | break | stopped
        self._stop = threading.Event()
        self._run = threading.Event()  # set = not paused
        self._lock = threading.Lock()
        self._threads = []
        self.logs = deque(maxlen=200)
        self._user_paused = False
        self.editor = Editor(log=self.log)
        self._reset_stats()

    # ------------------------------------------------------------ utilities
    def log(self, msg):
        line = time.strftime("%H:%M:%S ") + str(msg)
        self.logs.append(line)
        print(line, flush=True)

    def _reset_stats(self):
        self.stats = {"chars": 0, "lines": 0, "snippets": 0, "mouse_moves": 0,
                      "typos": 0, "scrolls": 0, "breaks": 0, "language": "",
                      "started_at": None, "ends_at": None}

    def _wait(self, seconds):
        """Sleep that respects stop and pause. Returns False if stopped."""
        end = time.time() + seconds
        while not self._stop.is_set():
            if not self._run.is_set():
                self._run.wait(0.2)
                end += 0.2  # don't count paused time
                continue
            left = end - time.time()
            if left <= 0:
                return True
            self._stop.wait(min(left, 0.2))
        return False

    def _gate(self):
        """Block while paused; return False if stopped."""
        while not self._stop.is_set() and not self._run.is_set():
            self._run.wait(0.2)
        return not self._stop.is_set()

    @property
    def running(self):
        return any(t.is_alive() for t in self._threads)

    # ------------------------------------------------------------- controls
    def start(self, cfg_dict=None):
        if self.running:
            return False, "already running"
        self.cfg = Config.from_dict(cfg_dict)
        self._stop.clear()
        self._run.set()
        self._user_paused = False
        self._reset_stats()
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
        if self.running and self._run.is_set():
            self._user_paused = True
            self._run.clear()
            self.state = "paused"
            self.log("Paused")
        return True, self.state

    def resume(self):
        if self.running and not self._run.is_set():
            self._user_paused = False
            self._run.set()
            self.state = "running"
            self.log("Resumed")
        return True, self.state

    def toggle_pause(self):
        return self.resume() if not self._run.is_set() else self.pause()

    def status(self):
        s = dict(self.stats)
        if s["started_at"]:
            s["uptime"] = int(time.time() - s["started_at"])
        else:
            s["uptime"] = 0
        state = self.state
        if not self.running and state not in ("idle", "stopped"):
            state = "stopped"
        return {"state": state,
                "running": self.running, "config": asdict(self.cfg), "stats": s,
                "logs": list(self.logs)[-40:], "editor": self.editor.name or "",
                "scratch_file": self.editor.path}

    # ------------------------------------------------------------ main loop
    def _main(self):
        cfg = self.cfg
        try:
            if cfg.auto_open_editor and cfg.mode != "mouse":
                self.editor.open()
            if cfg.start_delay:
                self.log(f"Starting in {cfg.start_delay:.0f}s...")
                if not self._wait(cfg.start_delay):
                    return
            self.stats["started_at"] = time.time()
            if cfg.minutes:
                self.stats["ends_at"] = time.time() + cfg.minutes * 60
            self.state = "running"
            self.log(f"Running: mode={cfg.mode}, {cfg.wpm} wpm")

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
                time.sleep(0.25)
            for w in workers:
                w.join(timeout=3)
        finally:
            self.state = "stopped"
            self.log("Stopped")

    def _safe(self, fn):
        try:
            fn()
        except pyautogui.FailSafeException:
            self.log("Fail-safe triggered (mouse in top-left corner)")
            self._stop.set()
            self._run.set()
        except Exception as exc:  # noqa: BLE001
            self.log(f"Error in {fn.__name__}: {exc!r}")
            self._stop.set()
            self._run.set()

    # ---------------------------------------------------------------- mouse
    def _mouse_loop(self):
        w, h = pyautogui.size()
        margin = 80
        tweens = [pyautogui.easeInOutQuad, pyautogui.easeOutQuad,
                  pyautogui.easeInOutSine, pyautogui.easeOutCubic]
        while self._gate():
            x0, y0 = pyautogui.position()
            # mostly short drifts, sometimes a long trip across the screen
            if random.random() < 0.7:
                x = min(max(margin, x0 + random.randint(-350, 350)), w - margin)
                y = min(max(margin, y0 + random.randint(-250, 250)), h - margin)
            else:
                x, y = random.randint(margin, w - margin), random.randint(margin, h - margin)
            dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
            with self._lock:
                pyautogui.moveTo(x, y, duration=min(1.8, 0.25 + dist / 900 * random.uniform(0.8, 1.4)),
                                 tween=random.choice(tweens))
            self.stats["mouse_moves"] += 1
            if self.cfg.scroll and random.random() < 0.15:
                with self._lock:
                    pyautogui.scroll(random.choice([-3, -2, -1, 1, 2, 3]))
                self.stats["scrolls"] += 1
            if not self._wait(random.uniform(self.cfg.mouse_min, self.cfg.mouse_max)):
                return

    # --------------------------------------------------------------- typing
    def _pool(self):
        if self.cfg.custom_file:
            try:
                pool = chunk_file(self.cfg.custom_file)
                if pool:
                    return pool
                self.log("Custom file is empty, using built-in snippets")
            except OSError as exc:
                self.log(f"Can't read custom file ({exc}); using built-in snippets")
        return pick_pool(self.cfg.languages)

    def _type_char(self, ch, char_delay):
        cfg = self.cfg
        if (cfg.typo_rate and ch.lower() in NEIGHBORS and random.random() < cfg.typo_rate):
            wrong = random.choice(NEIGHBORS[ch.lower()])
            pyautogui.write(wrong.upper() if ch.isupper() else wrong)
            time.sleep(char_delay * random.uniform(1.5, 4))
            pyautogui.press("backspace")
            time.sleep(char_delay * random.uniform(0.8, 2))
            self.stats["typos"] += 1
        pyautogui.write(ch)
        self.stats["chars"] += 1
        d = char_delay * random.uniform(0.45, 1.6)
        if ch in " (.:,=" and random.random() < 0.06:
            d += random.uniform(0.25, 0.9)  # "thinking"
        time.sleep(d)

    def _clear(self):
        mod = "command" if sys.platform == "darwin" else "ctrl"
        with self._lock:
            if self.cfg.keep_focus:
                self.editor.focus(force=True)
            pyautogui.hotkey(mod, "a")
            pyautogui.press("backspace")
        self.log("Cleared scratch file")

    def _type_loop(self):
        pool = self._pool()
        lines_since_clear = 0
        last = None
        while self._gate():
            choices = [p for p in pool if p is not last] or pool
            lang, snippet = last = random.choice(choices)
            self.stats["language"] = lang
            for line in snippet.splitlines():
                if not self._gate():
                    return
                char_delay = 60.0 / (self.cfg.wpm * 5)
                text = line.lstrip() if self.cfg.strip_indent else line
                with self._lock:
                    if self.cfg.keep_focus:
                        self.editor.focus()
                    for ch in text:
                        if self._stop.is_set():
                            return
                        if not self._run.is_set() and not self._gate():
                            return  # paused mid-line: wait, then finish the line
                        if ch == "\t":
                            pyautogui.press("tab")
                        elif ch in string.printable:
                            self._type_char(ch, char_delay)
                    pyautogui.press("enter")
                    if self.cfg.strip_indent:
                        pyautogui.press("home")
                self.stats["lines"] += 1
                lines_since_clear += 1
                if not self._wait(random.uniform(0.15, 0.9)):
                    return
            self.stats["snippets"] += 1
            with self._lock:
                pyautogui.press("enter")
            if self.cfg.clear_after_lines and lines_since_clear >= self.cfg.clear_after_lines:
                if not self._wait(random.uniform(1, 3)):
                    return
                self._clear()
                lines_since_clear = 0
            if not self._wait(random.uniform(1.5, 5)):
                return

    # --------------------------------------------------------------- breaks
    def _break_loop(self):
        while self._wait(random.uniform(180, 480)):
            dur = random.uniform(20, 90)
            self.log(f"Taking a {dur:.0f}s break")
            self.stats["breaks"] += 1
            self._run.clear()
            self.state = "break"
            end = time.time() + dur
            while time.time() < end and not self._stop.is_set():
                time.sleep(0.2)
            if self._stop.is_set():
                return
            if not self._user_paused:
                self._run.set()
                self.state = "running"
                self.log("Back from break")
