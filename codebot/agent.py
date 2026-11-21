"""The AI agent: an LLM decides, the bot does it on screen.

    task ("build a todo API with tests")
      -> the model plans and calls tools one by one
      -> every tool is carried out visibly: files typed in VS Code, commands typed in VS Code's
         terminal (their output is read back), the app opened next to the code, spreadsheets
         typed into WPS / Excel
      -> results go back to the model, which fixes problems and carries on until `finish`.

`Actions` is the interface the engine implements (VSCodeActions in engine.py); a fake one
is used in tests.
"""

import json
import re

from .llm import LLMError

MAX_STEPS = 40
MAX_RESULT = 6000

TOOLS = [
    {"name": "list_files", "description": "List files and folders in the project (recursive, max 200).",
     "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Folder, relative to the project. Default '.'"}}}},
    {"name": "read_file", "description": "Read a text file from the project.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Create or overwrite a file with the full content. The user watches it being typed in VS Code, so write complete, working files.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace an exact piece of text in a file (old must occur exactly once). Use for small fixes.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}}, "required": ["path", "old", "new"]}},
    {"name": "run_command", "description": "Run a shell command in the project folder in VS Code's terminal and get its output and exit code. For installs, builds, tests, scripts. Not for servers that keep running (use start_server).",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout": {"type": "integer", "description": "Seconds to wait, default 120"}}, "required": ["command"]}},
    {"name": "start_server", "description": "Start a long-running app/server in its own VS Code terminal, wait until the url answers, and show it in VS Code's browser next to the code.",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "url": {"type": "string", "description": "e.g. http://127.0.0.1:8000"}}, "required": ["command", "url"]}},
    {"name": "open_browser", "description": "Show a URL in VS Code's browser next to the code.",
     "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "spreadsheet", "description": "Create an .xlsx workbook and type it into WPS Office / Excel cell by cell. rows = list of rows, each a list of cell texts; formulas start with '=' (use commas, A1 references).",
     "parameters": {"type": "object", "properties": {"file": {"type": "string", "description": "e.g. budget.xlsx"},
                    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}}, "required": ["file", "rows"]}},
    {"name": "finish", "description": "Call when the task is done (or can't be done). Give a short summary for the user.",
     "parameters": {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}},
]


def tool_specs():
    return [{"type": "function", "function": t} for t in TOOLS]


def system_prompt(env):
    return f"""You are Invotech 360, an autonomous software agent working on the user's computer.
You control VS Code (and WPS Office / Excel for spreadsheets) through tools; the user watches you work.

Project folder: {env['project_dir']}
Operating system: {env['os']}; terminal: {env['shell']}; tools available: {env['toolchain']}.

How to work:
- First reply with a short plan (2-6 numbered steps), then do it with tools, one step at a time.
- Write complete, working files with write_file (no placeholders, no "..."). Keep each file under ~250 lines;
  split bigger programs into modules. Prefer the standard library / few dependencies.
- After writing code, run it or its tests with run_command, read the output, fix problems with edit_file or
  write_file, and run again until it works.
- For web apps/APIs use start_server (it opens the app next to the code), then check it.
- For spreadsheet / Excel / WPS work use the spreadsheet tool with real formulas.
- Paths are relative to the project folder. Never touch files outside it.
- When done, call finish with a short summary of what you built and how to use it.
"""


def _short(value, n=120):
    text = value if isinstance(value, str) else json.dumps(value)
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def describe(name, args):
    """One line for the dashboard's agent timeline."""
    if name in ("write_file", "read_file", "edit_file"):
        verb = {"write_file": "Writing", "read_file": "Reading", "edit_file": "Editing"}[name]
        return f"{verb} {args.get('path', '?')}"
    if name == "run_command":
        return f"$ {args.get('command', '')}"
    if name == "start_server":
        return f"Starting the app: {args.get('command', '')}"
    if name == "open_browser":
        return f"Opening {args.get('url', '')}"
    if name == "spreadsheet":
        return f"Filling {args.get('file', 'workbook')} ({len(args.get('rows') or [])} rows)"
    if name == "list_files":
        return f"Looking at {args.get('path') or 'the project'}"
    return name


