# code-bot

Moves the mouse around the screen and types code nonstop into whatever window has focus.

## Setup (one time)

You need Python 3.9+ (Windows users: check "Add Python to PATH" when installing).

```bash
pip install -r requirements.txt
```

Linux only: you may also need `sudo apt install python3-tk python3-dev` (X11; Wayland is not supported by pyautogui).
macOS only: allow your Terminal in **System Settings → Privacy & Security → Accessibility** (and Input Monitoring for the Esc key).

## Run

1. Open your editor with an **empty** file.
2. Start the bot:
   - Windows: double-click `run_windows.bat`
   - macOS/Linux: `./run_mac_linux.sh`
   - or: `python code_bot.py`
3. You get 5 seconds to click into the editor. Then it starts.

## Stop

- Press **Esc**, or
- press **Ctrl+C** in the terminal, or
- shove the mouse into the **top-left corner** of the screen.

## Options

| Flag | What it does |
|---|---|
| `--mouse-only` | only move the mouse |
| `--type-only` | only type |
| `--wpm 70` | typing speed (default 55) |
| `--clear` | wipe the file after each snippet so it never grows |
| `--keep-indent` | type the leading spaces (for Notepad / plain editors). Leave off for VS Code etc. which auto-indent |
| `--file path.py` | type your own code file instead of the built-in snippets |
| `--mouse-min 2 --mouse-max 6` | seconds between mouse moves |
| `--delay 10` | countdown before starting |
| `--minutes 60` | stop automatically after N minutes |

Tip: in VS Code, auto-closing brackets and quotes can leave extra `)` or `}` behind. For the cleanest output use a plain editor (Notepad, TextEdit in plain-text mode, gedit) with `--keep-indent`, or turn off `editor.autoClosingBrackets` and `editor.autoClosingQuotes`.
