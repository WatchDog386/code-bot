# Invotech 360

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

## Short files, many of them

Every code file the bot types is **at most 100 lines** (most are 40-100), so it finishes many
files instead of spending hours on one. Each library project has about 90-100 such files and
still works as a whole (its tests pass). New generated projects are split the same way.

## Data entry with pauses

In spreadsheets the bot pauses before every cell as if reading the next value (about 0.6-1.8 s,
now and then a longer look), and between rows, then keys the value in. The "Thinking pauses"
slider in Settings makes all of these longer or shorter.

## Programming and spreadsheets, nonstop

**Projects** page:
- **Both, nonstop** (default) - a code project from the library typed in VS Code, then a spreadsheet
  typed in **WPS Office** (Excel if WPS isn't installed), round and round, forever.
- **Programming (VS Code)** - only the code library. **Spreadsheet (WPS Office)** - only spreadsheets.
- **Upload Excel / CSV** - your own workbooks; the bot types them into WPS cell by cell (values and
  formulas), then ready-made ones (budget, sales, inventory, payroll, results, expenses, tracker).
  Finished workbooks can be **downloaded** from the same page (kept in memory, not on disk).

Nothing piles up on your PC: each finished project's folder is removed (tick "Keep finished
projects" to keep them), and there is no log file.

## Keeping VS Code clean and the right size

- At the start of every project the bot resets the zoom to 100 % and closes the side bars and
  the bottom panel, so you only see the code. The explorer no longer expands folders by itself,
  and Ctrl + mouse wheel can't change the font size.
- It never types into another window: before every key it checks that VS Code is the window in
  front, and that no Ctrl / Alt / Windows key is held down (which would turn letters into
  shortcuts like zoom out). If either isn't so, it stops typing at once and keeps writing the
  file in the background until VS Code is back.

## Install: desktop icon, start at sign-in, every day at 3 AM

Run this once (Windows: just double-click **install_windows.bat**):

```bash
python install.py
```

- **Windows**: puts an **Invotech 360** icon on your desktop, starts it quietly in the
  background every time you sign in, and adds a Task Scheduler task that starts it every day at
  03:00 and wakes the PC from sleep for it. It also starts it right away.
- **macOS**: a LaunchAgent (at login and every day at 03:00) and a launcher on the desktop.
- **Linux**: an autostart entry, a desktop launcher and a cron entry at 03:00.

**Install it as an app and pin it:** open the dashboard and click **Install app** (top bar,
green). Edge/Chrome install Invotech 360 with its own icon and window; Edge's dialog has a
*Pin to taskbar* option. (If you don't see the button: in Edge, *... > Apps > Install this site
as an app*; in Chrome, the install icon at the right of the address bar.)

**Or pin the shortcut** (Windows doesn't let programs pin themselves): open Start, type
*Invotech 360*, right-click it and choose **Pin to taskbar**. (Or right-click the desktop icon >
*Show more options* > *Pin to taskbar*.) Clicking it opens the dashboard in its own window with
the Invotech 360 icon, like an app, not as a browser tab. In Edge you can also use
*... > Apps > Install this site as an app* on the dashboard, then pin that.

`python install.py --uninstall` removes all of it.

**10 hours a day.** By default it starts at **03:00** and works until **13:00**. The 10 hours are
a hard daily limit: they also count runs you start yourself, and once they're used up it won't
start again until the next day's 03:00. If you press Stop (or Esc Esc), it stays off until the
next day. Change the time and the hours under **Settings > Schedule**; it shows today's hours
used and left, and when it starts next. The hours used are kept in `usage.json`.

The computer must be **on (or asleep), signed in and unlocked** at 03:00: mouse and keyboard
control can't work on a locked screen or the sign-in screen. Set Windows to not lock the screen
(Settings > Accounts > Sign-in options) if it should work through the night. Logs are written
to `logs/invotech360.log`.

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
| `python code_bot.py --projects fleet-api --wpm 70` | one library project, faster |
| `python code_bot.py --editor notepad` | Notepad instead of VS Code |
| `python code_bot.py --minutes 120 --breaks` | 2 hours, with short random breaks |
| `python code_bot.py --think 1.5` | even longer thinking pauses (slower, more human) |

Or press **F5** in VS Code and pick an "Invotech 360" launch config.

## The dashboard

Laid out like the Optimas MS desktop app (navy side rail, white top bar, KPI cards, hairline panels,
light/dark), with a coding workspace in the style of Cursor / Windsurf:

- **Workspace** - an IDE view. The explorer shows the project being written (files tick off as they are
  done), the editor shows the code live as it is typed, with syntax highlighting and a cursor,
  and the Task panel lists each step (planned, created, thinking, verified...). There is also an
  Output / Problems / Session panel and a VS Code-style status bar. Click any file to open it in a
  tab.
- **Commands** - type in the command box, e.g. `new project in go`, `write fleet-api at 60 wpm`, `typing only`,
  `pause`, `stop`, `status` or `help`.
- **Command palette** - `Ctrl+K` (or `Ctrl+Shift+P`) runs any action or opens any file.
- **Overview** - KPI cards and the current run. **Projects** - choose and preview projects.
  **Activity** - full timeline and raw log. **Settings** - every option.
- Shortcuts: `Ctrl+Enter` start, `Ctrl+.` stop, `Ctrl+L` command box, `Ctrl+J` bottom panel,
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

## What the mouse does

The cursor works the way a developer's hand does, and every move fits what is happening:

| While the bot is... | the mouse... |
|---|---|
| typing | rests near the line being written, glances at the file in the explorer |
| thinking | follows the code up the screen, hovers names to see their pop-up, clicks to put the caret where the next line goes |
| finishing a file | scrolls back up through it, reads it, scrolls back down |
| opening the terminal | goes up to the menu bar, clicks **Terminal**, then **New Terminal**, then clicks into the terminal |
| running commands | watches the output in the terminal panel |
| running the app | looks at the app's page, opened next to the code, and scrolls through it |

The menu bar is found on screen (from a screenshot of VS Code's title bar), so it works with
any theme, screen size or scaling. If the menu can't be found for certain, or didn't open, the
bot uses the command palette instead, so a missed click never does anything unexpected; after
any click it puts the cursor back at the end of the code before typing again. It only clicks
or scrolls when VS Code is the window in front, never in yours. (On macOS the menus live in
the system menu bar, so there it uses the command palette.)

## Terminal

Off by default (the bot only types code in the editor). Turn on "After writing a project, run it in
VS Code's terminal" under Settings > Screen & workspace to get this:

- **Bot has the keyboard:** it opens a new VS Code terminal (`Terminal: Create New Terminal`),
  `cd`s into the project and types each command: install, tests, build. Then it **starts the
  app** and opens it in **VS Code's built-in browser** (`Simple Browser`) **beside the code**,
  so code is on the left and the running app on the right. It leaves it running for
  a while (45 s, "Keep a started app running for"), and stops it with `Ctrl+C`.
- **You have the keyboard (or not VS Code):** the same steps run in the background; the output,
  exit codes and whether the app answered show in the dashboard's **Terminal** tab.

New projects bring their own steps (see below). For a project you add to `projects/`, list
them in a `.codebot-run` file, one per line, for example:

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

## It never stops

Once started, Invotech 360 keeps going until **you** stop it (Esc Esc, Stop, or the optional
time limit). By default ("Loop forever" in Settings > What to write) it writes a brand-new
project, then the next project from the library, then another new one, round and round.
When a project is finished it moves straight on to the next one; if anything goes wrong (a
file can't be written, a command fails, VS Code is slow to open) it notes it in the
Activity log and carries on a few seconds later. Your cursor resting in a screen corner no
longer stops it either.

## Projects: a new one every time

The bot **comes up with a new project for every run** ("New project every time" in
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

The **Projects** page also has a library of 6 ready projects made this way (clinic-service,
school-service, fleet-api, warehouse-api, restaurant-kit, events-kit). To
add more generated ones to the library:

```bash
python -m codebot.gen --out projects --count 6
```

## How it works

- **Real projects**: a new project every run (or one from `projects/`). The bot creates each
  file in the workspace, opens it
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
  scrolling, and clicks with a purpose (see "What the mouse does").
- **Your own projects**: drop any folder into `projects/`. Add a `.codebot-order` file listing
  files in order if you want, otherwise configs/docs go first, then source, then tests.
  Only plain-ASCII text files are typed.
- **Safe**: the bot only deletes project folders it created itself (marked with `.codebot`),
  and won't overwrite a `.vscode/settings.json` it didn't write. The server listens on
  127.0.0.1 only.
