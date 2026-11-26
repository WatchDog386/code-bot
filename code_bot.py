#!/usr/bin/env python3
"""
Terminal-only version (no dashboard). Same engine as app.py.

    python code_bot.py                              # VS Code, never stops: new + library projects
    python code_bot.py --gen-languages go           # new projects, Go only
    python code_bot.py --editor notepad             # Notepad instead
    python code_bot.py --projects fleet-api  # only this library project
    python code_bot.py --monitor 2 --minutes 60 --breaks
    python code_bot.py --list-screens
    python code_bot.py --source file --file path/to/code.py

Kill switch: press Esc twice quickly (or Ctrl+C). F9 = pause/resume.
Touch the mouse/keyboard and it pauses; it carries on after 20s of you being idle.
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
    p = argparse.ArgumentParser(description="Invotech 360: write real code nonstop with human-like typing and mouse.")
    p.add_argument("--editor", choices=["vscode", "notepad", "focused"], default="vscode")
    p.add_argument("--source", choices=["projects", "spreadsheets", "mixed", "generated", "snippets", "file"], default=None,
                   help="projects = the library, forever (default); spreadsheets = Excel projects; "
                        "mixed = new + library; generated = only new projects")
    p.add_argument("--projects", nargs="+", choices=list_projects() or None, default=[],
                   help="which library projects to write (implies --source projects)")
    p.add_argument("--gen-languages", nargs="+", choices=["python", "go", "typescript"],
                   default=["python", "go", "typescript"], help="languages for new projects")
    p.add_argument("--workspace", default="~/dev-projects", help="VS Code workspace folder")
    p.add_argument("--file", default="", help="file to type with --source file")
    p.add_argument("--languages", nargs="+", choices=LANGUAGES, default=LANGUAGES)
    p.add_argument("--mode", choices=["both", "mouse", "type"], default="both")
    p.add_argument("--wpm", type=int, default=34)
    p.add_argument("--think", type=float, default=1.0, help="thinking-pause multiplier (0.5 - 3)")
    p.add_argument("--monitor", type=int, default=0,
                   help="screen number to use (1, 2, 3 ... ; 0 = auto). Run with --list-screens to see them")
    p.add_argument("--list-screens", action="store_true", help="show the screens and exit")
    p.add_argument("--no-detect", action="store_true", help="don't pause when you use the mouse/keyboard")
    p.add_argument("--resume-after", type=float, default=5, help="idle seconds before taking the keyboard back (0 = never)")
    p.add_argument("--keep-finished", action="store_true", help="keep finished projects in the workspace")
    p.add_argument("--typo-rate", type=float, default=0.015)
    p.add_argument("--mouse-min", type=float, default=4.0)
    p.add_argument("--mouse-max", type=float, default=14.0)
    p.add_argument("--minutes", type=float, default=0, help=argparse.SUPPRESS)
    p.add_argument("--breaks", action="store_true", help="take short random breaks")
    p.add_argument("--no-scroll", action="store_true")
    p.add_argument("--no-review", action="store_true", help="don't arrow up/down to re-read code")
    p.add_argument("--delay", type=float, default=3)
    a = p.parse_args()

    if a.list_screens:
        from codebot.engine import monitors_info
        for m in monitors_info():
            print(f"  {m['label']}   at ({m['x']}, {m['y']})")
        return

    bot = Bot()
    bot.start_listeners()

    bot.start({
        "editor": a.editor, "source": a.source or "projects",
        "projects": a.projects, "gen_languages": a.gen_languages,
        "workspace_dir": a.workspace, "custom_file": a.file, "languages": a.languages,
        "mode": a.mode, "wpm": a.wpm, "typo_rate": a.typo_rate,
        "mouse_min": a.mouse_min, "mouse_max": a.mouse_max, "minutes": a.minutes,
        "breaks": a.breaks, "scroll": not a.no_scroll, "review_moves": not a.no_review,
        "auto_open_editor": a.editor != "focused", "keep_focus": a.editor != "focused",
        "start_delay": a.delay, "think": a.think, "monitor": a.monitor - 1,
        "detect_user": not a.no_detect, "resume_after": a.resume_after,
        "keep_finished": a.keep_finished,
    })
    try:
        while bot.running:
            time.sleep(0.3)
    except KeyboardInterrupt:
        bot.stop()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
