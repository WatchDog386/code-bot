"""What the agent's tools do on screen, in the VS Code window the bot opened.

write_file   -> the file is created, opened as a tab and typed (or written instantly)
edit_file    -> the change is made and the file shown in VS Code
run_command  -> typed into VS Code's terminal; its output is copied to .invotech/ and read back
start_server -> typed into a new VS Code terminal; the page opens in VS Code next to the code
spreadsheet  -> an .xlsx is opened in WPS Office / Excel and typed cell by cell

If you are using the keyboard at that moment, commands run in the background instead (the
output still goes to the agent and the dashboard), so nothing is ever typed into your window.
"""

import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pyautogui

IS_WIN = sys.platform.startswith("win")
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".invotech", ".pytest_cache"}
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def decode(data):
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16", "replace")
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", "replace")
    return data.decode("utf-8", "replace")


class VSCodeActions:
    def __init__(self, bot):
        self.bot = bot
        self.editor = bot.editor
        self.dir = bot.editor.project_dir
        self.inv = os.path.join(self.dir, ".invotech")
        os.makedirs(self.inv, exist_ok=True)
        self.term_open = False
        self.servers = []          # background server processes
        self.visible_servers = 0
        self.n = 0

    # ------------------------------------------------------------- basics
    def environment(self):
        tools = [t for t in ("python", "python3", "node", "npm", "go", "git", "java", "dotnet") if shutil.which(t)]
        return {"project_dir": self.dir,
                "os": "Windows" if IS_WIN else ("macOS" if sys.platform == "darwin" else "Linux"),
                "shell": "PowerShell (VS Code terminal)" if IS_WIN else os.path.basename(os.environ.get("SHELL", "bash")),
                "toolchain": ", ".join(tools) or "unknown"}

    def context(self):
        files = self.list_files(".")
        return "Existing files in the project:\n" + files if "(empty)" not in files else ""

    def should_stop(self):
        return self.bot._stop.is_set()

    def set_status(self, kind, text):
        self.bot.agent_status = text
        self.bot.activity = "thinking" if kind == "thinking" else "agent"

    def _path(self, rel):
        rel = (rel or ".").replace("\\", "/").lstrip("/")
        full = os.path.normpath(os.path.join(self.dir, rel))
        if os.path.commonpath([full, os.path.normpath(self.dir)]) != os.path.normpath(self.dir):
            raise ValueError("paths must stay inside the project folder")
        return full

    def _can_drive(self):
        """May the bot use keyboard/mouse in VS Code right now?"""
        return self.bot._hands.is_set() and self.editor.kind == "vscode"

    def run(self, name, args):
        fn = getattr(self, name, None)
        if name.startswith("_") or fn is None or name in ("run", "cleanup", "context", "environment"):
            return f"Error: unknown tool {name}"
        return fn(**args)

    # ------------------------------------------------------------- files
    def list_files(self, path="."):
        root = self._path(path)
        out = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP)
            for f in sorted(filenames):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, self.dir).replace(os.sep, "/")
                if rel.startswith(".codebot"):
                    continue
                out.append(f"{rel} ({os.path.getsize(full)} bytes)")
                if len(out) >= 200:
                    return "\n".join(out) + "\n…"
        return "\n".join(out) or "(empty)"

    def read_file(self, path):
        full = self._path(path)
        if not os.path.isfile(full):
            return f"Error: {path} doesn't exist"
        with open(full, "rb") as fh:
            data = fh.read(80_000)
        return decode(data)

    def write_file(self, path, content):
        full = self._path(path)
        rel = os.path.relpath(full, self.dir).replace(os.sep, "/")
        content = content.replace("\r\n", "\n")
        bot = self.bot
        if rel not in bot.live["files"]:
            bot.live["files"].append(rel)
        bot.live.update(file=rel, text="")
        bot.current_files[rel] = content
        bot.stats["files_total"] = len(bot.live["files"])
        os.makedirs(os.path.dirname(full), exist_ok=True)
        typed = False
        if bot.cfg.agent_typing == "type" and self._can_drive() and content.strip():
            with bot._act():
                bot.editor.project_dir = self.dir
                path_opened = self.editor.begin_file(rel, show=True)
                bot._cur_path = path_opened
                bot._need_refocus = False
            saved = (bot.cfg.wpm, bot.cfg.think, bot.cfg.review_moves, bot.cfg.typo_rate)
            bot.cfg.wpm, bot.cfg.think, bot.cfg.review_moves = bot.cfg.agent_wpm, 0.25, False
            bot.cfg.typo_rate = min(bot.cfg.typo_rate, 0.005)
            try:
                typed = bot._type_document(content)
            finally:
                bot.cfg.wpm, bot.cfg.think, bot.cfg.review_moves, bot.cfg.typo_rate = saved
            if not typed and bot._stop.is_set():
                return "Stopped"
            with bot._act():
                if bot._hands.is_set():
                    pyautogui.hotkey("command" if sys.platform == "darwin" else "ctrl", "s")
                    time.sleep(0.8)
        # the file on disk is always exactly the content (whatever the editor did while typing)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        if not typed and self._can_drive():
            with bot._act():
                self.editor.show_file(full)
        bot.live["text"] = content
        if rel not in bot.live["done"]:
            bot.live["done"].append(rel)
        bot.stats["files"] += 1
        return f"Wrote {rel} ({content.count(chr(10)) + 1} lines)"

    def edit_file(self, path, old, new):
        full = self._path(path)
        if not os.path.isfile(full):
            return f"Error: {path} doesn't exist"
        with open(full, encoding="utf-8") as fh:
            text = fh.read()
        count = text.count(old)
        if count != 1:
            return f"Error: the text to replace occurs {count} times in {path} (it must occur exactly once)"
        text = text.replace(old, new)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        rel = os.path.relpath(full, self.dir).replace(os.sep, "/")
        self.bot.current_files[rel] = text
        self.bot.live.update(file=rel, text=text)
        if self._can_drive():
            with self.bot._act():
                self.editor.show_file(full)
        line = text[:text.find(new)].count("\n") + 1 if new else 0
        return f"Edited {rel}" + (f" (around line {line})" if line else "")

    # ---------------------------------------------------------- terminal
    def _open_terminal(self):
        bot = self.bot
        base = 60.0 / (max(bot.cfg.agent_wpm, 120) * 5)
        if not self.term_open:
            self.editor.open_terminal_ui(use_mouse=bot._mouse.is_set(), stop=bot._halt)
            bot._type_text(f'cd "{self.dir}"', base, mirror=False)
            pyautogui.press("enter")
            time.sleep(0.8)
            self.term_open = True
        else:
            self.editor.click_terminal(use_mouse=bot._mouse.is_set(), stop=bot._halt)
        bot._need_caret = True
        return base

    def _wrap(self, command, out, code):
        """The command as typed, with its output also copied to a file the agent reads."""
        if IS_WIN:   # PowerShell, VS Code's default terminal on Windows
            return (f"$global:LASTEXITCODE=0; & {{ {command} }} *>&1 | Tee-Object -FilePath .invotech\\{out}; "
                    f"Set-Content -Encoding ascii .invotech\\{code} ([int]$LASTEXITCODE)")
        return f"{{ {command} ; echo $? > .invotech/{code}; }} 2>&1 | tee .invotech/{out}"

    def run_command(self, command, timeout=120):
        timeout = max(5, min(900, int(timeout or 120)))
        self.n += 1
        out, code = f"out-{self.n}.txt", f"exit-{self.n}.txt"
        out_p, code_p = os.path.join(self.inv, out), os.path.join(self.inv, code)
        bot = self.bot
        bot._term(f"$ {command}")
        if self._can_drive():
            with bot._act():
                base = self._open_terminal()
                n = bot._type_text(self._wrap(command, out, code), base, mirror=False)
                if n is None:
                    return "Stopped"
                pyautogui.press("enter")
            started = time.time()
            while time.time() - started < timeout and not bot._stop.is_set():
                if os.path.exists(code_p):
                    time.sleep(0.3)
                    break
                if time.time() - started > 10 and not os.path.exists(out_p):
                    bot._term("(the VS Code terminal didn't report back - running it in the background)")
                    return self._background(command, timeout)
                time.sleep(0.5)
            output = self._read(out_p)
            for line in output.splitlines()[-40:]:
                bot._term(line)
            if not os.path.exists(code_p):
                return f"Still running after {timeout}s (it keeps running in the terminal). Output so far:\n{output[-3000:]}"
            exit_code = self._read(code_p).strip() or "0"
            bot._term(f"[exit {exit_code}]")
            return f"exit code {exit_code}\n{output}"
        return self._background(command, timeout)

    def _read(self, path):
        try:
            with open(path, "rb") as fh:
                return ANSI.sub("", decode(fh.read()))
        except OSError:
            return ""

    def _background(self, command, timeout):
        kw = {"creationflags": 0x08000000} if IS_WIN else {}
        try:
            proc = subprocess.run(command, shell=True, cwd=self.dir, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=timeout, **kw)
        except subprocess.TimeoutExpired as exc:
            return f"Timed out after {timeout}s. Output so far:\n{(exc.stdout or '')[-3000:]}"
        output = (proc.stdout or "") + (proc.stderr or "")
        for line in output.splitlines()[-40:]:
            self.bot._term(line)
        self.bot._term(f"[exit {proc.returncode}]")
        return f"exit code {proc.returncode}\n{output}"

    def start_server(self, command, url):
        bot = self.bot
        bot._term(f"$ {command}   (server)")
        self.n += 1
        log = f"server-{self.n}.txt"
        if self._can_drive():
            with bot._act():
                base = 60.0 / (max(bot.cfg.agent_wpm, 120) * 5)
                self.editor.focus(force=True)
                self.editor._palette("Terminal: Create New Terminal", settle=2.5)
                bot._type_text(f'cd "{self.dir}"', base, mirror=False)
                pyautogui.press("enter")
                time.sleep(0.6)
                line = (f"& {{ {command} }} *>&1 | Tee-Object -FilePath .invotech\\{log}" if IS_WIN
                        else f"{command} 2>&1 | tee .invotech/{log}")
                bot._type_text(line, base, mirror=False)
                pyautogui.press("enter")
                bot._need_caret = True
            self.visible_servers += 1
        else:
            kw = {"creationflags": 0x08000000} if IS_WIN else {"start_new_session": True}
            fh = open(os.path.join(self.inv, log), "wb")
            self.servers.append(subprocess.Popen(command, shell=True, cwd=self.dir, stdout=fh, stderr=subprocess.STDOUT, **kw))
        answer = "no answer"
        log_path = os.path.join(self.inv, log)
        for tick in range(60):
            if bot._stop.is_set():
                return "Stopped"
            time.sleep(1)
            if tick == 15 and not self.servers and not os.path.exists(log_path):
                # the VS Code terminal didn't start it (other shell?): start it in the background
                bot._term("(starting the server in the background instead)")
                kw = {"creationflags": 0x08000000} if IS_WIN else {"start_new_session": True}
                fh = open(log_path, "wb")
                self.servers.append(subprocess.Popen(command, shell=True, cwd=self.dir, stdout=fh,
                                                     stderr=subprocess.STDOUT, **kw))
            try:
                with urllib.request.urlopen(url, timeout=3) as r:
                    answer = f"{r.status} {r.reason}: {r.read(400).decode('utf-8', 'replace')}"
                    break
            except urllib.error.HTTPError as exc:
                answer = f"{exc.code} {exc.reason}"
                break
            except Exception:  # noqa: BLE001 - not up yet
                continue
        bot._term(f"GET {url} -> {answer[:80]}")
        if answer != "no answer":
            self.open_browser(url)
        logs = self._read(os.path.join(self.inv, log))[-2000:]
        return f"Server started. {url} answered: {answer}\nServer output so far:\n{logs}"

    def open_browser(self, url):
        if self._can_drive():
            with self.bot._act():
                self.editor.open_browser(url, beside=True)
            self.bot.activity = "serving"
            return f"Opened {url} next to the code"
        return f"(VS Code is busy with you right now; {url} not opened)"

    # ------------------------------------------------------- spreadsheets
    def spreadsheet(self, file, rows):
        from .office import OfficeEditor
        bot = self.bot
        if not file.lower().endswith(".xlsx"):
            file += ".xlsx"
        rows = [[str(c) for c in (r or [])] for r in (rows or [])]
        office = OfficeEditor(os.path.dirname(self.dir), log=bot.log)
        office.project_dir = self.dir
        vscode = bot.editor
        bot.editor = office
        try:
            if not bot._gate_hands():
                return "Stopped"
            with bot._act():
                office.begin_file(file)
            bot.live.update(file=file, text="")
            if file not in bot.live["files"]:
                bot.live["files"].append(file)
            ok = bot._type_sheet(rows)
            with bot._act():
                office.end_file(office.current, rows)
        finally:
            bot.editor = vscode
        bot.live["done"].append(file)
        return f"Typed {len(rows)} rows into {file} in {office.name} and saved it" if ok else "Stopped"

    # ------------------------------------------------------------ cleanup
    def cleanup(self):
        for proc in self.servers:
            try:
                proc.kill()
            except OSError:
                pass
        if self.visible_servers and self._can_drive():
            try:
                with self.bot._act():
                    self.editor._palette("Terminal: Kill All Terminals", settle=1.0)
            except Exception:  # noqa: BLE001
                pass
