#!/usr/bin/env python3
"""Install Invotech 360 on this computer (run once):

    python install.py              # desktop icon + start at login + daily 3 AM start
    python install.py --uninstall  # remove all of that again

Windows : a desktop shortcut with the Invotech 360 icon, a shortcut in your Startup folder
          (starts quietly in the background when you sign in), and a Task Scheduler task
          that starts it every day at the schedule time and wakes the PC from sleep for it.
macOS   : a LaunchAgent (at login + every day at the schedule time) and a desktop launcher.
Linux   : an autostart entry, a desktop launcher and a cron entry at the schedule time.

There is no run or daily time limit. Invotech 360 itself controls the schedule time.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app.py")
ICO = os.path.join(HERE, "assets", "invotech360.ico")
PNG = os.path.join(HERE, "assets", "invotech360.png")
NAME = "Invotech 360"
IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"


def schedule_start():
    for path in (os.path.join(HERE, "bot_data", "settings.json"), os.path.join(HERE, "settings.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                value = json.load(fh).get("schedule_start", "03:00")
            hh, mm = (int(v) for v in value.split(":"))
            return hh, mm
        except (OSError, ValueError, AttributeError):
            continue
    return 3, 0


# ----------------------------------------------------------------------------- Windows
def _ps(script):
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8-sig") as fh:
        fh.write(script)
        path = fh.name
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path],
                             capture_output=True, text=True)
        if out.returncode != 0:
            print(out.stdout + out.stderr)
        return out.returncode == 0
    finally:
        os.remove(path)


def _q(path):                      # PowerShell single-quoted string
    return "'" + path.replace("'", "''") + "'"


def windows(uninstall):
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    hh, mm = schedule_start()
    if uninstall:
        ok = _ps(f"""
$desk = [Environment]::GetFolderPath('Desktop'); $start = [Environment]::GetFolderPath('Startup')
$menu = [Environment]::GetFolderPath('Programs')
Remove-Item -ErrorAction SilentlyContinue (Join-Path $desk '{NAME}.lnk'), (Join-Path $start '{NAME}.lnk'), (Join-Path $menu '{NAME}.lnk')
Unregister-ScheduledTask -TaskName '{NAME}' -Confirm:$false -ErrorAction SilentlyContinue
""")
        print("Removed the desktop and Start menu icons, the startup entry and the scheduled task." if ok else "Some parts could not be removed.")
        return
    ok = _ps(f"""
