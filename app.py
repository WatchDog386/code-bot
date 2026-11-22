#!/usr/bin/env python3
"""
Invotech 360 control panel, served at http://localhost:8765

    python app.py                  # opens VS Code on your chosen screen + the dashboard
    python app.py --autostart      # also starts the bot immediately
    python app.py --port 9000 --no-browser --no-editor

Kill switch (anywhere): press Esc twice quickly. F9 = pause/resume.
It never stops on its own: only Esc Esc, Stop, or the time limit end a run.
"""

import argparse
import json
import os
import sys
import threading
import webbrowser
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from codebot.engine import Bot, Config, monitors_info
    from codebot.projects import list_projects, project_files
    from codebot.snippets import LANGUAGES
    from codebot.gen import LANGUAGES as GEN_LANGUAGES
    from codebot.gen.schema import DOMAINS as GEN_DOMAINS
except ImportError as exc:
    print(f"Missing dependency ({exc}). Run:\n    python -m pip install -r requirements.txt")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = os.path.join(HERE, "settings.json")
INDEX = os.path.join(HERE, "web", "index.html")
FAVICON = os.path.join(HERE, "web", "favicon.png")

bot = Bot()


def load_settings():
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            return Config.from_dict(json.load(fh))
    except (OSError, ValueError):
        return Config()


from codebot.schedule import Scheduler  # noqa: E402

scheduler = Scheduler(bot, lambda: load_settings(), os.path.join(HERE, "usage.json"))


def start_by_hand(body):
    ok, msg = scheduler.allow_start()
    if not ok:
        bot.log(msg)
        return False, msg
    return bot.start(body)


