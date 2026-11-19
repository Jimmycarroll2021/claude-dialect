#!/usr/bin/env python3
"""Delegation test: work here by default, hand off only when it pays, and get the right answer.

Builds throwaway projects in a temp folder, runs a real task in each with
`claude -p --model sonnet`, reads the session log for Agent spawns, and checks
the actual output where there is a known right answer.
  t0 one-command git status check            -> no hand-off
  t1 classify 200 tickets                    -> tickets.csv >= 98% correct (hand-off optional)
  t2 small script with a test                -> no hand-off
  t4 flaky test, unknown cause               -> no hand-off, and the test then passes 5 runs
  t5 a rule given in an earlier turn, then t1 -> tickets.csv >= 98% correct WITH the rule applied
  t6 a fact given in an earlier turn, then "independent check before publishing"
                                             -> hand-off whose brief holds the request word for
                                                word AND the earlier fact
Tools are scoped with --allowedTools; there is no permission bypass.
This runs real work, so it takes several minutes and uses tokens.
"""

import concurrent.futures as cf
import csv
import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile

root = pathlib.Path(tempfile.mkdtemp(prefix="claude-dialect-deleg-"))
N = 200
TOOLS = ("Agent,Task,SendMessage,Read,Write,Edit,Glob,Grep,"
         "Bash(python3:*),Bash(pytest:*),Bash(ls:*),Bash(git log:*),Bash(git status:*)")
TICKETS = (f"Classify each of the {N} support tickets in tickets/ as billing, login, shipping "
           "or product and write tickets.csv with columns file,category.")
VIP_TURN = ("Before the next task, note this rule for this project: any ticket whose order "
            "number is above 1030 is a VIP ticket and gets the category vip. Just acknowledge it.")
AUD_TURN = ("Before the next task, note this: every figure in stats.md is in AUD, rounded to "
            "whole dollars. Just acknowledge it.")
CHECK = ("I'm about to publish stats.md. Get an independent check that every figure in it "
         "matches data.csv before I publish, and tell me what is wrong.")
truth = {}


def fixtures():
    g = root / "t0"
    g.mkdir()
    (g / "app.py").write_text("print('hi')\n")
    git = ["git", "-c", "user.name=dev", "-c", "user.email=dev@example.com"]
    subprocess.run(["git", "init", "-q"], cwd=g, check=True)
    subprocess.run(["git", "add", "."], cwd=g, check=True)
    subprocess.run(git + ["commit", "-q", "-m", "Add login rate limit"], cwd=g, check=True)

    random.seed(1)
    kinds = {
        "billing": ["I was charged twice this month", "refund still not received", "invoice shows wrong tax", "card declined but money taken"],
        "login": ["cannot reset my password", "2FA code never arrives", "locked out after update", "magic link expired instantly"],
        "shipping": ["parcel stuck in transit for a week", "wrong address on label", "delivery marked done but nothing came", "courier left it in the rain"],
        "product": ["zip broke on first use", "size chart is wrong for the jacket", "colour faded after one wash", "seam split after two rides"],
    }
    t = root / "t1" / "tickets"
    t.mkdir(parents=True)
    for i in range(N):
        k = random.choice(list(kinds))
        name = f"t{i:03}.txt"
        (t / name).write_text(f"{random.choice(kinds[k])}. order #{1000 + i}\n")
        truth[name] = k
    shutil.copytree(root / "t1", root / "t5")

    d = root / "t2" / "data"
    d.mkdir(parents=True)
    (d / "rides.csv").write_text("date,rider,km\n2026-11-01,amy,42\n2026-11-02,bob,18\n2026-11-02,amy,25\n")

    c = root / "t4"
    c.mkdir()
    (c / "cache.py").write_text(
        "import threading, time, random\n"
        "class Counter:\n"
        "    def __init__(self): self.n = 0; self.lock = threading.Lock()\n"
        "    def incr(self):\n"
        "        v = self.n\n"
        "        time.sleep(random.random() / 10000)\n"
        "        self.n = v + 1\n")
    (c / "test_cache.py").write_text(
        "import threading\nfrom cache import Counter\n"
        "def test_parallel_increments():\n"
        "    c = Counter()\n"
        "    ts = [threading.Thread(target=lambda: [c.incr() for _ in range(200)]) for _ in range(8)]\n"
        "    [t.start() for t in ts]; [t.join() for t in ts]\n"
        "    assert c.n == 1600\n")

    s = root / "t6"
    s.mkdir()
    (s / "data.csv").write_text("month,revenue\n2026-08,12000\n2026-09,15500\n2026-10,14250\n")
    (s / "stats.md").write_text("# Q3 stats\n\n- Total revenue: 41,750\n- Best month: September (15,500)\n- Average per month: 13,917\n")


