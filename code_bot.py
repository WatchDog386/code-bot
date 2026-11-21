#!/usr/bin/env python3
"""
Terminal-only version (no dashboard). Same engine as app.py.

    python code_bot.py                              # VS Code, writes projects nonstop
    python code_bot.py --editor notepad             # Notepad instead
    python code_bot.py --projects task-tracker-api  # only this project
    python code_bot.py --wpm 70 --minutes 60 --breaks
    python code_bot.py --source file --file path/to/code.py

Stop: Ctrl+C, F10/Esc, or mouse into a screen corner. F9 = pause/resume.
"""

import argparse
import sys
import time

try:
    from codebot.engine import Bot
    from codebot.projects import list_projects
    from codebot.snippets import LANGUAGES
except ImportError as exc:
    print(f"Missing dependency ({exc}). Run:\n    python -m pip install -r requirements.txt")
    sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="Write real code nonstop with human-like typing and mouse.")
    p.add_argument("--editor", choices=["vscode", "notepad", "focused"], default="vscode")
    p.add_argument("--source", choices=["projects", "snippets", "file"], default="projects")
    p.add_argument("--projects", nargs="+", choices=list_projects() or None, default=[],
                   help="which projects to write (default: all)")
    p.add_argument("--workspace", default="~/dev-projects", help="VS Code workspace folder")
    p.add_argument("--file", default="", help="file to type with --source file")
    p.add_argument("--languages", nargs="+", choices=LANGUAGES, default=LANGUAGES)
    p.add_argument("--mode", choices=["both", "mouse", "type"], default="both")
    p.add_argument("--wpm", type=int, default=55)
    p.add_argument("--typo-rate", type=float, default=0.015)
    p.add_argument("--mouse-min", type=float, default=3.0)
    p.add_argument("--mouse-max", type=float, default=10.0)
    p.add_argument("--minutes", type=float, default=0, help="auto-stop after N minutes")
    p.add_argument("--breaks", action="store_true", help="take short random breaks")
    p.add_argument("--no-scroll", action="store_true")
    p.add_argument("--no-review", action="store_true", help="don't arrow up/down to re-read code")
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
        "editor": a.editor, "source": a.source, "projects": a.projects,
        "workspace_dir": a.workspace, "custom_file": a.file, "languages": a.languages,
        "mode": a.mode, "wpm": a.wpm, "typo_rate": a.typo_rate,
        "mouse_min": a.mouse_min, "mouse_max": a.mouse_max, "minutes": a.minutes,
        "breaks": a.breaks, "scroll": not a.no_scroll, "review_moves": not a.no_review,
        "auto_open_editor": a.editor != "focused", "keep_focus": a.editor != "focused",
        "start_delay": a.delay,
    })
    try:
        while bot.running:
            time.sleep(0.3)
    except KeyboardInterrupt:
        bot.stop()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
