#!/usr/bin/env bash
# Install claude-dialect into ~/.claude: skill, prompt hook, session-start check, CLAUDE.md block.
# Safe to rerun. Backs up settings.json and CLAUDE.md before changing them.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
C="$HOME/.claude"
TS="$(date +%Y%m%d-%H%M%S)"
command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }
command -v claude >/dev/null || echo "note: 'claude' CLI not on PATH; install Claude Code to use this"
mkdir -p "$C/skills" "$C/hooks" "$C/bin"

if [ -d "$C/skills/optimise-prompt" ] && ! diff -rq "$SRC/skills/optimise-prompt" "$C/skills/optimise-prompt" >/dev/null 2>&1; then
  mv "$C/skills/optimise-prompt" "$C/skills/optimise-prompt.bak-$TS"
  echo "existing skill moved to skills/optimise-prompt.bak-$TS"
fi
rm -rf "$C/skills/optimise-prompt"
cp -r "$SRC/skills/optimise-prompt" "$C/skills/optimise-prompt"
install -m 755 "$SRC/hooks/claude-dialect-route.sh" "$C/hooks/claude-dialect-route.sh"
install -m 755 "$SRC/bin/claude-dialect-check.py" "$C/bin/claude-dialect-check.py"

[ -f "$C/settings.json" ] && cp "$C/settings.json" "$C/settings.json.bak-$TS"
[ -f "$C/CLAUDE.md" ] && cp "$C/CLAUDE.md" "$C/CLAUDE.md.bak-$TS"

python3 - "$C" "$SRC/CLAUDE.snippet.md" <<'PY'
import json, pathlib, re, sys
c = pathlib.Path(sys.argv[1]); snippet = pathlib.Path(sys.argv[2]).read_text().strip()
sp = c / "settings.json"
s = json.loads(sp.read_text()) if sp.exists() else {}
hooks = s.setdefault("hooks", {})
want = {
    "UserPromptSubmit": {"type": "command", "command": "bash ~/.claude/hooks/claude-dialect-route.sh", "timeout": 5},
    "SessionStart": {"type": "command", "command": "python3 ~/.claude/bin/claude-dialect-check.py || true", "timeout": 5},
}
for event, h in want.items():
    groups = hooks.setdefault(event, [])
    if not any(x.get("command") == h["command"] for g in groups for x in g.get("hooks", [])):
        groups.append({"hooks": [h]})
sp.write_text(json.dumps(s, indent=2) + "\n")
md = c / "CLAUDE.md"
text = md.read_text() if md.exists() else ""
pat = re.compile(r"<!-- claude-dialect:start -->.*?<!-- claude-dialect:end -->", re.S)
text = pat.sub(snippet, text) if pat.search(text) else (text.rstrip() + "\n\n" + snippet + "\n").lstrip()
md.write_text(text)
PY

if python3 "$C/bin/claude-dialect-check.py"; then
  echo "claude-dialect installed. Start a new Claude Code session to use it."
  echo "Prove it: python3 $SRC/tests/run.py   (12 routing prompts, dry run)"
else
  echo "install finished but the check reported problems (see above)"; exit 1
fi
