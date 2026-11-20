"""Shared guard: stop the tests early if the claude-dialect prompt hook is not active.

Without the hook, Claude invents its own classes and the tests report nonsense
(for example 3/12). This runs every UserPromptSubmit hook in ~/.claude/settings.json
and looks for the claude-dialect text in its output.
"""
import json
import pathlib
import subprocess
import sys


def require_hook():
    sp = pathlib.Path.home() / ".claude" / "settings.json"
    try:
        groups = json.loads(sp.read_text()).get("hooks", {}).get("UserPromptSubmit", [])
    except (OSError, ValueError):
        groups = []
    for g in groups:
        for h in g.get("hooks", []):
            cmd = h.get("command", "")
            try:
                out = subprocess.run(cmd, shell=True, input='{"prompt":"test"}', capture_output=True,
                                     text=True, timeout=10).stdout
            except (OSError, subprocess.TimeoutExpired):
                continue
            if "claude-dialect:" in out:
                return
    sys.exit("claude-dialect's prompt hook is not active, so this test would measure plain Claude.\n"
             "Run ./install.sh from a normal terminal (not inside Claude Code), start a new session, then retry.")
