"""Project library: every folder in ./projects is a project the bot can 'write'.

Drop any real project folder in there or import it from a ZIP in the dashboard; the bot types
supported files file by file.
An optional `.codebot-order` file lists the files in the order to type them.
"""

import io
import json
import os
import random
import re
import shutil
import stat
import sys
import tempfile
import threading
import zipfile
import zlib
from .storage import PROJECT_UPLOADS_DIR

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(HERE, "projects")

TEXT_EXT = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rs", ".rb", ".php", ".cs",
    ".c", ".h", ".cpp", ".hpp", ".swift", ".sql", ".html", ".css", ".scss", ".json", ".yaml",
    ".yml", ".toml", ".md", ".txt", ".sh", ".mod", ".cfg", ".ini", ".env", ".xml", ".vue",
    ".svelte", ".mdx", ".rst", ".csproj", ".sln", ".props", ".targets", ".lock", ".properties",
    ".gradle", ".bat", ".ps1", ".dockerignore", ".editorconfig", ".gitattributes", ".yarnrc",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".idea", ".vscode"}
MAX_FILE_BYTES = 400_000
PROJECT_UPLOAD_MAX_BYTES = 50_000_000
PROJECT_UPLOAD_MAX_FILES = 2_500
PROJECT_UPLOAD_MAX_EXPANDED = 150_000_000
UPLOAD_MARKER = ".codebot-upload.json"
_UPLOAD_LOCK = threading.Lock()
_TYPEABLE_NAMES = {
    "Dockerfile", "Makefile", "CMakeLists.txt", "Procfile", ".gitignore", ".dockerignore",
    ".editorconfig", ".gitattributes", ".npmrc", ".nvmrc", ".python-version", ".env",
    "LICENSE", "NOTICE", "AUTHORS", "CHANGELOG", "CONTRIBUTING", "Gemfile", "Rakefile",
    "Justfile", "Brewfile",
}
_PROJECT_ROOT_DIRS = {
    "src", "app", "lib", "docs", "test", "tests", "examples", "public", "static", "cmd",
    "internal", "pkg", "include", "assets", "scripts", "config", "bin", "backend", "frontend",
}


def list_projects():
    names = set()
    for root in (PROJECTS_DIR, PROJECT_UPLOADS_DIR):
        if os.path.isdir(root):
            names.update(d for d in os.listdir(root)
                         if os.path.isdir(os.path.join(root, d)) and not d.startswith("."))
    return sorted(names)


def _project_path(name):
    """Resolve built-in projects and locally stored uploaded projects."""
    for root in (PROJECTS_DIR, PROJECT_UPLOADS_DIR):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            return path
    return os.path.join(PROJECTS_DIR, name)


def _is_typeable(path):
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path)
    if ext not in TEXT_EXT and name not in _TYPEABLE_NAMES:
        return False
    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            return False
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return False
    return _is_typeable_text(name, text)


def _is_typeable_text(name, text):
    ext = os.path.splitext(name)[1].lower()
    if ext not in TEXT_EXT and name not in _TYPEABLE_NAMES:
        return False
    if len(text.encode("utf-8")) > MAX_FILE_BYTES:
        return False
    return all(ch in "\n\r\t" or 32 <= ord(ch) < 127 for ch in text)  # plain ASCII only


