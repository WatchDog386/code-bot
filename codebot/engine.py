"""The bot: writes real projects file by file with human-like typing and mouse movement."""

import os
import random
import re
import sys
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field

import pyautogui

from . import human
from .editor import FocusedWindowEditor, NotepadEditor, VSCodeEditor, doc_end_keys
from .projects import list_projects, project_cycle
from .snippets import LANGUAGES, pick_pool

pyautogui.FAILSAFE = True  # mouse into a screen corner = emergency stop
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


@dataclass
class Config:
    editor: str = "vscode"             # vscode | notepad | focused
    source: str = "projects"           # projects | snippets | file
    projects: list = field(default_factory=list)   # empty = all
    workspace_dir: str = "~/dev-projects"
    languages: list = field(default_factory=lambda: list(LANGUAGES))
    custom_file: str = ""
    mode: str = "both"                 # both | mouse | type
    wpm: int = 55
    typo_rate: float = 0.015
    mouse_min: float = 3.0
    mouse_max: float = 10.0
    scroll: bool = True
    review_moves: bool = True          # sometimes arrow up to "re-read" code, then back
    breaks: bool = False
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
        c.wpm = max(5, min(300, int(c.wpm)))
        c.mouse_min = max(0.5, float(c.mouse_min))
        c.mouse_max = max(c.mouse_min, float(c.mouse_max))
        c.typo_rate = max(0.0, min(0.3, float(c.typo_rate)))
        c.clear_after_lines = max(0, int(c.clear_after_lines))
        c.minutes = max(0.0, float(c.minutes))
        c.start_delay = max(0.0, float(c.start_delay))
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
        self.state = "idle"
        self._stop = threading.Event()
        self._run = threading.Event()
        self._lock = threading.Lock()
        self._threads = []
        self._user_paused = False
        self.logs = deque(maxlen=300)
        self.editor = None
        self._energy = 1.0
        self._reset_stats()

    # ------------------------------------------------------------ utilities
    def log(self, msg):
        line = time.strftime("%H:%M:%S ") + str(msg)
        self.logs.append(line)
        print(line, flush=True)

    def _reset_stats(self):
        self.stats = {"chars": 0, "lines": 0, "files": 0, "projects": 0, "mouse_moves": 0,
                      "typos": 0, "scrolls": 0, "breaks": 0, "verified": 0, "mismatched": 0,
                      "project": "", "file": "", "line": 0, "lines_total": 0,
                      "file_index": 0, "files_total": 0, "started_at": None, "ends_at": None}

    def _stopped(self):
        return self._stop.is_set()

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
            if not (isinstance(self.editor, VSCodeEditor)
                    and self.editor.ws == os.path.abspath(os.path.expanduser(cfg.workspace_dir))):
                self.editor = VSCodeEditor(cfg.workspace_dir, log=self.log)
        elif cfg.editor == "notepad":
            if not isinstance(self.editor, NotepadEditor) or self.editor.kind != "notepad":
                self.editor = NotepadEditor(log=self.log)
        else:
            self.editor = FocusedWindowEditor(log=self.log)
        return self.editor

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
        s["uptime"] = int(time.time() - s["started_at"]) if s["started_at"] else 0
        state = self.state
        if not self.running and state not in ("idle", "stopped"):
            state = "stopped"
        return {"state": state, "running": self.running, "config": asdict(self.cfg),
                "stats": s, "logs": list(self.logs)[-60:],
                "editor": self.editor.name if self.editor and self.editor.name else "",
                "projects": list_projects()}

    # ------------------------------------------------------------ main loop
    def _main(self):
        cfg = self.cfg
        try:
            if cfg.auto_open_editor and cfg.mode != "mouse":
                if not self.editor.open():
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
            self.log("Fail-safe triggered (mouse in a screen corner)")
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
            with self._lock:  # all pyautogui calls stay under the lock (X11 isn't thread-safe)
                region = self.editor.region() if self.editor else (0, 0, *pyautogui.size())
                l, t, w, h = region
                if r < 0.40:
                    human.micro_drift(stop=self._stopped)
                elif r < 0.65:
                    human.read_lines(region, stop=self._stopped)
                elif r < 0.78:  # glance at the file explorer / sidebar
                    human.move_to(l + w * random.uniform(0.04, 0.16), t + h * random.uniform(0.15, 0.7),
                                  stop=self._stopped)
                elif r < 0.90 and self.cfg.scroll:
                    human.move_to(l + w * random.uniform(0.3, 0.7), t + h * random.uniform(0.3, 0.7),
                                  stop=self._stopped)
                    for _ in range(random.randint(1, 4)):
                        pyautogui.scroll(random.choice([-3, -2, -1, 1, 2]))
                        time.sleep(random.uniform(0.08, 0.35))
                    self.stats["scrolls"] += 1
                else:  # anywhere on screen
                    sw, sh = pyautogui.size()
                    human.move_to(random.uniform(0.1, 0.9) * sw, random.uniform(0.1, 0.9) * sh,
                                  stop=self._stopped)
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
            d = base * random.uniform(1.0, 1.7)
        elif ch.isupper() or ch in SHIFTED:
            d = base * random.uniform(1.2, 2.0)
        elif ch.isdigit():
            d = base * random.uniform(1.0, 1.5)
        elif ch.isalpha():
            d = base * random.uniform(0.45, 1.15)
        else:
            d = base * random.uniform(1.0, 1.6)
        if random.random() < 0.025:
            d += random.uniform(0.15, 0.6)  # micro-hesitation
        return d

    def _type_text(self, text, base):
        cfg = self.cfg
        i = 0
        while i < len(text):
            if self._stop.is_set():
                return False
            if not self._run.is_set() and not self._gate():
                return False
            ch = text[i]
            if cfg.typo_rate and i > 0 and ch.lower() in NEIGHBORS and random.random() < cfg.typo_rate:
                wrong = random.choice(NEIGHBORS[ch.lower()])
                pyautogui.write(wrong.upper() if ch.isupper() else wrong)
                time.sleep(base * random.uniform(1.5, 4))
                pyautogui.press("backspace")
                time.sleep(base * random.uniform(0.8, 2))
                self.stats["typos"] += 1
            pyautogui.write(ch)
            self.stats["chars"] += 1
            time.sleep(self._char_delay(ch, base))
            # hesitation: back up over the last few characters and retype them
            if ch == " " and i > 4 and random.random() < cfg.typo_rate * 0.6:
                k = random.randint(2, min(4, i))
                time.sleep(random.uniform(0.2, 0.6))
                for _ in range(k):
                    pyautogui.press("backspace")
                    time.sleep(base * random.uniform(0.6, 1.0))
                for c in text[i - k + 1:i + 1]:
                    pyautogui.write(c)
                    time.sleep(self._char_delay(c, base))
            i += 1
        return True

    def _line_pause(self, line):
        s = line.strip()
        if not s:
            return random.uniform(0.2, 0.9)
        if BLOCK_START.match(s):
            return random.uniform(0.8, 2.6)   # thinking about the next function/class
        if s.startswith(("#", "//", "/*", "*", "--", '"""')):
            return random.uniform(0.5, 1.6)
        if s.startswith(CONTROL):
            return random.uniform(0.3, 1.2)
        return random.uniform(0.05, 0.5)

    def _review(self):
        """Arrow up a few lines as if re-reading, then come back."""
        k = random.randint(2, 8)
        for _ in range(k):
            pyautogui.press("up")
            time.sleep(random.uniform(0.08, 0.3))
        time.sleep(random.uniform(0.8, 2.5))
        for _ in range(k):
            pyautogui.press("down")
            time.sleep(random.uniform(0.05, 0.18))
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
            self._energy = min(1.35, max(0.75, self._energy + random.uniform(-0.03, 0.03)))
            if not self._wait(self._line_pause(line) / self._energy):
                return False
            base = 60.0 / (cfg.wpm * 5) / self._energy * random.lognormvariate(0, 0.12)
            stripped = line.lstrip(" ")
            indent = len(line) - len(stripped)
            with self._lock:
                if cfg.keep_focus and self.editor.kind != "focused":
                    self.editor.focus()
                    pyautogui.hotkey(*doc_end_keys())  # caret back to end, whatever happened
                for _ in range(indent):
                    pyautogui.press("space")
                    time.sleep(base * random.uniform(0.15, 0.35))
                if not self._type_text(stripped, base):
                    return False
                if idx < len(lines) - 1 or ends_with_newline:
                    pyautogui.press("enter")
            self.stats["lines"] += 1
            self.stats["line"] = idx + 1
            lines_since_clear += 1
            if (self.editor.kind == "notepad" and cfg.clear_after_lines
                    and lines_since_clear >= cfg.clear_after_lines):
                with self._lock:
                    self.editor.clear()
                lines_since_clear = 0
            if cfg.review_moves and self.editor.kind != "focused" and stripped and random.random() < 0.03:
                with self._lock:
                    self._review()
            elif random.random() < 0.02:
                with self._lock:
                    pyautogui.hotkey("command" if sys.platform == "darwin" else "ctrl", "s")
        return True

    def _type_loop(self):
        for project, files in self._jobs():
            if not self._gate():
                return
            with self._lock:
                self.editor.begin_project(project)
            self.stats.update(project=project, files_total=len(files), file_index=0)
            self.stats["projects"] += 1
            for i, (rel, content) in enumerate(files, 1):
                if not self._gate():
                    return
                self.stats.update(file=rel, file_index=i, line=0)
                self.log(f"Writing {project}/{rel}")
                with self._lock:
                    path = self.editor.begin_file(rel)
                if not self._type_document(content):
                    return
                with self._lock:
                    ok = self.editor.end_file(path, content)
                self.stats["files"] += 1
                if ok is True:
                    self.stats["verified"] += 1
                elif ok is False:
                    self.stats["mismatched"] += 1
                    self.log(f"  {rel}: saved file differs from source (editor changed something?)")
                if not self._wait(random.uniform(2.5, 8)):   # pause between files
                    return
            self.log(f"Finished project {project}")
            if not self._wait(random.uniform(8, 20)):
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
