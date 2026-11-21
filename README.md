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
| `python code_bot.py --think 1.5` | even longer thinking pauses (slower, more human) |

Or press **F5** in VS Code and pick a "code-bot" launch config.

## The dashboard

Laid out like the Optimas MS desktop app (navy side rail, white top bar, KPI cards, hairline panels,
light/dark), with a coding-agent workspace in the style of Cursor / Windsurf:

- **Agent** - an IDE view. The explorer shows the project being written (files tick off as they are
  done), the editor shows the code live as it is typed, with syntax highlighting and a cursor,
  and the agent panel lists each step (planned, created, thinking, verified...). There is also an
  Output / Problems / Session panel and a VS Code-style status bar. Click any file to open it in a
  tab.
- **Ask the agent** - type in the agent box, e.g. `write link-shortener at 60 wpm`, `typing only`,
  `pause`, `stop`, `status` or `help`.
- **Command palette** - `Ctrl+K` (or `Ctrl+Shift+P`) runs any action or opens any file.
- **Overview** - KPI cards and the current run. **Projects** - choose and preview projects.
  **Activity** - full timeline and raw log. **Settings** - every option.
- Shortcuts: `Ctrl+Enter` start, `Ctrl+.` stop, `Ctrl+L` ask the agent, `Ctrl+J` bottom panel,
  `Ctrl+B` explorer.

## Stop / take over

- **Kill switch: press `Esc` twice quickly** (anywhere). Or **Stop** in the dashboard.
- **F9** pauses / resumes.
- **Just use your computer.** The moment you touch the mouse or keyboard the bot lets go of
  both: the mouse stops moving and no more keystrokes are sent, so nothing lands in the window
  you're working in. **The code keeps being written anyway**: the bot writes it straight into the
  file on disk, word by word at the same pace, and VS Code shows the file growing. New files
  appear in VS Code's explorer. When you've left the mouse and keyboard alone for 20 seconds
  (configurable) it brings VS Code back, opens the file it's on, puts the cursor at the end
  and carries on typing for real. Pressing **Resume** gives it the keyboard back straight away.
  Don't type in the file the bot is writing while it works in the background.
  (Turn this off with "Keep writing code while I work". Notepad mode always pauses instead.)
- `Ctrl+C` in the terminal quits the server.

## Terminal

When a project is finished the bot runs its commands, like a developer checking their work:

- **Bot has the keyboard:** it opens VS Code's own terminal (`Terminal: Focus Terminal`), `cd`s
  into the project and types each command.
- **You're busy (or not VS Code):** the commands run in the background, and the output shows up in
  the dashboard's **Terminal** tab with the exit code.

Commands come from a `.codebot-run` file in the project (one per line, `#` for comments).
Without one, Go projects get `go build ./...` and Python projects get `python -m compileall -q .`.
The sample projects run their tests. Turn this off under Settings > Screen & workspace.

## Live preview

The monitor button above the editor in the dashboard (or `preview` in the agent box) opens a
**Preview** tab with a live picture of the bot's screen (VS Code, its terminal), updated every
second. On macOS allow **Screen Recording** for your terminal / Python in System Settings >
Privacy & Security.

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
  brackets/quotes, auto-indent, IntelliSense, Copilot and format-on-save, so what gets typed is
  exactly the source. After each file the bot checks that the saved file matches the source
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
