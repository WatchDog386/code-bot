#!/usr/bin/env python3
"""
code-bot control panel, served at http://localhost:8765

    python app.py                  # opens VS Code on your chosen screen + the dashboard
    python app.py --autostart      # also starts the bot immediately
    python app.py --port 9000 --no-browser --no-editor

Kill switch (anywhere): press Esc twice quickly. F9 = pause/resume.
Emergency stop: shove the mouse into a corner of the screen.
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

bot = Bot()


def load_settings():
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            return Config.from_dict(json.load(fh))
    except (OSError, ValueError):
        return Config()


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
            return self._send(200, bot.status())
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
            "/api/start": lambda: (save_settings(body), bot.start(body))[1],
            "/api/stop": bot.stop,
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
        self._send(200, {"ok": bool(ok), "message": msg, "status": bot.status()})


def main():
    p = argparse.ArgumentParser(description="code-bot control panel")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true", help="don't open the dashboard")
    p.add_argument("--no-editor", action="store_true", help="don't open Notepad on launch")
    p.add_argument("--autostart", action="store_true", help="start the bot right away")
    args = p.parse_args()

    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        print(f"Port {args.port} is busy. Is code-bot already running? "
              f"Try: python app.py --port {args.port + 1}")
        sys.exit(1)

    url = f"http://localhost:{args.port}"
    hot = bot.start_listeners()
    print("=" * 56)
    print(f"  code-bot dashboard:  {url}")
    print("  Kill switch: press Esc TWICE quickly.  F9 = pause/resume" if hot else
          "  (install pynput for the Esc-Esc kill switch)")
    print("  Use your mouse/keyboard any time - the bot pauses and waits for you")
    print("  Quit server: Ctrl+C")
    print("=" * 56, flush=True)

    if not args.no_editor:
        threading.Thread(target=lambda: bot.open_editor(load_settings()), daemon=True).start()
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    if args.autostart:
        from dataclasses import asdict
        threading.Timer(2.5, lambda: bot.start(asdict(load_settings()))).start()

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
