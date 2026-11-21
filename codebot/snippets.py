"""Built-in code snippets, grouped by language."""

SNIPPETS = {
    "python": [
'''def fibonacci(n):
    """Return the first n Fibonacci numbers."""
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]


if __name__ == "__main__":
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
'''import logging
import time
from functools import wraps

log = logging.getLogger(__name__)


def retry(times=3, delay=0.5):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    log.warning("attempt %d failed: %s", attempt, exc)
                    time.sleep(delay * attempt)
            raise RuntimeError(f"{fn.__name__} failed after {times} tries")
        return wrapper
    return decorator
''',
'''from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    title: str
    priority: int = 3
    done: bool = False
    created: datetime = field(default_factory=datetime.now)

    def complete(self):
        self.done = True


def pending(tasks):
    return sorted((t for t in tasks if not t.done), key=lambda t: t.priority)
''',
    ],
    "javascript": [
'''async function fetchUsers(page = 1) {
  const res = await fetch(`/api/users?page=${page}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  const data = await res.json();
  return data.users.map((u) => ({ id: u.id, name: u.name }));
}
''',
'''function debounce(fn, wait = 300) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(null, args), wait);
  };
}

const onSearch = debounce((query) => {
  console.log("searching for", query);
}, 250);
''',
'''const express = require("express");
const app = express();

app.use(express.json());

const todos = [];

app.get("/todos", (req, res) => res.json(todos));

app.post("/todos", (req, res) => {
  const todo = { id: todos.length + 1, text: req.body.text, done: false };
  todos.push(todo);
  res.status(201).json(todo);
});

app.listen(3000, () => console.log("listening on 3000"));
''',
    ],
    "typescript": [
'''interface User {
  id: number;
  email: string;
  roles: string[];
}

export function hasRole(user: User, role: string): boolean {
  return user.roles.includes(role);
}

export function groupByRole(users: User[]): Record<string, User[]> {
  const out: Record<string, User[]> = {};
  for (const u of users) {
    for (const r of u.roles) {
      (out[r] ??= []).push(u);
    }
  }
  return out;
}
''',
'''type Result<T> = { ok: true; value: T } | { ok: false; error: string };

export async function safeJson<T>(url: string): Promise<Result<T>> {
  try {
    const res = await fetch(url);
    if (!res.ok) return { ok: false, error: `HTTP ${res.status}` };
    return { ok: true, value: (await res.json()) as T };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}
''',
    ],
    "sql": [
'''SELECT u.id, u.name, COUNT(o.id) AS orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2025-01-01'
GROUP BY u.id, u.name
ORDER BY orders DESC
LIMIT 20;
''',
'''CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    issued_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoices_customer ON invoices(customer_id);
''',
    ],
    "go": [
'''package main

import (
    "fmt"
    "net/http"
)

func health(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    fmt.Fprintln(w, "ok")
}

func main() {
    http.HandleFunc("/health", health)
    fmt.Println("listening on :8080")
    http.ListenAndServe(":8080", nil)
}
''',
    ],
    "java": [
'''public class Stack<T> {
    private Object[] data = new Object[16];
    private int size = 0;

    public void push(T item) {
        if (size == data.length) {
            data = java.util.Arrays.copyOf(data, size * 2);
        }
        data[size++] = item;
    }

    @SuppressWarnings("unchecked")
    public T pop() {
        if (size == 0) throw new RuntimeException("empty");
        return (T) data[--size];
    }
}
''',
    ],
}

LANGUAGES = list(SNIPPETS)


def pick_pool(languages):
    """Return [(language, snippet), ...] for the chosen languages."""
    langs = [l for l in (languages or LANGUAGES) if l in SNIPPETS] or LANGUAGES
    return [(l, s) for l in langs for s in SNIPPETS[l]]


def chunk_file(path, lines_per_chunk=25):
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    return [("file", "\n".join(lines[i:i + lines_per_chunk]) + "\n")
            for i in range(0, len(lines), lines_per_chunk)]