def uploaded_projects():
    """Uploaded projects that can be removed from the library."""
    out = []
    for name in list_projects():
        folder = _project_path(name)
        marker = os.path.join(folder, UPLOAD_MARKER)
        try:
            with open(marker, encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("managed_by") == "invotech360-project-upload":
                out.append({"name": name, "archive": data.get("archive", name),
                            "files": int(data.get("files", 0))})
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return out


def import_project_archive(filename, payload):
    """Import supported plain-text files from a ZIP into the project library.

    Archive paths are validated before extraction; binary files and common dependency/build
    folders are skipped. The order list preserves the archive's file order.
    """
    if not isinstance(payload, bytes) or not payload:
        raise ValueError("The ZIP file is empty")
    if len(payload) > PROJECT_UPLOAD_MAX_BYTES:
        raise ValueError("ZIP files must be 50 MB or smaller")
    raw_name = str(filename or "project.zip").replace("\\", "/").rsplit("/", 1)[-1]
    if not raw_name.lower().endswith(".zip"):
        raise ValueError("Choose a .zip file containing your project folder")

    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError("That file is not a readable ZIP archive") from exc

    candidates = []
    order_entry = None
    skipped = 0
    expanded = 0
    infos = archive.infolist()
    if len(infos) > 10_000:
        raise ValueError("The ZIP has too many entries")
    for info in infos:
        if info.is_dir():
            continue
        rel = info.filename.replace("\\", "/")
        parts = rel.split("/")
        if (not rel or rel.startswith("/") or any(":" in part for part in parts)
                or any(part in ("", ".", "..") for part in parts)):
            raise ValueError("The ZIP contains an unsafe file path")
        # Ignore common generated folders before inspecting their file metadata. ZIPs made
        # by Git, npm, or macOS can contain links or encrypted metadata in these folders;
        # none of those entries are ever extracted into a project.
        if any(part in SKIP_DIRS or part == "__MACOSX" for part in parts[:-1]):
            skipped += 1
            continue
        mode = (info.external_attr >> 16) & 0o170000
        if stat.S_ISLNK(mode):
            raise ValueError("ZIP projects cannot contain symbolic links")
        if mode and mode != stat.S_IFREG:
            raise ValueError("The ZIP contains a non-regular file")
        if info.flag_bits & 0x1:
            raise ValueError("Encrypted ZIP files are not supported")
        basename = parts[-1]
        if basename == ".codebot-order":
            if len(parts) <= 2 and info.file_size <= 200_000:
                order_entry = (parts, info)
            continue
        if basename.startswith(".codebot") or basename == ".DS_Store":
            skipped += 1
            continue
        if os.path.splitext(basename)[1].lower() not in TEXT_EXT and basename not in _TYPEABLE_NAMES:
            skipped += 1
            continue
        if info.file_size > MAX_FILE_BYTES:
            skipped += 1
            continue
        expanded += info.file_size
        if expanded > PROJECT_UPLOAD_MAX_EXPANDED:
            raise ValueError("The ZIP contains too much project source text")
        try:
            content = archive.read(info)
            text = content.decode("utf-8-sig")
            content = text.encode("utf-8")
        except (UnicodeDecodeError, RuntimeError, EOFError, zlib.error, zipfile.BadZipFile, NotImplementedError):
            skipped += 1
            continue
        if not _is_typeable_text(basename, text):
            skipped += 1
            continue
        if len(candidates) >= PROJECT_UPLOAD_MAX_FILES:
            raise ValueError("The ZIP has too many supported project files")
        candidates.append((parts, content))

    if not candidates:
        raise ValueError("No supported plain-text project files were found in that ZIP")
    if len(candidates) > PROJECT_UPLOAD_MAX_FILES:
        raise ValueError("The ZIP has too many supported project files")

    first_parts = {parts[0] for parts, _ in candidates}
    has_root_files = any(len(parts) == 1 for parts, _ in candidates)
    only_root = next(iter(first_parts)) if len(first_parts) == 1 else None
    archive_stem = os.path.splitext(raw_name)[0].casefold()
    strip_root = (only_root if only_root and not has_root_files
                  and (only_root.casefold() == archive_stem or only_root.casefold() not in _PROJECT_ROOT_DIRS)
                  else None)
    files = []
    seen = set()
    for parts, content in candidates:
        rel_parts = parts[1:] if strip_root and parts[0] == strip_root else parts
        rel = "/".join(rel_parts)
        if not rel or rel.casefold() in seen:
            raise ValueError("The ZIP has duplicate project file paths")
        seen.add(rel.casefold())
        files.append((rel, content))

    requested = []
    if order_entry:
        parts, info = order_entry
        rel_parts = parts[1:] if strip_root and parts[0] == strip_root else parts
        if rel_parts == [".codebot-order"]:
            try:
                order_text = archive.read(info).decode("ascii")
                requested = [line.strip().replace("\\", "/") for line in order_text.splitlines()
                             if line.strip() and not line.lstrip().startswith("#")]
            except (UnicodeDecodeError, RuntimeError, EOFError, zlib.error, zipfile.BadZipFile):
                requested = []
    ordered = []
    remaining = dict(files)
    for rel in requested:
        if rel in remaining:
            ordered.append(rel)
            remaining.pop(rel)
    ordered.extend(rel for rel, _ in files if rel in remaining)
    file_data = dict(files)

    stem = os.path.splitext(raw_name)[0]
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-_-")[:48].lower() or "uploaded-project"
    with _UPLOAD_LOCK:
        name = slug
        suffix = 2
        while any(os.path.lexists(os.path.join(root, name)) for root in (PROJECTS_DIR, PROJECT_UPLOADS_DIR)):
            name = f"{slug}-{suffix}"
            suffix += 1
        os.makedirs(PROJECT_UPLOADS_DIR, exist_ok=True)
        staging = tempfile.mkdtemp(prefix=".codebot-upload-", dir=PROJECT_UPLOADS_DIR)
        try:
            for rel in ordered:
                path = os.path.join(staging, *rel.split("/"))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(file_data[rel])
            with open(os.path.join(staging, ".codebot-order"), "w", encoding="ascii", newline="\n") as fh:
                fh.write("\n".join(ordered) + "\n")
            with open(os.path.join(staging, UPLOAD_MARKER), "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"managed_by": "invotech360-project-upload", "archive": raw_name,
                           "files": len(ordered)}, fh, indent=2)
            os.replace(staging, os.path.join(PROJECT_UPLOADS_DIR, name))
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
    return {"name": name, "files": len(ordered), "skipped": skipped}


