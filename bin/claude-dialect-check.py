#!/usr/bin/env python3
"""Check the optimise-prompt skill's guidance is wired and fresh.
Exit 0 silent when OK; prints one line per problem otherwise (SessionStart shows it)."""
import datetime, json, pathlib, re, sys
home = pathlib.Path.home() / ".claude"
ref = home / "skills/optimise-prompt/references"
max_age = int(sys.argv[1]) if len(sys.argv) > 1 else 30
problems = []
if not (ref / "routing.md").exists():
    print("[claude-dialect] skill not installed: rerun install.sh"); sys.exit(1)
routing = (ref / "routing.md").read_text()
ids = re.findall(r"^\| `\w+` \| `(claude-[a-z0-9-]+)` \|", routing, re.M)
if len(ids) != 4:
    problems.append(f"routing.md alias table has {len(ids)} model rows, expected 4")
files = [ref / "routing.md"] + [ref / f"{i.removeprefix('claude-')}.md" for i in ids]
today = datetime.date.today()
for f in files:
    if not f.exists():
        problems.append(f"missing guidance file {f.name}")
        continue
    m = re.search(r"last_verified: (\d{4}-\d{2}-\d{2})", f.read_text())
    if not m:
        problems.append(f"{f.name} has no last_verified")
    elif (today - datetime.date.fromisoformat(m.group(1))).days > max_age:
        problems.append(f"{f.name} last verified {m.group(1)}, over {max_age} days: refresh from the Claude prompting docs")
sp = home / "settings.json"
hooks = json.loads(sp.read_text()).get("hooks", {}) if sp.exists() else {}
if "claude-dialect-route" not in json.dumps(hooks.get("UserPromptSubmit", [])):
    problems.append("UserPromptSubmit hook claude-dialect-route is not registered: rerun install.sh")
for p in problems:
    print(f"[claude-dialect] {p}")
sys.exit(1 if problems else 0)
