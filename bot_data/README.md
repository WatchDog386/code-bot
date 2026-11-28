# Local bot database

This is Invotech 360's local, file-based database. It stays on this computer and does not use a cloud database.

The app creates these files and folders here as needed:

- `projects/` for coding projects imported from ZIP files
- `sheets/` for uploaded spreadsheets
- `settings.json` for dashboard settings
- `usage.json` for schedule history

The app continues to read the existing built-in projects from the repository's `projects/` folder.
