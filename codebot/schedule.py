"""Daily schedule: start by itself at a set time (default 03:00) and run at most N hours a
day (default 10). The day runs from one start time to the next, so with 03:00 / 10 h the
bot works 03:00-13:00 and "today's" hours reset at 03:00 the next morning.

Rules
- Inside the window, not stopped by you today, hours left -> it starts by itself (also when
  the app is opened at login in the middle of the window).
- The daily limit always applies, also when you start it by hand: at 10 h it stops and
  won't start again until the next day.
- A run the schedule started is stopped when the window ends.
- If you stop it yourself (Stop / Esc Esc), it stays stopped until the next day's start.
- Hours used are saved in usage.json, so restarting the computer doesn't reset them.
"""

import json
import os
import threading
import time
from dataclasses import asdict
from datetime import date, datetime, timedelta

COUNTED = ("running", "you", "break")      # states that use up the daily hours


def start_parts(cfg):
    hh, mm = (int(v) for v in cfg.schedule_start.split(":"))
    return hh, mm


def day_key(now, cfg):
    """Which schedule day `now` belongs to (days begin at the start time)."""
    hh, mm = start_parts(cfg)
    return (now - timedelta(hours=hh, minutes=mm)).date().isoformat()


def window(now, cfg):
    """(start, end) of the window of the schedule day containing `now`."""
    hh, mm = start_parts(cfg)
    start = datetime.combine(date.fromisoformat(day_key(now, cfg)), datetime.min.time()).replace(hour=hh, minute=mm)
    return start, start + timedelta(hours=cfg.daily_hours or 24)


def fmt_hours(seconds):
    seconds = int(max(0, seconds))
    return f"{seconds // 3600}h {seconds % 3600 // 60:02d}m"


class Scheduler:
    def __init__(self, bot, load_cfg, usage_path, now=datetime.now):
        self.bot = bot
        self.load_cfg = load_cfg
        self.usage_path = usage_path
        self.now = now
        self.usage = self._load()
        self.held_day = None            # schedule day you stopped it on (no auto-restart that day)
        self._last = None
        self._was_running = False
        self._was_in_window = None
        self._saved = 0.0
        self._lock = threading.Lock()

    # ------------------------------------------------------------- storage
    def _load(self):
        try:
            with open(self.usage_path, encoding="utf-8") as fh:
                data = json.load(fh)
            return {k: float(v) for k, v in data.items()}
        except (OSError, ValueError, AttributeError):
            return {}

    def _save(self):
        keep = dict(sorted(self.usage.items())[-30:])   # a month is plenty
        try:
            with open(self.usage_path, "w", encoding="utf-8") as fh:
                json.dump(keep, fh, indent=2)
        except OSError:
            pass

    # ------------------------------------------------------------- queries
    def used(self, now=None, cfg=None):
        cfg = cfg or self.load_cfg()
        return self.usage.get(day_key(now or self.now(), cfg), 0.0)

    def cap(self, cfg):
        return cfg.daily_hours * 3600 if cfg.daily_hours else 0

    def allow_start(self):
        """(ok, message) for a manual start."""
        cfg = self.load_cfg()
        now = self.now()
        cap = self.cap(cfg)
        if cap and self.used(now, cfg) >= cap:
            start, _ = window(now, cfg)
            return False, (f"Today's limit of {cfg.daily_hours:g} hours is used up - "
                           f"it starts again at {cfg.schedule_start} on {(start + timedelta(days=1)):%a %d %b}")
        return True, ""

    def status(self):
        cfg = self.load_cfg()
        now = self.now()
        start, end = window(now, cfg)
        used = self.used(now, cfg)
        cap = self.cap(cfg)
        key = day_key(now, cfg)
        in_win = start <= now < end
        if in_win and self.held_day != key and (not cap or used < cap):
            next_start = now
        else:
            next_start = start + timedelta(days=1)
        return {
            "enabled": cfg.schedule_enabled, "start": cfg.schedule_start, "hours": cfg.daily_hours,
            "window": f"{start:%H:%M}-{end:%H:%M}", "in_window": in_win,
            "used": int(used), "used_text": fmt_hours(used),
            "left": int(max(0, cap - used)) if cap else None,
            "left_text": fmt_hours(cap - used) if cap else "no limit",
            "held": self.held_day == key, "started_by": self.bot.started_by,
            "next_start": next_start.isoformat(timespec="minutes"),
            "next_start_text": "now" if next_start == now else f"{next_start:%a %H:%M}",
        }

    # ---------------------------------------------------------------- tick
    def tick(self):
        with self._lock:
            self._tick()

    def _tick(self):
        bot = self.bot
        cfg = self.load_cfg()
        now = self.now()
        key = day_key(now, cfg)
        # count the time the bot was really working since the last tick
        if self._last is not None and bot.running and bot.state in COUNTED:
            step = min(120.0, max(0.0, (now - self._last).total_seconds()))
            self.usage[key] = self.usage.get(key, 0.0) + step
        self._last = now
        if time.time() - self._saved > 60:
            self._save()
            self._saved = time.time()

        # you stopped it (Stop, Esc Esc, time limit): no automatic restart until tomorrow
        if self._was_running and not bot.running and bot.stop_reason not in ("schedule", "agent"):
            self.held_day = key
            bot.log(f"Stopped by you - the schedule starts it again at {cfg.schedule_start} tomorrow")
        cap = self.cap(cfg)
        used = self.usage.get(key, 0.0)
        start, end = window(now, cfg)
        in_win = start <= now < end

        if bot.running and cap and used >= cap:
            bot.log(f"Daily limit reached ({cfg.daily_hours:g} hours) - "
                    f"back at {cfg.schedule_start} tomorrow")
            bot.event("stop", "Daily limit reached", f"{cfg.daily_hours:g} hours today · back at {cfg.schedule_start}")
            bot.stop("schedule")
            self._save()
        elif bot.running and bot.started_by == "schedule" and self._was_in_window and not in_win:
            bot.log(f"Today's working hours are over ({start:%H:%M}-{end:%H:%M})")
            bot.event("stop", "Working hours over", f"back at {cfg.schedule_start} tomorrow")
            bot.stop("schedule")
            self._save()
        elif (cfg.schedule_enabled and not bot.running and in_win and self.held_day != key
              and (not cap or used < cap) and bot.state in ("idle", "stopped")):
            bot.log(f"Scheduled start ({cfg.schedule_start}, up to {cfg.daily_hours:g} hours a day; "
                    f"{fmt_hours(used)} used today)")
            ok, _ = bot.start(asdict(cfg))
            if ok:
                bot.started_by = "schedule"
        self._was_in_window = in_win
        self._was_running = bot.running

    def run_forever(self, every=5.0):
        def loop():
            while True:
                try:
                    self.tick()
                except Exception as exc:  # noqa: BLE001 - the scheduler must never die
                    try:
                        self.bot.log(f"Scheduler problem: {exc!r}")
                    except Exception:  # noqa: BLE001
                        pass
                time.sleep(every)
        t = threading.Thread(target=loop, daemon=True, name="invotech360-schedule")
        t.start()
        return t
