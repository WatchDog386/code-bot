"""Project library: every folder in ./projects is a project the bot can 'write'.

Drop any real project folder in there and the bot will type it file by file.
An optional `.codebot-order` file lists the files in the order to type them.
"""

import os
import random
import shutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(HERE, "projects")

TEXT_EXT = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rs", ".rb", ".php", ".cs",
    ".c", ".h", ".cpp", ".hpp", ".swift", ".sql", ".html", ".css", ".scss", ".json", ".yaml",
    ".yml", ".toml", ".md", ".txt", ".sh", ".mod", ".cfg", ".ini", ".env", ".xml", ".vue",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".idea", ".vscode"}
MAX_FILE_BYTES = 60_000


def list_projects():
    if not os.path.isdir(PROJECTS_DIR):
        return []
    return sorted(d for d in os.listdir(PROJECTS_DIR)
                  if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith("."))


def _is_typeable(path):
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path)
    if ext not in TEXT_EXT and name not in ("Dockerfile", "Makefile", ".gitignore"):
        return False
    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            return False
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return False
    return all(ch in "\n\t" or 32 <= ord(ch) < 127 for ch in text)  # plain ASCII only


def project_files(name):
    """Return [(relative_path, content), ...] in typing order."""
    root = os.path.join(PROJECTS_DIR, name)
    order_file = os.path.join(root, ".codebot-order")
    rels = []
    if os.path.exists(order_file):
        with open(order_file, encoding="utf-8") as fh:
            rels = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    else:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for f in sorted(filenames):
                if f.startswith(".codebot"):
                    continue
                rels.append(os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/"))
        # config/docs first, then source, tests last - like a real dev
        def rank(p):
            low = p.lower()
            if low.endswith((".md", ".json", ".toml", ".mod", ".txt", ".yaml", ".yml", ".cfg")):
                return 0
            if "test" in low:
                return 2
            return 1
        rels.sort(key=lambda p: (rank(p), p.count("/"), p))
    out = []
    for rel in rels:
        full = os.path.join(root, rel)
        if os.path.isfile(full) and _is_typeable(full):
            with open(full, encoding="utf-8") as fh:
                out.append((rel, fh.read()))
    return out


def project_cycle(selected=None):
    """Yield (project_name, files) forever."""
    names = [n for n in (selected or []) if n in list_projects()] or list_projects()
    if not names:
        return
    last = None
    while True:
        order = names[:]
        random.shuffle(order)
        if len(order) > 1 and order[0] == last:
            order.append(order.pop(0))
        for name in order:
            files = project_files(name)
            if files:
                last = name
                yield name, files


def project_commands(name):
    """Commands to run once a project is written (build, tests...).

    A `.codebot-run` file in the project lists them, one per line (# for comments).
    Without one, a safe default is picked from the project type.
    """
    root = os.path.join(PROJECTS_DIR, name)
    run_file = os.path.join(root, ".codebot-run")
    if os.path.exists(run_file):
        with open(run_file, encoding="utf-8") as fh:
            return [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
    if os.path.exists(os.path.join(root, "go.mod")):
        return ["go build ./..."]
    if any(f.endswith(".py") for _, _, fs in os.walk(root) for f in fs):
        return ["python -m compileall -q ."]
    return []


def localize_command(cmd):
    """`python` is often called `python3` on macOS / Linux."""
    if cmd.startswith("python ") and not shutil.which("python") and shutil.which("python3"):
        return "python3 " + cmd[len("python "):]
    return cmd