def delete_uploaded_project(name):
    """Delete only a direct child project carrying our upload marker."""
    if not isinstance(name, str) or not name or name in (".", "..") or "/" in name or "\\" in name:
        return False
    roots = {os.path.abspath(root) for root in (PROJECTS_DIR, PROJECT_UPLOADS_DIR)}
    folder = os.path.abspath(_project_path(name))
    if os.path.dirname(folder) not in roots or os.path.islink(folder) or not os.path.isdir(folder):
        return False
    marker = os.path.join(folder, UPLOAD_MARKER)
    try:
        with open(marker, encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("managed_by") != "invotech360-project-upload":
            return False
    except (OSError, ValueError, AttributeError):
        return False
    shutil.rmtree(folder)
    return True


def project_files(name):
    """Return [(relative_path, content), ...] in typing order."""
    root = _project_path(name)
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


def project_scaffold(name, typed):
    """Files of a library project that aren't typed (not in its .codebot-order): they're
    put in place instantly when the project starts (go.mod, package.json, README...)."""
    root = _project_path(name)
    if not os.path.exists(os.path.join(root, ".codebot-order")):
        return []
    typed = set(typed)
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/")
            if f.startswith(".codebot") or rel in typed:
                continue
            try:
                with open(os.path.join(dirpath, f), encoding="utf-8") as fh:
                    out.append((rel, fh.read()))
            except (OSError, UnicodeDecodeError):
                pass
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
    """What to run once a project is written, as steps:
    {"cmd": str, "serve": bool, "open": url or None, "wait": seconds or None}.

    A `.codebot-run` file in the project lists them, one per line (# for comments):
        python -m pytest -q            # wait 30   <- optional: seconds to give it
        serve: python -m uvicorn main:app --port 8000   <- the app itself, left running a while
        open: http://127.0.0.1:8000/docs                <- shown in VS Code's browser
    Without one, a safe default is picked from the project type.
    """
    root = _project_path(name)
    run_file = os.path.join(root, ".codebot-run")
    lines = []
    if os.path.exists(run_file):
        with open(run_file, encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
    elif os.path.exists(os.path.join(root, "go.mod")):
        lines = ["go build ./..."]
    elif any(f.endswith(".py") for _, _, fs in os.walk(root) for f in fs):
        lines = ["python -m compileall -q ."]
    steps = []
    for line in lines:
        wait = None
        m = re.search(r"\s+#\s*wait\s+(\d+)\s*$", line)
        if m:
            wait = int(m.group(1))
            line = line[:m.start()].rstrip()
        low = line.lower()
        if low.startswith("open:"):
            if steps and steps[-1]["serve"]:
                steps[-1]["open"] = line[5:].strip()
            continue
        serve = low.startswith("serve:")
        if serve:
            line = line[6:].strip()
        steps.append({"cmd": line, "serve": serve, "open": None, "wait": wait})
    return steps


def localize_command(cmd):
    """Make a command right for this computer: `{venv}` = the project's virtualenv
    scripts folder, and `python` is often called `python3` on macOS / Linux."""
    win = sys.platform.startswith("win")
    cmd = cmd.replace("{venv}", ".venv\\Scripts\\" if win else ".venv/bin/")
    if cmd.startswith("python ") and not shutil.which("python") and shutil.which("python3"):
        return "python3 " + cmd[len("python "):]
    return cmd


def guess_wait(cmd):
    """Roughly how long a command takes (the bot can't read VS Code's terminal)."""
    low = cmd.lower()
    if "install" in low or "venv" in low:
        return 45
    if "test" in low:
        return 25
    if any(w in low for w in ("build", "vet", "tsc", "compile", "lint")):
        return 15
    return 12


def explain_command(cmd, serve=False):
    """A plain-English line the bot types (echo) before running a command."""
    low = cmd.lower()
    if serve:
        return "Starting the app so we can see it running"
    if "venv" in low:
        return "Creating a separate Python environment for this project"
    if "install" in low:
        return "Installing what the project needs"
    if "test" in low:
        return "Running the tests to check everything works"
    if "vet" in low or "compileall" in low or "tsc" in low or "build" in low:
        return "Checking the code for mistakes"
    if "selftest" in low or low.startswith(("node ", "python ")):
        return "Running the program"
    return "Running: " + cmd.split()[0]