$shell = New-Object -ComObject WScript.Shell
function Make($path, $arguments, $desc) {{
  $s = $shell.CreateShortcut($path)
  $s.TargetPath = {_q(pythonw)}
  $s.Arguments = $arguments
  $s.WorkingDirectory = {_q(HERE)}
  $s.IconLocation = {_q(ICO)} + ',0'
  $s.Description = $desc
  $s.Save()
}}
$desk = [Environment]::GetFolderPath('Desktop'); $start = [Environment]::GetFolderPath('Startup')
$menu = [Environment]::GetFolderPath('Programs')
Make (Join-Path $desk '{NAME}.lnk') {_q('"' + APP + '"')} 'Open the {NAME} dashboard'
Make (Join-Path $menu '{NAME}.lnk') {_q('"' + APP + '"')} 'Open the {NAME} dashboard'
Make (Join-Path $start '{NAME}.lnk') {_q('"' + APP + '" --background')} 'Start {NAME} in the background at sign-in'
$action = New-ScheduledTaskAction -Execute {_q(pythonw)} -Argument {_q('"' + APP + '" --background')} -WorkingDirectory {_q(HERE)}
$trigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::Today.AddHours({hh}).AddMinutes({mm}))
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName '{NAME}' -Action $action -Trigger $trigger -Settings $settings -Description 'Starts {NAME} every day (it runs at most the daily hours set in its dashboard).' -Force | Out-Null
""")
    if ok:
        print(f"Done:\n  - '{NAME}' icon on your desktop and in the Start menu (opens the dashboard)\n"
              f"  - starts by itself in the background when you sign in\n"
              f"  - Task Scheduler task '{NAME}' every day at {hh:02d}:{mm:02d}, waking the PC from sleep")
    else:
        print("Something went wrong (see above).")
    if ok:
        subprocess.Popen([pythonw, APP, "--background"], cwd=HERE, creationflags=0x00000008)  # DETACHED
        print(f"{NAME} is now running in the background. Double-click the desktop icon to open the dashboard.")
        print(f"To pin it to the taskbar: open Start, type '{NAME}', right-click it > Pin to taskbar.")


# ------------------------------------------------------------------------------ macOS
def mac(uninstall):
    agent = os.path.expanduser("~/Library/LaunchAgents/com.invotech360.agent.plist")
    launcher = os.path.expanduser(f"~/Desktop/{NAME}.command")
    if uninstall:
        subprocess.run(["launchctl", "unload", agent], capture_output=True)
        for p in (agent, launcher):
            if os.path.exists(p):
                os.remove(p)
        print("Removed the LaunchAgent and the desktop launcher.")
        return
    hh, mm = schedule_start()
    os.makedirs(os.path.dirname(agent), exist_ok=True)
    with open(agent, "w", encoding="utf-8") as fh:
        fh.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.invotech360.agent</string>
  <key>ProgramArguments</key><array><string>{sys.executable}</string><string>{APP}</string><string>--background</string></array>
  <key>WorkingDirectory</key><string>{HERE}</string>
  <key>RunAtLoad</key><true/>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>{hh}</integer><key>Minute</key><integer>{mm}</integer></dict>
</dict></plist>
""")
    subprocess.run(["launchctl", "unload", agent], capture_output=True)
    subprocess.run(["launchctl", "load", agent], capture_output=True)
    with open(launcher, "w", encoding="utf-8") as fh:
        fh.write(f'#!/bin/sh\ncd "{HERE}" && exec "{sys.executable}" app.py\n')
    os.chmod(launcher, 0o755)
    print(f"Done: starts at login and every day at {hh:02d}:{mm:02d}; '{NAME}' launcher on your desktop.\n"
          f"To wake the Mac for it: sudo pmset repeat wakeorpoweron MTWRFSU {hh:02d}:{max(0, mm - 2):02d}:00")


# ------------------------------------------------------------------------------ Linux
def linux(uninstall):
    autostart = os.path.expanduser("~/.config/autostart/invotech360.desktop")
    desk_dir = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True).stdout.strip() \
        if shutil.which("xdg-user-dir") else os.path.expanduser("~/Desktop")
    desktop = os.path.join(desk_dir, "invotech360.desktop")
    marker = "# invotech360"
    cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout if shutil.which("crontab") else ""
    cron = "\n".join(l for l in cron.splitlines() if marker not in l)
    if uninstall:
        for p in (autostart, desktop):
            if os.path.exists(p):
                os.remove(p)
        if shutil.which("crontab"):
            subprocess.run(["crontab", "-"], input=cron + "\n", text=True)
        print("Removed the autostart entry, the desktop launcher and the cron entry.")
        return
    hh, mm = schedule_start()
    entry = ("[Desktop Entry]\nType=Application\nName={name}\nComment=Task automation\n"
             f"Icon={PNG}\nPath={HERE}\nTerminal=false\n")
    os.makedirs(os.path.dirname(autostart), exist_ok=True)
    with open(autostart, "w", encoding="utf-8") as fh:
        fh.write(entry.format(name=NAME) + f'Exec="{sys.executable}" "{APP}" --background\n')
    os.makedirs(desk_dir, exist_ok=True)
    with open(desktop, "w", encoding="utf-8") as fh:
        fh.write(entry.format(name=NAME) + f'Exec="{sys.executable}" "{APP}"\n')
    os.chmod(desktop, 0o755)
    if shutil.which("crontab"):
        line = f'{mm} {hh} * * * cd "{HERE}" && DISPLAY=:0 "{sys.executable}" app.py --background {marker}'
        subprocess.run(["crontab", "-"], input=(cron + "\n" + line + "\n").lstrip("\n"), text=True)
    print(f"Done: starts at login (autostart), every day at {hh:02d}:{mm:02d} (cron), and '{NAME}' is on your desktop.")


def main():
    uninstall = "--uninstall" in sys.argv
    if IS_WIN:
        windows(uninstall)
    elif IS_MAC:
        mac(uninstall)
    else:
        linux(uninstall)


if __name__ == "__main__":
    main()
