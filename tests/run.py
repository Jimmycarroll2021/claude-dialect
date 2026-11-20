#!/usr/bin/env python3
"""Routing test: does each sample prompt get the expected class?

Runs every prompt in cases.json through `claude -p` as a dry run (nothing is
executed) and checks the class in the Route line it returns.
Usage: python3 tests/run.py [label]   -> writes tests/result-<label>.json
"""

import concurrent.futures as cf
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _installed import require_hook  # noqa: E402

require_hook()

here = pathlib.Path(__file__).parent
label = sys.argv[1] if len(sys.argv) > 1 else "run"
cases = json.loads((here / "cases.json").read_text())
cwd = tempfile.mkdtemp(prefix="claude-dialect-routing-")
SUFFIX = (
    "\n\n(Routing dry run: do not do the work and ask nothing. "
    "Reply with only one line: Route: <alias> · <effort> · class <N> <short-name>)"
)


def one(c):
    try:
        out = subprocess.run(
            ["claude", "-p", c["prompt"] + SUFFIX, "--model", "sonnet"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=240,
        ).stdout
    except subprocess.TimeoutExpired:
        out = "TIMEOUT"
    m = re.search(r"class\s*(\d)", out)
    got = int(m.group(1)) if m else None
    return {**c, "got": got, "ok": got == c["expect"], "raw": out.strip()[-200:]}


with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, cases))
(here / f"result-{label}.json").write_text(json.dumps(res, indent=1))
for r in res:
    last = r["raw"].splitlines()[-1] if r["raw"] else ""
    print(
        f"{r['id']} expect {r['expect']} got {r['got']} {'OK' if r['ok'] else 'MISS'} | {last}"
    )
n = sum(r["ok"] for r in res)
print(f"{label}: {n}/{len(res)}")
sys.exit(0 if n == len(res) else 1)
