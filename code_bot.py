#!/usr/bin/env python3
"""
code-bot: moves the mouse around the screen and types code nonstop
into whatever window is focused (open an empty file in your editor first).

STOP IT:
  * press Ctrl+C in the terminal that is running it, OR
  * slam the mouse into the TOP-LEFT corner of the screen (failsafe), OR
  * press the Esc key (if the optional "pynput" package is installed).

Usage:
  python code_bot.py                 # mouse + typing (default)
  python code_bot.py --mouse-only    # only move the mouse
  python code_bot.py --type-only     # only type code
  python code_bot.py --wpm 60 --delay 8 --clear
  python code_bot.py --file my_code.py   # type your own file instead
"""

import argparse
import random
import sys
import threading
import time

try:
    import pyautogui
except ImportError:
    print("Missing dependency. Install it with:\n    pip install pyautogui")
    sys.exit(1)

pyautogui.FAILSAFE = True   # mouse to top-left corner = abort
pyautogui.PAUSE = 0         # we control timing ourselves

STOP = threading.Event()

# --------------------------------------------------------------------------
# Built-in code snippets that get typed out (loops forever, random order)
# --------------------------------------------------------------------------
SNIPPETS = [
'''def fibonacci(n):
    """Return the first n Fibonacci numbers."""
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]


print(fibonacci(15))
''',
'''class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, name, qty=1):
        self.items[name] = self.items.get(name, 0) + qty

    def remove(self, name, qty=1):
        if self.items.get(name, 0) < qty:
            raise ValueError(f"not enough {name}")
        self.items[name] -= qty

    def total(self):
        return sum(self.items.values())
''',
'''import json
from pathlib import Path


def load_config(path="config.json"):
    file = Path(path)
    if not file.exists():
        return {"debug": False, "retries": 3}
    with file.open() as fh:
        return json.load(fh)


def save_config(cfg, path="config.json"):
    Path(path).write_text(json.dumps(cfg, indent=2))
''',
'''def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
''',
'''async function fetchUsers(page = 1) {
  const res = await fetch(`/api/users?page=${page}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  const data = await res.json();
  return data.users.map((u) => ({ id: u.id, name: u.name }));
}
''',
'''def merge_sort(items):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    return out + left[i:] + right[j:]
''',
'''SELECT u.id, u.name, COUNT(o.id) AS orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2025-01-01'
GROUP BY u.id, u.name
ORDER BY orders DESC
LIMIT 20;
''',
]


def sleep(seconds):
    """Sleep that wakes up immediately when STOP is set."""
    STOP.wait(seconds)


# --------------------------------------------------------------------------
# Mouse movement
# --------------------------------------------------------------------------
def mouse_loop(lock, min_pause, max_pause):
    w, h = pyautogui.size()
    margin = 60  # keep away from edges / the failsafe corner
    tweens = [pyautogui.easeInOutQuad, pyautogui.easeOutQuad,
              pyautogui.easeInOutSine, pyautogui.linear]
    while not STOP.is_set():
        x = random.randint(margin, w - margin)
        y = random.randint(margin, h - margin)
        with lock:
            try:
                pyautogui.moveTo(x, y, duration=random.uniform(0.4, 1.6),
                                 tween=random.choice(tweens))
            except pyautogui.FailSafeException:
                STOP.set()
                break
        sleep(random.uniform(min_pause, max_pause))


# --------------------------------------------------------------------------
# Typing
# --------------------------------------------------------------------------
def type_line(line, char_delay):
    for ch in line:
        if STOP.is_set():
            return
        pyautogui.write(ch)
        # human-ish rhythm: small jitter, occasional longer "thinking" pause
        d = char_delay * random.uniform(0.5, 1.6)
        if ch in " (.:" and random.random() < 0.08:
            d += random.uniform(0.2, 0.7)
        time.sleep(d)


def type_loop(lock, snippets, wpm, clear, keep_indent, snippet_pause):
    char_delay = 60.0 / (wpm * 5)   # 5 chars per "word"
    while not STOP.is_set():
        snippet = random.choice(snippets)
        for line in snippet.splitlines():
            if STOP.is_set():
                return
            text = line if keep_indent else line.lstrip()
            with lock:
                try:
                    type_line(text, char_delay)
                    pyautogui.press("enter")
                    if not keep_indent:
                        # editors auto-indent; jump to line start so the
                        # next line's indentation stays sane
                        pyautogui.press("home")
                except pyautogui.FailSafeException:
                    STOP.set()
                    return
            sleep(random.uniform(0.1, 0.6))   # lets the mouse move between lines
        sleep(snippet_pause)
        if clear and not STOP.is_set():
            mod = "command" if sys.platform == "darwin" else "ctrl"
            with lock:
                pyautogui.hotkey(mod, "a")
                pyautogui.press("backspace")
        elif not STOP.is_set():
            pyautogui.press("enter")


def start_esc_listener():
    try:
        from pynput import keyboard
    except ImportError:
        return None

    def on_press(key):
        if key == keyboard.Key.esc:
            STOP.set()
            return False

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener


def main():
    p = argparse.ArgumentParser(description="Move the mouse and type code nonstop.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--mouse-only", action="store_true", help="only move the mouse")
    g.add_argument("--type-only", action="store_true", help="only type code")
    p.add_argument("--wpm", type=int, default=55, help="typing speed (default 55)")
    p.add_argument("--file", help="type the contents of this file instead of built-in snippets")
    p.add_argument("--clear", action="store_true",
                   help="select-all + delete after each snippet so the file never grows")
    p.add_argument("--keep-indent", action="store_true",
                   help="type leading spaces (use in plain editors like Notepad)")
    p.add_argument("--mouse-min", type=float, default=2.0, help="min seconds between mouse moves")
    p.add_argument("--mouse-max", type=float, default=6.0, help="max seconds between mouse moves")
    p.add_argument("--delay", type=float, default=5.0,
                   help="seconds to wait before starting (time to click into your editor)")
    p.add_argument("--minutes", type=float, default=0, help="stop automatically after N minutes (0 = never)")
    args = p.parse_args()

    snippets = SNIPPETS
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            content = fh.read()
        # split file into chunks of ~25 lines so it loops nicely
        lines = content.splitlines()
        snippets = ["\n".join(lines[i:i + 25]) for i in range(0, len(lines), 25)] or SNIPPETS

    esc = start_esc_listener()
    print("code-bot starting in %d seconds..." % args.delay)
    print("-> click into an EMPTY editor window now.")
    print("Stop: Ctrl+C here, mouse to TOP-LEFT corner" + (", or press Esc." if esc else "."))
    for i in range(int(args.delay), 0, -1):
        print(f"  {i}...", flush=True)
        time.sleep(1)

    lock = threading.Lock()
    threads = []
    if not args.type_only:
        threads.append(threading.Thread(target=mouse_loop, daemon=True,
                                        args=(lock, args.mouse_min, args.mouse_max)))
    if not args.mouse_only:
        threads.append(threading.Thread(target=type_loop, daemon=True,
                                        args=(lock, snippets, args.wpm, args.clear,
                                              args.keep_indent, 2.0)))
    for t in threads:
        t.start()
    print("Running.")

    end = time.time() + args.minutes * 60 if args.minutes else None
    try:
        while not STOP.is_set():
            if end and time.time() >= end:
                STOP.set()
            time.sleep(0.2)
    except KeyboardInterrupt:
        STOP.set()
    for t in threads:
        t.join(timeout=3)
    print("\nStopped.")


if __name__ == "__main__":
    main()
