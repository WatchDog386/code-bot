"""Project generator: the bot comes up with a new, complete project every time.

    generate("hotel", "go")  ->  {"name": "hotel-api", "files": [...], "scaffold": [...], "steps": [...]}

14 business domains x 3 languages (Python service, Go API, TypeScript kit). Records are
added to the domain until every typed file is at least `min_lines` long, so each file the
bot types is a long, real, working source file (with tests that pass).

`files` are typed by the bot; `scaffold` files (go.mod, package.json, README...) are put in
place instantly; `steps` are what the bot runs in the terminal afterwards.

    python -m codebot.gen --out projects --count 6      # write projects to disk
"""

import random

from . import go_gen, python_gen, ts_gen
from .schema import DOMAINS, load_domain, pool_entities

LANGUAGES = {
    "python": (python_gen, "service"),
    "go": (go_gen, "api"),
    "typescript": (ts_gen, "kit"),
}
MIN_LINES = 1000


def combos():
    return [(d, l) for d in sorted(DOMAINS) for l in sorted(LANGUAGES)]


def generate(domain=None, language=None, seed=None, min_lines=MIN_LINES):
    rng = random.Random(seed)
    key = domain or rng.choice(sorted(DOMAINS))
    lang = language or rng.choice(sorted(LANGUAGES))
    module, suffix = LANGUAGES[lang]
    d = load_domain(key)
    name = f"{key}-{suffix}"
    pool = pool_entities(d.entities[0], {e.name for e in d.entities})
    rng.shuffle(pool)
    while True:
        files, scaffold, steps = module.render(d, name)
        shortest = min(text.count("\n") for _, text in files)
        if shortest >= min_lines or not pool:
            break
        d.entities.append(pool.pop())
    return {"name": name, "domain": key, "language": lang, "title": d.title,
            "records": [e.name for e in d.entities],
            "files": files, "scaffold": scaffold, "steps": steps}


def generated_cycle(seed=None, only=None):
    """Yield new projects forever, going through every domain/language pair before
    repeating one. `only` = a list of languages to stick to."""
    rng = random.Random(seed)
    last = None
    while True:
        order = [c for c in combos() if not only or c[1] in only]
        rng.shuffle(order)
        if last and order and order[0] == last:
            order.append(order.pop(0))
        for key, lang in order:
            last = (key, lang)
            yield generate(key, lang, seed=rng.random())


def write(project, root):
    """Write a generated project to `root/<name>` (typed files listed in .codebot-order)."""
    import os
    base = os.path.join(root, project["name"])
    for rel, text in project["files"] + project["scaffold"]:
        path = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    with open(os.path.join(base, ".codebot-order"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(rel for rel, _ in project["files"]) + "\n")
    lines = ["# typed into VS Code's terminal by the bot after the project is written"]
    for step in project["steps"]:
        prefix = "serve: " if step["serve"] else ""
        wait = f"   # wait {step['wait']}" if step["wait"] else ""
        lines.append(prefix + step["cmd"] + wait)
        if step["open"]:
            lines.append("open: " + step["open"])
    with open(os.path.join(base, ".codebot-run"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return base


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Write generated projects to disk.")
    p.add_argument("--out", default="projects")
    p.add_argument("--count", type=int, default=6)
    p.add_argument("--domain", action="append", help="business domain (repeatable)")
    p.add_argument("--language", action="append", choices=sorted(LANGUAGES))
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args(argv)
    pairs = [(d, l) for d, l in combos()
             if (not args.domain or d in args.domain) and (not args.language or l in args.language)]
    random.Random(args.seed).shuffle(pairs)
    for key, lang in pairs[:args.count]:
        project = generate(key, lang, seed=args.seed)
        path = write(project, args.out)
        sizes = [t.count("\n") for _, t in project["files"]]
        print(f"{path}: {len(sizes)} typed files, {min(sizes)}-{max(sizes)} lines each")
