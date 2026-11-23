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

This opens **only the dashboard** in your browser. Nothing else happens yet.

1. Tick the project you want written.
2. Press **Start**.
3. VS Code opens on `~/dev-projects` with just the **file explorer** on the left and the code
   editor (no terminal, no chat panel). The bot creates the project's files one by one in the
   explorer, opens each one and types it, until the whole project is written. Then it stops.
   (Tick "Keep going when finished" to have it carry on with more projects.)

**First run only:** VS Code may ask "Do you trust the authors of the files in this folder?".
Click **Yes, I trust the authors** (tick "trust parent folder") so it never asks again.

Other commands:

| Command | What it does |
|---|---|
| `python app.py --autostart` | open everything and start immediately |
| `python app.py --open-editor` | open VS Code right away instead of waiting for Start |
| `python code_bot.py --repeat` | keep writing projects forever instead of stopping |
| `python code_bot.py` | terminal only, no dashboard |
| `python code_bot.py --projects task-tracker-api --wpm 70` | one project, faster |
| `python code_bot.py --editor notepad` | Notepad instead of VS Code |
| `python code_bot.py --minutes 120 --breaks` | 2 hours, with short random breaks |
| `python code_bot.py --think 1.5` | even longer thinking pauses (slower, more human) |

Or press **F5** in VS Code and pick a "code-bot" launch config.

## Stop / take over

- **Kill switch: press `Esc` twice quickly** (anywhere). Or **Stop** in the dashboard.
- **F9** pauses / resumes.
- **Just use your mouse or keyboard.** The bot notices at once, lets go of the mouse and stops
  typing. When you've left everything alone for 20 seconds (configurable) it brings VS Code
  back, puts the cursor at the end of the file and carries on exactly where it stopped.
- `Ctrl+C` in the terminal quits the server.

## Multiple monitors

Pick the screen in the dashboard ("Screen for the bot"), or from the terminal:

```bash
python code_bot.py --list-screens
```
```bash
python code_bot.py --monitor 3
```

Screens are numbered left to right. VS Code is moved to that screen and maximized there, and
the bot's mouse never leaves it. "Auto" picks a side screen (not your main one).

## How it works

- **Real projects**: `projects/` holds complete projects (Python FastAPI service, React +
  TypeScript dashboard, Go URL shortener). The bot creates each file in the workspace, opens it
  as a VS Code tab and types it top to bottom. The explorer tree fills up like a real project,
  files autosave, then it moves on to the next project, forever.
- **Clean code**: the workspace gets a `.vscode/settings.json` that turns off auto-closing
  brackets/quotes, auto-indent, Copilot and format-on-save, so what gets typed is exactly the source.
- **Autocomplete for show**: suggestion popups appear while it types, like a real editor, but
  they are never accepted (Enter, Tab and characters like `(` or `.` can't accept them).
- **Only the editor**: the terminal panel, chat side bar, welcome pages and tips are hidden.
  Keyboard focus always goes back to the code editor, so nothing is ever typed into a terminal.
- **Mouse stays in VS Code**: the mouse only moves inside the VS Code window (code area and
  file explorer), never anywhere else on the screen. After each file the bot checks that the saved file matches the source
  ("files verified clean" in the dashboard).
- **Clean workspace**: the workspace only ever holds the project being written. When a new
  project starts, the previous one is deleted (tick "Keep finished projects" to keep them).
  Folders you put there yourself are never touched, and `.vscode` is hidden from the explorer.
- **Human pace**: about 34 WPM raw, plus thinking pauses before functions, between lines,
  between files (6-20 s) and projects (25-60 s), and occasional 5-14 s "stop and think"
  moments. The "Thinking pauses" slider scales all of them.
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
