#!/usr/bin/env python3
"""
code-bot control panel, served at http://localhost:8765

    python app.py                  # opens Notepad + the dashboard in your browser
    python app.py --autostart      # also starts the bot immediately
    python app.py --port 9000 --no-browser --no-editor

Hotkeys (anywhere): F9 = pause/resume, F10 or Esc = stop.
Emergency stop: shove the mouse into the top-left corner of the screen.
"""

import argparse
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from codebot.engine import Bot, Config
    from codebot.snippets import LANGUAGES
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
        if self.path in ("/", "/index.html"):
            with open(INDEX, "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if self.path == "/api/status":
            return self._send(200, bot.status())
        if self.path == "/api/settings":
            from dataclasses import asdict
            return self._send(200, {"config": asdict(load_settings()), "languages": LANGUAGES})
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
            "/api/open-editor": lambda: (bot.editor.open(), "opened"),
            "/api/settings": lambda: (save_settings(body), (True, "saved"))[1],
        }
        fn = routes.get(self.path)
        if not fn:
            return self._send(404, {"error": "not found"})
        ok, msg = fn()
        self._send(200, {"ok": bool(ok), "message": msg, "status": bot.status()})


def start_hotkeys():
    try:
        from pynput import keyboard
    except ImportError:
        return False

    def on_press(key):
        if key == keyboard.Key.f9:
            bot.toggle_pause()
        elif key in (keyboard.Key.f10, keyboard.Key.esc):
            if bot.running:
                bot.stop()

    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        return True
    except Exception:  # noqa: BLE001
        return False


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
    hot = start_hotkeys()
    print("=" * 56)
    print(f"  code-bot dashboard:  {url}")
    print("  Hotkeys: F9 pause/resume, F10/Esc stop" if hot else
          "  (install pynput for F9/F10 hotkeys)")
    print("  Emergency stop: mouse to the TOP-LEFT corner")
    print("  Quit server: Ctrl+C")
    print("=" * 56, flush=True)

    if not args.no_editor:
        threading.Thread(target=bot.editor.open, daemon=True).start()
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
