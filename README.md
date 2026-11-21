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
- **Share the mouse.** Move the mouse whenever you like: the bot lets go of it at once but
  **keeps typing in VS Code with real keystrokes**, exactly as before (moving the mouse doesn't
  change which window gets the keys). About 1 second after you stop moving it, the bot takes
  the mouse back ("Take the mouse back after I stop" in Settings). Clicking inside VS Code is
  fine too: the bot puts its cursor back at the end of the file and carries on.
- **Your keyboard / other windows.** If you start typing, or click into another window, the bot
  stops sending keystrokes before the next key (they would land in your window) and keeps
  writing the file on disk character by character instead; VS Code shows it growing. After you
  have been idle for 5 seconds ("Take the keyboard back after I'm idle") it brings VS Code back
  and carries on typing for real from the same spot. **Resume** gives it back at once.
  Don't type in the file the bot is writing while it works in the background.
  (Turn this off with "Keep writing code while I work". Notepad mode pauses instead.)
- `Ctrl+C` in the terminal quits the server.

## Terminal

When a project is finished the bot works in the terminal like a developer:

- **Bot has the keyboard:** it opens a new VS Code terminal (`Terminal: Create New Terminal`),
  `cd`s into the project and types each command: install, tests, build. Then it **starts the
  app** and opens it in **VS Code's built-in browser** (`Simple Browser`), leaves it running for
  a while (45 s, "Keep a started app running for"), and stops it with `Ctrl+C`.
- **You have the keyboard (or not VS Code):** the same steps run in the background; the output,
  exit codes and whether the app answered show in the dashboard's **Terminal** tab.

The steps come from a `.codebot-run` file in the project:

```
python -m venv .venv
{venv}python -m pip install -q -r requirements.txt   # wait 60
{venv}python -m pytest -q
serve: {venv}python -m uvicorn main:app --port 8000
open: http://127.0.0.1:8000/docs
```

`serve:` = the app itself (left running, then stopped), `open:` = the page shown in VS Code,
`# wait N` = seconds to give a command in VS Code's terminal (the bot can't read that terminal),
`{venv}` = the project's virtualenv (`.venv\Scripts\` on Windows, `.venv/bin/` elsewhere).
Without the file, Go projects get `go build ./...` and Python projects `python -m compileall -q .`.
The samples: task-tracker-api installs, tests and runs its API (docs page), link-shortener vets,
tests and runs its server, inventory-dashboard installs and type-checks.
Turn it off under Settings > Screen & workspace.

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

## Projects: a new one every time

By default the bot **comes up with a new project for every run** ("New project every time" in
Settings > What to write, or `new project` in the agent box). It picks one of 14 kinds of
business app (library, clinic, hotel, fleet, school, warehouse, restaurant, gym, events, real
estate, help desk, payroll, farm, shipping) and one of 3 languages:

| Language | What it writes (each typed file is over 1000 lines) | Terminal afterwards |
|---|---|---|
| Python | models, repository, services, HTTP API, unittest suite (standard library only) | compile, run the tests, start the API and open it in VS Code |
| Go | model, store, service, `net/http` API, tests | `go vet`, `go test`, `go run`, open it in VS Code |
| TypeScript | models, store, services, query layer, self-test (strict, no dependencies) | `npm install`, `tsc`, run the self-test |

Records are added to the project until every file it types is over 1000 lines (typically
1000-2600). The code is real and works: every combination is checked to compile and pass its
own tests. Small files a project needs (go.mod, package.json, README, `__init__.py`) are put in
place instantly instead of being typed. Pick the languages under Settings > What to write.

The **Projects** page also has a library of 9 ready projects (6 of them generated this way). To
add more generated ones to the library:

```bash
python -m codebot.gen --out projects --count 6
```

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