def tickets_score(folder, vip):
    f = root / folder / "tickets.csv"
    if not f.exists():
        return 0.0
    rows = {r.get("file", "").strip().split("/")[-1]: r.get("category", "").strip().lower()
            for r in csv.DictReader(f.open())}
    def want(name):
        return "vip" if vip and int(name[1:4]) + 1000 > 1030 else truth[name]
    return sum(rows.get(n) == want(n) for n in truth) / len(truth)


def flaky_fixed():
    return all(subprocess.run([sys.executable, "-m", "pytest", "-q", "test_cache.py"], cwd=root / "t4",
                              capture_output=True).returncode == 0 for _ in range(5))


# (folder, earlier turn, prompt, spawn rule: False = none allowed / True = required / None = either,
#  texts the brief must contain, outcome check)
cases = [
    ("t0", None, "Has the backend dev pushed a commit here yet? Tell me the latest commit message.", False, [], None),
    ("t1", None, TICKETS, None, [TICKETS], lambda: tickets_score("t1", False) >= 0.98),
    ("t2", None, "Write tools/summarise.py that reads data/rides.csv and prints total km per rider, sorted descending, plus a pytest test for it, and run the test.", False, [], None),
    ("t4", None, "test_cache.py fails intermittently. Find the root cause and fix it.", False, [], flaky_fixed),
    ("t5", VIP_TURN, TICKETS, None, ["1030"], lambda: tickets_score("t5", True) >= 0.98),
    ("t6", AUD_TURN, CHECK, True, [CHECK, "AUD"], None),
]


def events(text):
    for line in text.splitlines():
        try:
            yield json.loads(line)
        except ValueError:
            pass


def claude(cwd, prompt, resume=None):
    cmd = ["claude", "-p", prompt, "--model", "sonnet", "--output-format", "stream-json",
           "--verbose", "--permission-mode", "acceptEdits", "--allowedTools", TOOLS]
    if resume:
        cmd += ["--resume", resume]
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
    return list(events(p.stdout)), p.stderr


def run(c):
    d, earlier, prompt, spawn_rule, must, check = c
    resume = None
    if earlier:
        evs, _ = claude(root / d, earlier)
        resume = next((e.get("session_id") for e in evs if e.get("session_id")), None)
    evs, err = claude(root / d, prompt, resume)
    spawns, tail = [], err[-160:]
    for ev in evs:
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            for b in ev["message"].get("content", []):
                if b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                    i = b["input"]
                    brief = i.get("prompt") or ""
                    spawns.append((i.get("model"), all(m in brief for m in must)))
        if ev.get("type") == "result":
            tail = ev.get("result", "")[:140]
    notes = []
    if spawn_rule is False and spawns:
        notes.append("handed off but should not")
    if spawn_rule is True and not spawns:
        notes.append("no hand-off")
    if spawns and must and not any(ok for _, ok in spawns):
        notes.append("brief missing the request or the earlier fact")
    if check and not check():
        notes.append("wrong result")
    return d, spawns, notes, tail


fixtures()
passed = 0
with cf.ThreadPoolExecutor(6) as ex:
    for d, spawns, notes, tail in ex.map(run, cases):
        passed += not notes
        print(f"{d}: {'OK' if not notes else 'MISS (' + '; '.join(notes) + ')'} spawns={spawns}\n   -> {tail!r}")
print(f"delegation: {passed}/{len(cases)}  (fixtures in {root})")
sys.exit(0 if passed == len(cases) else 1)
