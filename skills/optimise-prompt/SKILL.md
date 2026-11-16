---
name: optimise-prompt
description: Use by default on every user request (a prompt hook applies it). Also when the user says "optimise my prompt", "/optimise-prompt", "which model should I use" or "route this", or asks which Claude model or effort level suits a task.
argument-hint: "[--show] [--model <alias>] <your query>"
---

# Optimise Prompt

Understand the request, size it, route it to the Claude model and effort that fit, rewrite it in that model's dialect, then hand it off or do it here.

Raw input: $ARGUMENTS (applied by default: the user's message)

## Modes

- **Sub-agent:** if this session was spawned with a brief, skip routing and do the work in the brief.
- **Default** (applied by the hook): quiet. Show one line `Route: <alias> · <effort> · class N <short-name>` only when an agent is spawned. Class 6 chat is answered directly.
- **Shown** (`/optimise-prompt`, `--show`, or the user asks for routing advice): show the full Route block in step 7, run nothing.

## Workflow

1. **Interpret.** Settle silently: outcome, target, constraints, deliverable, done-when. Resolve "this/that" from context. Keep paths, IDs, commands, numbers and quoted wording verbatim. Honour the verb: fix/build/create → do it; why → diagnose; how → plan; draft → text; review → findings.

2. **Ask or stop early.** Ask one question and stop only when a gap would change the outcome and cannot be discovered, or the action is production-impacting (deploy, publish, billing, production data, destructive deletes) without approval in this conversation. With `--show`, put a `[placeholder]` instead of asking.

3. **Route.** Read `references/routing.md`. Classify by difficulty, not by the tools needed; the hardest part decides. Take the class's model and starting effort. "Be thorough" / "double check" raise effort one level (and leave the prompt). `--model <alias>` overrides the model.

4. **Pick the agent type** per `routing.md` "Agent type". Never `fork` when the route differs from the session's model (a fork ignores `model`).

5. **Load guidance:** `references/<model id without "claude-">.md`, plus `general.md` in shown mode. A model file missing or `last_verified` over 30 days old: refresh it per `general.md` "Live fetch" and say so.

6. **Rewrite.** Keep intent and literals; a short query gets a short rewrite.
   1. A testable done-when, from the user's words only.
   2. Action verbs when action is wanted; plans and suggestions stay so.
   3. Spell out what the user asked for; add nothing.
   4. Colleague test: add missing context from the conversation; keep each constraint's reason.
   5. Plain, positive wording; no capitalised emphasis.
   6. No requests to write out reasoning, no `<thinking>` tags, no prefill.
   7. XML tags only for distinct parts; long documents first, query last.
   8. Apply the model file's transforms last; the model file wins.

7. **Show the result.** Default: the Route line, only when spawning. Shown mode:

   ````
   Route: <alias> (<model id>) · effort <level> · class N <short-name>

   ```
   <rewritten prompt>
   ```

   - <why this route, which agent, what changed>
   ````

   Stop here for `--show` or advice-only requests.

8. **Hand off or do it here.**
   - Class 6 chat, or the routed model is the session's own model: do the work in this session.
   - Any other route: spawn the agent from step 4 with `model: <alias>`, `effort: <level>` and the rewritten prompt, whatever the size of the task. Check what comes back before relying on it, then reply outcome first.

## Example

Session on Sonnet: "the checkout tests fail randomly on CI, find out why and fix it. be really thorough". Unknown root cause → class 4 complex → Opus at medium, raised to high for "be thorough". Opus differs from the session's Sonnet, so it is spawned:

```
Route: opus · high · class 4 complex
```

The brief sent to Opus: "Find and fix the cause of the intermittent checkout test failure on CI. Done means: the cause is shown with evidence, the fix addresses it, and the test passes on repeated runs. Change only what the fix needs." The "double-check" style wording is dropped because Opus verifies on its own.
