# code-bot

Moves the mouse and types code nonstop. Opens Notepad by itself and is controlled from a
dashboard at **http://localhost:8765**.

## First-time setup

1. Install Python 3.9+ from python.org (Windows: tick **"Add Python to PATH"**).
2. Open this folder in VS Code, open the terminal (`` Ctrl+` ``) and run:

```bash
python -m pip install -r requirements.txt
```

macOS: allow VS Code (or Terminal) under **System Settings → Privacy & Security → Accessibility** and **Input Monitoring**.
Linux: X11 only; you may need `sudo apt install python3-tk xdotool`.

## Run it

From the VS Code terminal:

```bash
python app.py
```

That will:
1. open Notepad with its own scratch file (it never types into your real notes),
2. open the dashboard at http://localhost:8765 in your browser,
3. wait for you to press **Start**.

Other ways:

| Command | What it does |
|---|---|
| `python app.py --autostart` | open Notepad + dashboard and start immediately |
| `python app.py --port 9000` | use another port |
| `python app.py --no-browser` | don't open the browser (go to the URL yourself) |
| `python code_bot.py` | terminal only, no dashboard |
| `python code_bot.py --mode mouse --minutes 60` | mouse only for an hour |
| `python code_bot.py --file C:\path\main.py --wpm 70` | type your own file |

In VS Code you can also press **F5** and choose a "code-bot" launch config.

## Stopping

- **Stop** button in the dashboard, or **F10** / **Esc**
- **F9** pauses and resumes
- emergency: shove the mouse into the **top-left corner** of the screen
- `Ctrl+C` in the terminal shuts down the server

## Features

- Dashboard: Start / Pause / Stop, live stats (uptime, characters, lines, mouse moves, typos), log
- Opens Notepad by itself (TextEdit on macOS, gedit/mousepad on Linux) and keeps it in front,
  so typing never lands in the wrong window
- Human-like typing: speed you set, random rhythm, "thinking" pauses, realistic typos that get corrected
- Natural mouse: short drifts plus occasional long moves, eased curves, random scrolling
- Code in Python, JavaScript, TypeScript, SQL, Go and Java, or your own file
- Clears the scratch file every N lines so it never grows forever
- Optional random 20–90 s breaks, auto-stop timer
- Settings remembered in `settings.json`
- The server only listens on 127.0.0.1 and rejects requests from other websites
