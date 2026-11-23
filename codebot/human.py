"""Human-like mouse movement.

Real hands don't move in straight lines at constant speed. This module moves the
cursor along a curved (Bezier) path with a minimum-jerk speed profile
(slow start, fast middle, slow finish), slight hand tremor, movement time that
follows Fitts' law, and occasional overshoot + correction on long moves.
"""

import math
import random
import time

import pyautogui

SAFE_MARGIN = 40  # stay away from the screen edges/corners

# The rectangle (x, y, w, h) the bot's mouse is allowed to use: one monitor.
BOUNDS = None
# Last position the bot itself put the cursor at (used to notice when *you* move it).
last_pos = None
last_move_time = 0.0
# when the bot itself last pressed Esc (so the Esc-Esc kill switch ignores it)
last_bot_esc = 0.0
# called when the cursor isn't where the bot left it mid-move (someone grabbed the mouse)
on_interfere = None


def set_bounds(rect):
    global BOUNDS
    BOUNDS = tuple(int(v) for v in rect) if rect else None


def bounds():
    if BOUNDS:
        return BOUNDS
    w, h = pyautogui.size()
    return (0, 0, w, h)


def press_esc():
    """Esc pressed by the bot (closes a suggestion popup) - never counts as the kill switch."""
    global last_bot_esc
    last_bot_esc = time.time()
    pyautogui.press("esc")
    last_bot_esc = time.time()


def _clamp(x, y):
    bx, by, bw, bh = bounds()
    return (min(max(bx + SAFE_MARGIN, x), bx + bw - SAFE_MARGIN),
            min(max(by + SAFE_MARGIN, y), by + bh - SAFE_MARGIN))


def _put(x, y):
    global last_pos, last_move_time
    last_pos = (x, y)
    last_move_time = time.time()
    pyautogui.moveTo(x, y, _pause=False)


def inside(x, y):
    bx, by, bw, bh = bounds()
    return bx <= x < bx + bw and by <= y < by + bh


def _min_jerk(t):
    return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    x = u ** 3 * p0[0] + 3 * u ** 2 * t * p1[0] + 3 * u * t ** 2 * p2[0] + t ** 3 * p3[0]
    y = u ** 3 * p0[1] + 3 * u ** 2 * t * p1[1] + 3 * u * t ** 2 * p2[1] + t ** 3 * p3[1]
    return x, y


def _segment(x0, y0, x1, y1, speed=1.0, stop=None):
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist < 1:
        return
    # Fitts' law: T = a + b * log2(D / W + 1)
    duration = (0.08 + 0.11 * math.log2(dist / 12 + 1)) * random.uniform(0.85, 1.25) / speed
    # curved path: control points pushed sideways from the straight line
    nx, ny = -(y1 - y0) / dist, (x1 - x0) / dist
    bend = random.uniform(-0.25, 0.25) * dist
    c1 = (x0 + (x1 - x0) * random.uniform(0.2, 0.4) + nx * bend,
          y0 + (y1 - y0) * random.uniform(0.2, 0.4) + ny * bend)
    c2 = (x0 + (x1 - x0) * random.uniform(0.6, 0.8) + nx * bend * random.uniform(0.3, 0.9),
          y0 + (y1 - y0) * random.uniform(0.6, 0.8) + ny * bend * random.uniform(0.3, 0.9))
    steps = max(8, min(120, int(duration * 90)))
    dt = duration / steps
    tremor = min(1.6, 0.4 + dist / 900)
    for i in range(1, steps + 1):
        if stop is not None and stop():
            return
        if last_pos is not None and i % 3 == 0:
            cx, cy = pyautogui.position()
            if abs(cx - last_pos[0]) + abs(cy - last_pos[1]) > 12:
                if on_interfere:
                    on_interfere()
                return
        t = _min_jerk(i / steps)
        x, y = _bezier((x0, y0), c1, c2, (x1, y1), t)
        fade = 1 - i / steps  # tremor fades as the hand settles on target
        x += random.gauss(0, tremor) * fade
        y += random.gauss(0, tremor) * fade
        _put(*_clamp(round(x), round(y)))
        time.sleep(dt)


def move_to(x, y, speed=1.0, stop=None):
    """Move like a person to (x, y), staying inside BOUNDS."""
    x, y = _clamp(int(x), int(y))
    x0, y0 = pyautogui.position()
    if not inside(x0, y0):
        # cursor is on another monitor - a real hand would just appear from the
        # screen edge, so start the path from the nearest edge of our screen
        x0, y0 = _clamp(x0, y0)
        _put(x0, y0)
    dist = math.hypot(x - x0, y - y0)
    if dist > 250 and random.random() < 0.35:
        # overshoot the target a little, then correct back
        over = random.uniform(0.03, 0.08)
        ox = x + (x - x0) * over + random.uniform(-6, 6)
        oy = y + (y - y0) * over + random.uniform(-6, 6)
        ox, oy = _clamp(int(ox), int(oy))
        _segment(x0, y0, ox, oy, speed, stop)
        time.sleep(random.uniform(0.03, 0.12))
        if stop is not None and stop():
            return
        _segment(ox, oy, x, y, speed * 1.6, stop)
    else:
        _segment(x0, y0, x, y, speed, stop)
    # final settle: real cursors rarely land on the exact pixel and freeze
    if random.random() < 0.4:
        time.sleep(random.uniform(0.05, 0.2))
        if stop is not None and stop():
            return
        _segment(x, y, *_clamp(x + random.randint(-3, 3), y + random.randint(-3, 3)), speed * 2, stop)


def micro_drift(stop=None):
    """Tiny resting-hand movement of a few pixels."""
    x, y = pyautogui.position()
    if not inside(x, y):  # cursor is on another screen: come back to ours first
        bx, by, bw, bh = bounds()
        move_to(bx + bw * random.uniform(0.3, 0.7), by + bh * random.uniform(0.3, 0.7), stop=stop)
        return
    move_to(x + random.randint(-25, 25), y + random.randint(-18, 18), speed=0.6, stop=stop)


def read_lines(region, stop=None):
    """Hover over the code area and drift down as if following lines with the eyes."""
    l, t, w, h = region
    x = l + w * random.uniform(0.15, 0.55)
    y = t + h * random.uniform(0.2, 0.6)
    move_to(x, y, stop=stop)
    for _ in range(random.randint(2, 6)):
        if stop is not None and stop():
            return
        time.sleep(random.uniform(0.3, 1.1))
        x += random.uniform(-30, 60)
        y += random.uniform(8, 40)
        move_to(x, min(y, t + h * 0.92), speed=0.5, stop=stop)
