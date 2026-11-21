@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
python code_bot.py %*
pause
