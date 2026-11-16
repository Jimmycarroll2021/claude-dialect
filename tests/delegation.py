#!/usr/bin/env python3
"""Delegation test: do real tasks get handed to the routed model?

Builds three small throwaway projects in a temp folder, runs a real task in
each with `claude -p --model sonnet`, and reads the session log for Agent
spawns. Expected with a Sonnet session:
  t1 classify 40 tickets      -> spawns Haiku
  t2 small script with a test -> stays in the Sonnet session (no spawn)
  t4 flaky test, unknown cause -> spawns Opus
Tools are scoped with --allowedTools; there is no permission bypass.
This runs real work, so it costs a few minutes and some tokens.
"""

import concurrent.futures as cf
import json
import pathlib
import random
import subprocess
import sys
import tempfile

root = pathlib.Path(tempfile.mkdtemp(prefix="claude-dialect-deleg-"))
TOOLS = "Agent,Task,Read,Write,Edit,Glob,Grep,Bash(python3:*),Bash(pytest:*),Bash(ls:*)"


def fixtures():
    random.seed(1)
    kinds = {
        "billing": [
            "I was charged twice this month",
            "refund still not received",
            "invoice shows wrong tax",
        ],
        "login": [
            "cannot reset my password",
            "2FA code never arrives",
            "locked out after update",
        ],
        "shipping": [
            "parcel stuck in transit for a week",
            "wrong address on label",
            "delivery marked done but nothing came",
        ],
        "product": [
            "zip broke on first use",
            "size chart is wrong for the jacket",
            "colour faded after one wash",
        ],
    }
    t = root / "t1" / "tickets"
    t.mkdir(parents=True)
    for i in range(40):
        k = random.choice(list(kinds))
        (t / f"t{i:02}.txt").write_text(
            f"{random.choice(kinds[k])}. order #{1000 + i}\n"
        )
    d = root / "t2" / "data"
    d.mkdir(parents=True)
    (d / "rides.csv").write_text(
        "date,rider,km\n2026-11-01,amy,42\n2026-11-02,bob,18\n2026-11-02,amy,25\n"
    )
    c = root / "t4"
    c.mkdir()
    (c / "cache.py").write_text(
        "import threading, time, random\n"
        "class Counter:\n"
        "    def __init__(self): self.n = 0; self.lock = threading.Lock()\n"
        "    def incr(self):\n"
        "        v = self.n\n"
        "        time.sleep(random.random() / 10000)\n"
        "        self.n = v + 1\n"
    )
    (c / "test_cache.py").write_text(
        "import threading\nfrom cache import Counter\n"
        "def test_parallel_increments():\n"
        "    c = Counter()\n"
        "    ts = [threading.Thread(target=lambda: [c.incr() for _ in range(200)]) for _ in range(8)]\n"
        "    [t.start() for t in ts]; [t.join() for t in ts]\n"
        "    assert c.n == 1600\n"
    )


cases = [
    (
        "t1",
        "haiku",
        "Classify each of the 40 support tickets in tickets/ as billing, login, shipping or product and write tickets.csv with columns file,category.",
    ),
    (
        "t2",
        None,
        "Write tools/summarise.py that reads data/rides.csv and prints total km per rider, sorted descending, plus a pytest test for it, and run the test.",
    ),
    (
        "t4",
        "opus",
        "test_cache.py fails intermittently. Find the root cause and fix it.",
    ),
]


def events(text):
    for line in text.splitlines():
        try:
            yield json.loads(line)
        except ValueError:
            pass


def run(c):
    d, want, prompt = c
    p = subprocess.run(
        [
            "claude",
            "-p",
            prompt,
            "--model",
            "sonnet",
            "--output-format",
            "stream-json",
            "--verbose",
            "--permission-mode",
            "acceptEdits",
            "--allowedTools",
            TOOLS,
        ],
        cwd=root / d,
        capture_output=True,
        text=True,
        timeout=900,
    )
    spawns, tail = [], p.stderr[-200:]
    for ev in events(p.stdout):
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            for b in ev["message"].get("content", []):
                if b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                    i = b["input"]
                    spawns.append(
                        (i.get("subagent_type"), i.get("model"), i.get("effort"))
                    )
        if ev.get("type") == "result":
            tail = ev.get("result", "")[:200]
    return d, want, spawns, tail


fixtures()
ok_all = True
with cf.ThreadPoolExecutor(3) as ex:
    for d, want, spawns, tail in ex.map(run, cases):
        ok = (not spawns) if want is None else any(s[1] == want for s in spawns)
        ok_all &= ok
        print(
            f"{d} want {want or 'no hand-off'}: {'OK' if ok else 'MISS'} spawns={spawns}\n   -> {tail!r}"
        )
print(f"fixtures in {root}")
sys.exit(0 if ok_all else 1)