def save_settings(cfg_dict):
    from dataclasses import asdict
    try:
        with open(SETTINGS, "w", encoding="utf-8") as fh:
            json.dump(asdict(Config.from_dict(cfg_dict)), fh, indent=2)
    except OSError:
        pass


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal clean
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n))
        except ValueError:
            return {}

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        if url.path == "/api/live":
            try:
                since = int(q.get("since", 0))
            except ValueError:
                since = 0
            return self._send(200, bot.live_status(since))
        if url.path == "/api/screen.jpg":
            data = bot.screenshot_jpeg()
            if not data:
                return self._send(503, {"error": "screen capture not available"})
            return self._send(200, data, "image/jpeg")
        if url.path == "/api/project" and q.get("name") == bot.live["project"] and bot.current_files:
            return self._send(200, {"name": q["name"], "files": [
                {"path": rel, "lines": text.count("\n") + 1, "bytes": len(text)}
                for rel, text in bot.current_files.items()]})
        if url.path == "/api/file" and q.get("project") == bot.live["project"] and q.get("path") in bot.current_files:
            return self._send(200, {"path": q["path"], "text": bot.current_files[q["path"]]})
        if url.path == "/api/project":
            name = q.get("name", "")
            if name not in list_projects():
                return self._send(404, {"error": "no such project"})
            files = project_files(name)
            return self._send(200, {"name": name, "files": [
                {"path": rel, "lines": text.count("\n") + 1, "bytes": len(text)} for rel, text in files]})
        if url.path == "/api/file":
            name = q.get("project", "")
            if name not in list_projects():
                return self._send(404, {"error": "no such project"})
            for rel, text in project_files(name):
                if rel == q.get("path"):
                    return self._send(200, {"path": rel, "text": text})
            return self._send(404, {"error": "no such file"})
        if self.path in ("/", "/index.html"):
            with open(INDEX, "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if self.path == "/api/status":
            st = bot.status()
            st["schedule"] = scheduler.status()
            return self._send(200, st)
        if self.path == "/manifest.webmanifest":
            return self._send(200, {
                "id": "/", "name": "Invotech 360", "short_name": "Invotech 360",
                "description": "Coding agent dashboard", "start_url": "/", "scope": "/",
                "display": "standalone", "background_color": "#0E2135", "theme_color": "#0E2135",
                "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                          {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                          {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
            }, "application/manifest+json")
        if self.path in ("/icon-512.png", "/icon-192.png"):
            name = "invotech360.png" if "512" in self.path else "invotech360-192.png"
            with open(os.path.join(HERE, "assets", name), "rb") as fh:
                return self._send(200, fh.read(), "image/png")
        if self.path == "/sw.js":
            # tiny service worker: lets Edge / Chrome install the dashboard as an app
            return self._send(200, (
                'self.addEventListener("install", () => self.skipWaiting());\n'
                'self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));\n'
                'self.addEventListener("fetch", (e) => e.respondWith(fetch(e.request)));\n').encode(),
                "text/javascript")
        if self.path in ("/favicon.ico", "/favicon.png"):
            with open(FAVICON, "rb") as fh:
                return self._send(200, fh.read(), "image/png")
        if self.path == "/api/settings":
            from dataclasses import asdict
            return self._send(200, {"config": asdict(load_settings()), "languages": LANGUAGES,
                                    "generator": {"languages": list(GEN_LANGUAGES),
                                                  "domains": {k: v[0] for k, v in GEN_DOMAINS.items()}},
                                    "projects": list_projects(), "monitors": monitors_info()})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        # only accept requests from our own page (blocks other websites)
        origin = self.headers.get("Origin", "")
        if origin and not origin.startswith(("http://localhost", "http://127.0.0.1")):
            return self._send(403, {"error": "forbidden"})
        body = self._body()
        routes = {
            "/api/start": lambda: (save_settings(body), start_by_hand(body))[1],
            "/api/stop": lambda: bot.stop("user"),
            "/api/pause": bot.pause,
            "/api/resume": bot.resume,
            "/api/open-editor": lambda: (bot.open_editor(Config.from_dict(body) if body else load_settings()),
                                         "opened"),
            "/api/settings": lambda: (save_settings(body), (True, "saved"))[1],
        }
        fn = routes.get(self.path)
        if not fn:
            return self._send(404, {"error": "not found"})
        ok, msg = fn()
        st = bot.status()
        st["schedule"] = scheduler.status()
        self._send(200, {"ok": bool(ok), "message": msg, "status": st})


def open_dashboard(url):
    """Open the dashboard in its own app window (Edge / Chrome "app" mode: no tabs or
    address bar, the Invotech 360 icon in the taskbar). Falls back to the normal browser."""
    import shutil
    import subprocess
    candidates = []
    if sys.platform.startswith("win"):
        for base in (os.environ.get("ProgramFiles(x86)", ""), os.environ.get("ProgramFiles", ""),
                     os.environ.get("LOCALAPPDATA", "")):
            if base:
                candidates += [os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
                               os.path.join(base, "Google", "Chrome", "Application", "chrome.exe")]
    elif sys.platform == "darwin":
        candidates += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                       "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        candidates += [shutil.which(n) or "" for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge")]
    for exe in candidates:
        if exe and os.path.exists(exe):
            try:
                subprocess.Popen([exe, f"--app={url}", "--window-size=1440,900"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except OSError:
                pass
    webbrowser.open(url)


def already_running(port):
    """Is our own dashboard answering on this port?"""
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=2) as r:
            return "state" in json.loads(r.read())
    except Exception:  # noqa: BLE001
        return False


def main():
    p = argparse.ArgumentParser(description="Invotech 360 control panel")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true", help="don't open the dashboard")
    p.add_argument("--no-editor", action="store_true", help="don't open Notepad on launch")
    p.add_argument("--autostart", action="store_true", help="start the bot right away")
    p.add_argument("--background", action="store_true",
                   help="started at login / by the 3 AM task: no browser, no editor; the schedule decides")
    p.add_argument("--no-schedule", action="store_true", help="don't start/stop by the daily schedule")
    args = p.parse_args()
    url = f"http://localhost:{args.port}"

    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        if already_running(args.port):
            # Invotech 360 is already running (it starts at login): just show the dashboard
            if not args.background:
                open_dashboard(url)
            sys.exit(0)
        print(f"Port {args.port} is busy. Is something else using it? "
              f"Try: python app.py --port {args.port + 1}")
        sys.exit(1)

    hot = bot.start_listeners()
    print("=" * 56)
    print(f"  Invotech 360 dashboard:  {url}")
    print("  Kill switch: press Esc TWICE quickly.  F9 = pause/resume" if hot else
          "  (install pynput for the Esc-Esc kill switch)")
    print("  Use your mouse/keyboard any time - the bot pauses and waits for you")
    print("  Quit server: Ctrl+C")
    print("=" * 56, flush=True)

    cfg = load_settings()
    if cfg.schedule_enabled and not args.no_schedule:
        st = scheduler.status()
        print(f"  Schedule: every day from {cfg.schedule_start}, up to {cfg.daily_hours:g} hours "
              f"({st['used_text']} used today; next start: {st['next_start_text']})", flush=True)
    if not args.no_schedule:
        scheduler.run_forever()
    if args.background:
        args.no_editor = args.no_browser = True
    if not args.no_editor:
        threading.Thread(target=lambda: bot.open_editor(load_settings()), daemon=True).start()
    if not args.no_browser:
        threading.Timer(1.0, lambda: open_dashboard(url)).start()
    if args.autostart:
        from dataclasses import asdict
        threading.Timer(2.5, lambda: start_by_hand(asdict(load_settings()))).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        bot.stop()
        server.server_close()
        print("\nBye.")


if __name__ == "__main__":
    main()