class Agent:
    def __init__(self, llm, actions, emit, model=None, max_steps=MAX_STEPS):
        self.llm = llm
        self.actions = actions
        self.emit = emit                 # emit(kind, title, detail)
        self.model = model
        self.max_steps = max_steps
        self.messages = []
        self.summary = ""

    def _trim(self):
        """Keep the conversation within the model's context: shorten old tool results."""
        total = sum(len(json.dumps(m)) for m in self.messages)
        for m in self.messages[2:-6]:
            if total < 90_000:
                break
            if m.get("role") == "tool" and len(m.get("content", "")) > 300:
                total -= len(m["content"]) - 60
                m["content"] = m["content"][:60] + " …(trimmed)"

    def run(self, task, context=""):
        env = self.actions.environment()
        self.messages = [
            {"role": "system", "content": system_prompt(env)},
            {"role": "user", "content": task + (f"\n\nContext:\n{context}" if context else "")},
        ]
        self.emit("plan", "Agent task", task)
        bad_calls = 0
        for step in range(1, self.max_steps + 1):
            if self.actions.should_stop():
                self.emit("stop", "Agent stopped", "")
                return "stopped"
            self._trim()
            self.actions.set_status("thinking", f"step {step}")
            try:
                msg = self.llm.chat(self.messages, tools=tool_specs(), model=self.model)
            except LLMError as exc:
                text = str(exc)
                if "tool" in text.lower() and bad_calls < 3:      # the model produced a broken tool call
                    bad_calls += 1
                    self.messages.append({"role": "user", "content":
                                          "Your last tool call was not valid JSON for the tool's parameters. Try again."})
                    continue
                self.emit("warn", "AI problem", text)
                return "error"
            calls = msg.get("tool_calls") or []
            content = (msg.get("content") or "").strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()
            self.messages.append({"role": "assistant", "content": content or None,
                                  **({"tool_calls": calls} if calls else {})})
            if content:
                self.emit("say", "Agent", content)
            if not calls:
                if step == 1 or not content:
                    self.messages.append({"role": "user", "content": "Go ahead and do it now with the tools."})
                    continue
                self.summary = content
                self.emit("done", "Agent finished", content)
                return "done"
            for call in calls:
                fn = call.get("function", {})
                name = fn.get("name", "")
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                    if not isinstance(args, dict):
                        raise ValueError("arguments must be an object")
                except ValueError as exc:
                    result = f"Error: invalid arguments ({exc})"
                    args = {}
                else:
                    if name == "finish":
                        self.summary = args.get("summary", "")
                        self.messages.append({"role": "tool", "tool_call_id": call.get("id", ""), "content": "ok"})
                        self.emit("done", "Agent finished", self.summary)
                        return "done"
                    self.emit("tool", describe(name, args), _short(args.get("content") or args.get("new") or "", 160)
                              if name in ("write_file", "edit_file") else "")
                    self.actions.set_status("working", describe(name, args))
                    try:
                        result = self.actions.run(name, args)
                    except Exception as exc:  # noqa: BLE001 - report to the model, let it recover
                        result = f"Error: {exc}"
                if self.actions.should_stop():
                    return "stopped"
                result = str(result)
                if len(result) > MAX_RESULT:
                    result = result[:MAX_RESULT // 2] + "\n…(cut)…\n" + result[-MAX_RESULT // 2:]
                self.emit("result", describe(name, args), _short(result, 300))
                self.messages.append({"role": "tool", "tool_call_id": call.get("id", ""), "content": result})
        self.emit("warn", "Agent stopped", f"reached the {self.max_steps}-step limit")
        return "limit"
