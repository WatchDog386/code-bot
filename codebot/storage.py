"""Local, file-based storage for Invotech 360 user data."""

import os

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(APP_DIR, "bot_data")
PROJECT_UPLOADS_DIR = os.path.join(DATA_DIR, "projects")
SHEET_UPLOADS_DIR = os.path.join(DATA_DIR, "sheets")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
USAGE_FILE = os.path.join(DATA_DIR, "usage.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR
