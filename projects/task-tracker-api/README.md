# Task Tracker API

A small REST service for tracking tasks across projects.

## Features

- Create, update and complete tasks
- Filter tasks by project, status and priority
- Due-date tracking with overdue detection
- In-memory repository with a clean interface for swapping storage

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API is then available at http://localhost:8000 and the docs at /docs.

## Running tests

```bash
pytest -q
```
