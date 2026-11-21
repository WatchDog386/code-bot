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

SAFE_MARGIN = 40  # stay away from the screen corners (pyautogui fail-safe)


def _clamp(x, y):
    w, h = pyautogui.size()
    return (min(max(SAFE_MARGIN, x), w - SAFE_MARGIN),
            min(max(SAFE_MARGIN, y), h - SAFE_MARGIN))


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
        t = _min_jerk(i / steps)
        x, y = _bezier((x0, y0), c1, c2, (x1, y1), t)
        fade = 1 - i / steps  # tremor fades as the hand settles on target
        x += random.gauss(0, tremor) * fade
        y += random.gauss(0, tremor) * fade
        pyautogui.moveTo(*_clamp(round(x), round(y)), _pause=False)
        time.sleep(dt)


def move_to(x, y, speed=1.0, stop=None):
    """Move like a person to (x, y)."""
    x, y = _clamp(int(x), int(y))
    x0, y0 = pyautogui.position()
    dist = math.hypot(x - x0, y - y0)
    if dist > 250 and random.random() < 0.35:
        # overshoot the target a little, then correct back
        over = random.uniform(0.03, 0.08)
        ox = x + (x - x0) * over + random.uniform(-6, 6)
        oy = y + (y - y0) * over + random.uniform(-6, 6)
        ox, oy = _clamp(int(ox), int(oy))
        _segment(x0, y0, ox, oy, speed, stop)
        time.sleep(random.uniform(0.03, 0.12))
        _segment(ox, oy, x, y, speed * 1.6, stop)
    else:
        _segment(x0, y0, x, y, speed, stop)
    # final settle: real cursors rarely land on the exact pixel and freeze
    if random.random() < 0.4:
        time.sleep(random.uniform(0.05, 0.2))
        _segment(x, y, *_clamp(x + random.randint(-3, 3), y + random.randint(-3, 3)), speed * 2, stop)


def micro_drift(stop=None):
    """Tiny resting-hand movement of a few pixels."""
    x, y = pyautogui.position()
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
