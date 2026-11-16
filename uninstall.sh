#!/usr/bin/env bash
# Remove claude-dialect from ~/.claude. Backs up settings.json and CLAUDE.md first.
set -euo pipefail
C="$HOME/.claude"; TS="$(date +%Y%m%d-%H%M%S)"
rm -rf "$C/skills/optimise-prompt"
rm -f "$C/hooks/claude-dialect-route.sh" "$C/bin/claude-dialect-check.py"
[ -f "$C/settings.json" ] && cp "$C/settings.json" "$C/settings.json.bak-$TS"
[ -f "$C/CLAUDE.md" ] && cp "$C/CLAUDE.md" "$C/CLAUDE.md.bak-$TS"
python3 - "$C" <<'PY'
import json, pathlib, re, sys
c = pathlib.Path(sys.argv[1]); sp = c / "settings.json"
if sp.exists():
    s = json.loads(sp.read_text())
    for event, groups in list(s.get("hooks", {}).items()):
        for g in groups:
            g["hooks"] = [h for h in g.get("hooks", []) if "claude-dialect" not in h.get("command", "")]
        s["hooks"][event] = [g for g in groups if g.get("hooks")]
        if not s["hooks"][event]:
            del s["hooks"][event]
    sp.write_text(json.dumps(s, indent=2) + "\n")
md = c / "CLAUDE.md"
if md.exists():
    md.write_text(re.sub(r"\n*<!-- claude-dialect:start -->.*?<!-- claude-dialect:end -->\n?", "\n", md.read_text(), flags=re.S))
PY
echo "claude-dialect removed. Backups: settings.json.bak-$TS, CLAUDE.md.bak-$TS"
