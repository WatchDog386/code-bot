# code-bot

Writes real projects in VS Code nonstop, file by file, with human-like typing and mouse
movement. You control it from a dashboard at **http://localhost:8765**.

## First-time setup

1. Install **Python 3.9+** (Windows: tick "Add Python to PATH") and **VS Code**.
2. In this folder, open the VS Code terminal (`` Ctrl+` ``) and run:

```bash
python -m pip install -r requirements.txt
```

- macOS: allow VS Code/Terminal in **System Settings > Privacy & Security > Accessibility** and
  **Input Monitoring**. In VS Code run **"Shell Command: Install 'code' command in PATH"**.
- Linux: X11 only; `sudo apt install python3-tk xdotool`.

## Run

```bash
python app.py
```

This opens a **new VS Code window** on the workspace folder `~/dev-projects` and the dashboard
in your browser. Press **Start**.

**First run only:** VS Code may ask "Do you trust the authors of the files in this folder?".
Click **Yes, I trust the authors** (tick "trust parent folder") so it never asks again.

Other commands:

| Command | What it does |
|---|---|
| `python app.py --autostart` | open everything and start immediately |
| `python code_bot.py` | terminal only, no dashboard |
| `python code_bot.py --projects task-tracker-api --wpm 70` | one project, faster |
| `python code_bot.py --editor notepad` | Notepad instead of VS Code |
| `python code_bot.py --minutes 120 --breaks` | 2 hours, with short random breaks |

Or press **F5** in VS Code and pick a "code-bot" launch config.

## Stop

**Stop** in the dashboard, **F10** or **Esc**. **F9** pauses/resumes.
Emergency: shove the mouse into any **corner** of the screen. `Ctrl+C` quits the server.

## How it works

- **Real projects**: `projects/` holds complete projects (Python FastAPI service, React +
  TypeScript dashboard, Go URL shortener). The bot creates each file in the workspace, opens it
  as a VS Code tab and types it top to bottom. The explorer tree fills up like a real project,
  files autosave, then it moves on to the next project, forever.
- **Clean code**: the workspace gets a `.vscode/settings.json` that turns off auto-closing
  brackets/quotes, auto-indent, IntelliSense, Copilot and format-on-save, so what gets typed is
  exactly the source. After each file the bot checks that the saved file matches the source
  ("files verified clean" in the dashboard).
- **Human typing**: word-by-word rhythm, slower on symbols and capitals, thinking pauses before
  functions and classes, typos fixed with backspace, occasional back-up-and-retype, arrowing up to
  re-read code, Ctrl+S now and then, speed drifting over time.
- **Human mouse**: curved paths, slow-fast-slow speed, slight tremor, overshoot and
  correction, small resting drifts, "reading" moves over the code, glances at the file explorer,
  scrolling. It never clicks.
- **Your own projects**: drop any folder into `projects/`. Add a `.codebot-order` file listing
  files in order if you want, otherwise configs/docs go first, then source, then tests.
  Only plain-ASCII text files are typed.
- **Safe**: the bot only deletes project folders it created itself (marked with `.codebot`),
  and won't overwrite a `.vscode/settings.json` it didn't write. The server listens on
  127.0.0.1 only.
