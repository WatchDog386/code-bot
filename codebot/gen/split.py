"""Split long generated source files into several short files (40-100 lines each) that
still work together, so the bot finishes many files instead of one huge one.

Python  every part is a module of the same package; part k starts with
        `from .<part k-1> import *`, and the last part keeps the original name, so
        `from .models import X` still finds everything. Test files are split into
        independent test modules (each with the original imports).
Go      every part is a file of the same package (Go needs nothing else); each part gets
        only the imports it uses.
Code is cut only between top-level definitions, never inside one.
"""

import ast
import re


def _snake(name):
    if name.isupper() or "_" in name:
        return name.lower().strip("_")[:30] or "part"
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower().strip("_")[:30] or "part"


def _unique(name, taken):
    base, n = name, 2
    while name in taken:
        name = f"{base}_{n}"
        n += 1
    taken.add(name)
    return name


def _group(blocks, budget, rng, min_lines, max_lines, sep=1, first_budget=None):
    """Greedy: fill each part up to a random size between min_lines and max_lines, counting
    every line (the file's header, the blocks and the blank lines between them)."""
    parts, cur, size = [], [], 0
    head = budget if first_budget is None else first_budget
    target = rng.randint(min_lines, max_lines)
    for block in blocks:
        extra = len(block) + (sep if cur else 0)
        if cur and head + size + extra > min(target, max_lines):
            parts.append(cur)
            cur, size, head = [], 0, budget
            target = rng.randint(min_lines, max_lines)
            extra = len(block)
        cur.append(block)
        size += extra
    if cur:
        parts.append(cur)
    return parts


# --------------------------------------------------------------------------- Python
def _node_start(node):
    return min([d.lineno for d in getattr(node, "decorator_list", [])] + [node.lineno]) - 1


def split_python(rel, text, rng, max_lines=100, min_lines=40):
    lines = text.rstrip("\n").split("\n")
    if len(lines) <= max_lines:
        return [(rel, text)]
    tree = ast.parse(text)
    defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    if not defs:
        return [(rel, text)]
    first = _node_start(defs[0])
    header = lines[:first]
    while header and not header[-1].strip():
        header.pop()
    # the module docstring (first statement) - kept only in the first part
    doc_end = 0
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(getattr(tree.body[0], "value", None), ast.Constant) \
            and isinstance(tree.body[0].value.value, str):
        doc_end = tree.body[0].end_lineno
    imports = header[doc_end:]
    while imports and not imports[0].strip():
        imports.pop(0)
    starts = sorted({_node_start(n) for n in tree.body if _node_start(n) >= first})
    blocks = []
    for a, b in zip(starts, starts[1:] + [len(lines)]):
        block = lines[a:b]
        blocks.append(block)
    # comment lines at the end of a block belong to the next definition
    for i in range(len(blocks) - 1):
        while blocks[i] and (not blocks[i][-1].strip() or blocks[i][-1].lstrip().startswith("#")):
            moved = blocks[i].pop()
            if moved.strip():
                blocks[i + 1].insert(0, moved)
        while blocks[i] and not blocks[i][-1].strip():
            blocks[i].pop()
    blocks = [b for b in blocks if b]
    directory, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    stem = name[:-3]
    is_test = stem.startswith("test")
    budget = len(imports) + 6
    parts = _group(blocks, budget, rng, min_lines, max_lines, sep=2, first_budget=len(header) + 2)
    taken, names = {stem}, []
    for i, part in enumerate(parts):
        if is_test:
            names.append(stem if i == 0 else _unique(f"{stem}_{_first_name(part)}", taken))
        else:
            names.append(stem if i == len(parts) - 1 else _unique(f"{stem}_{_first_name(part)}", taken))
    out = []
    for i, part in enumerate(parts):
        body = []
        for block in part:
            if body:
                body += ["", ""]
            body += block
        if i == 0:
            head = header
        else:
            head = [f'"""{stem.replace("_", " ").capitalize()} (continued)."""', ""] + imports
            if not is_test:
                head = head + [f"from .{names[i - 1]} import *  # noqa: F401,F403"]
        content = "\n".join(head + ["", ""] + body).rstrip() + "\n"
        out.append(((directory + "/" if directory else "") + names[i] + ".py", content))
    return out


