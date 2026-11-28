"""Project generator: the bot comes up with a new, complete project every time.

    generate("hotel", "go")  ->  {"name": "hotel-api", "files": [...], "scaffold": [...], "steps": [...]}

14 business domains x 3 languages (Python service, Go API, TypeScript kit). Projects are kept
small on purpose: each one uses only the domain's root record type, so every typed file stays
short (well under `max_lines`) and the bot finishes one file and moves on to the next quickly
instead of grinding through a thousand-line file. The result is still real, working code whose
tests pass.

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
MAX_LINES = 300   # hard ceiling; a root-only project lands around 140-275 lines per file


def combos():
    return [(d, l) for d in sorted(DOMAINS) for l in sorted(LANGUAGES)]


def generate(domain=None, language=None, seed=None, max_lines=MAX_LINES):
    rng = random.Random(seed)
    key = domain or rng.choice(sorted(DOMAINS))
    lang = language or rng.choice(sorted(LANGUAGES))
    module, suffix = LANGUAGES[lang]
    d = load_domain(key)
    # Keep just the root record type, so the files stay small and the bot creates several of
    # them quickly. Extra pool records are only added while every file still fits `max_lines`.
    d.entities = d.entities[:1]
    pool = pool_entities(d.entities[0], {e.name for e in d.entities})
    rng.shuffle(pool)
    name = f"{key}-{suffix}"
    files, scaffold, steps = module.render(d, name)
    while pool:
        trial = load_domain(key)
        trial.entities = d.entities + [pool[-1]]
        try:
            trial_files, trial_scaffold, trial_steps = module.render(trial, name)
        except (StopIteration, KeyError):
            break
        if max(t.count("\n") for _, t in trial_files) > max_lines:
            break
        d.entities = trial.entities
        files, scaffold, steps = trial_files, trial_scaffold, trial_steps
        pool.pop()
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
