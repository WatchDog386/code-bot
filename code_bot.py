#!/usr/bin/env python3
"""
Terminal-only version (no dashboard). Same engine as app.py.

    python code_bot.py                       # opens Notepad, mouse + typing
    python code_bot.py --mode mouse          # only the mouse
    python code_bot.py --wpm 70 --minutes 60 --breaks
    python code_bot.py --file path/to/code.py

Stop: Ctrl+C, F10/Esc, or mouse into the top-left corner. F9 = pause/resume.
"""

import argparse
import sys
import time

try:
    from codebot.engine import Bot
    from codebot.snippets import LANGUAGES
except ImportError as exc:
    print(f"Missing dependency ({exc}). Run:\n    python -m pip install -r requirements.txt")
    sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="Move the mouse and type code nonstop.")
    p.add_argument("--mode", choices=["both", "mouse", "type"], default="both")
    p.add_argument("--wpm", type=int, default=55)
    p.add_argument("--languages", nargs="+", choices=LANGUAGES, default=LANGUAGES)
    p.add_argument("--file", default="", help="type this file instead of built-in snippets")
    p.add_argument("--typo-rate", type=float, default=0.02)
    p.add_argument("--mouse-min", type=float, default=2.0)
    p.add_argument("--mouse-max", type=float, default=6.0)
    p.add_argument("--minutes", type=float, default=0, help="auto-stop after N minutes")
    p.add_argument("--clear-after", type=int, default=150, help="wipe scratch file every N lines")
    p.add_argument("--breaks", action="store_true", help="take short random breaks")
    p.add_argument("--no-scroll", action="store_true")
    p.add_argument("--no-editor", action="store_true", help="don't open Notepad; type into the focused window")
    p.add_argument("--strip-indent", action="store_true", help="for editors that auto-indent (VS Code)")
    p.add_argument("--delay", type=float, default=3)
    a = p.parse_args()

    bot = Bot()
    try:
        from pynput import keyboard

        def on_press(key):
            if key == keyboard.Key.f9:
                bot.toggle_pause()
            elif key in (keyboard.Key.f10, keyboard.Key.esc):
                bot.stop()
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
    except Exception:  # noqa: BLE001
        pass

    bot.start({
        "mode": a.mode, "wpm": a.wpm, "languages": a.languages, "custom_file": a.file,
        "typo_rate": a.typo_rate, "mouse_min": a.mouse_min, "mouse_max": a.mouse_max,
        "minutes": a.minutes, "clear_after_lines": a.clear_after, "breaks": a.breaks,
        "scroll": not a.no_scroll, "auto_open_editor": not a.no_editor,
        "keep_focus": not a.no_editor, "strip_indent": a.strip_indent, "start_delay": a.delay,
    })
    try:
        while bot.running:
            time.sleep(0.3)
    except KeyboardInterrupt:
        bot.stop()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