def _first_name(part):
    for line in (l for block in part for l in block):
        m = re.match(r"(?:async\s+)?(?:def|class)\s+(\w+)", line)
        if m:
            return _snake(m.group(1))
        m = re.match(r"([A-Za-z_]\w*)\s*[:=]", line)
        if m:
            return _snake(m.group(1))
    return "part"


# ------------------------------------------------------------------------------- Go
def _go_depth_changes(line, state):
    """Track {[( depth across a line, skipping strings, runes, raw strings and comments."""
    i, n = 0, len(line)
    while i < n:
        ch = line[i]
        if state["raw"]:
            if ch == "`":
                state["raw"] = False
        elif ch == "`":
            state["raw"] = True
        elif ch == "/" and line[i:i + 2] == "//":
            break
        elif ch in "\"'":
            quote, i = ch, i + 1
            while i < n and line[i] != quote:
                i += 2 if line[i] == "\\" else 1
        elif ch in "{[(":
            state["depth"] += 1
        elif ch in "}])":
            state["depth"] -= 1
        i += 1


def split_go(rel, text, rng, max_lines=100, min_lines=40):
    lines = text.rstrip("\n").split("\n")
    if len(lines) <= max_lines:
        return [(rel, text)]
    p = next(i for i, l in enumerate(lines) if l.startswith("package "))
    doc, package = lines[:p], lines[p]
    imports, i = [], p + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("import ("):
        i += 1
        while lines[i] != ")":
            imports.append(lines[i])
            i += 1
        i += 1
    elif i < len(lines) and lines[i].startswith("import "):
        imports.append("\t" + lines[i][7:])
        i += 1
    body = lines[i:]
    blocks, cur, state = [], [], {"depth": 0, "raw": False}
    for line in body:
        if not line.strip() and state["depth"] == 0 and not state["raw"]:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        cur.append(line)
        _go_depth_changes(line, state)
    if cur:
        blocks.append(cur)
    directory, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    test = name.endswith("_test.go")
    stem = name[:-8] if test else name[:-3]
    parts = _group(blocks, 5 + len(imports), rng, min_lines, max_lines, sep=1,
                   first_budget=5 + len(imports) + len(doc))
    taken, out = {stem}, []
    for k, part in enumerate(parts):
        code = "\n\n".join("\n".join(b) for b in part)
        used = []
        for imp in imports:
            spec = imp.strip()
            if not spec:
                used.append("")
                continue
            m = re.match(r'(?:(\w+)\s+)?"([^"]+)"', spec)
            ident = m.group(1) or m.group(2).rsplit("/", 1)[-1]
            if ident == "_" or re.search(rf"\b{re.escape(ident)}\.", code):
                used.append(imp)
        # tidy blank-line groups
        while used and not used[0].strip():
            used.pop(0)
        while used and not used[-1].strip():
            used.pop()
        used = [u for j, u in enumerate(used) if u.strip() or (j and used[j - 1].strip())]
        head = (doc if k == 0 else []) + [package]
        if len(used) == 1:
            head += ["", "import " + used[0].strip()]
        elif used:
            head += ["", "import ("] + used + [")"]
        fname = stem if k == 0 else _unique(f"{stem}_{_go_name(part)}", taken)
        fname += "_test.go" if test else ".go"
        out.append(((directory + "/" if directory else "") + fname, "\n".join(head + ["", code]).rstrip() + "\n"))
    return out


def _go_name(part):
    for line in (l for block in part for l in block):
        m = re.match(r"func\s+(?:\([^)]*\)\s*)?(\w+)|type\s+(\w+)|var\s+(\w+)|const\s+(\w+)", line)
        if m:
            return _snake(next(g for g in m.groups() if g))
    return "part"


def split_files(files, language, rng, max_lines=100, min_lines=40):
    """All typed files of a project, long ones split into parts of at most max_lines."""
    out = []
    for rel, text in files:
        if language == "python" and rel.endswith(".py"):
            out += split_python(rel, text, rng, max_lines, min_lines)
        elif language == "go" and rel.endswith(".go"):
            out += split_go(rel, text, rng, max_lines, min_lines)
        else:
            out.append((rel, text))
    return out
