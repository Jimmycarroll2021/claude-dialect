---
name: optimise-prompt
description: Use by default on every user request (a prompt hook applies it). Also when the user says "optimise my prompt", "/optimise-prompt", "which model should I use" or "route this", or asks which Claude model or effort level suits a task.
argument-hint: "[--show] [--model <alias>] <your query>"
---

# Optimise Prompt

Understand the request and size it. Do it here by default at the effort that fits; hand it off only when a hand-off clearly pays, and then brief the agent in its model's dialect.

Raw input: $ARGUMENTS (applied by default: the user's message)

## Modes

- **Sub-agent:** if this session was spawned with a brief, skip routing and do the work in the brief.
- **Default** (applied by the hook): quiet. Work here. Show one line `Route: <alias> · <effort> · class N <short-name>` only when an agent is spawned.
- **Shown** (`/optimise-prompt`, `--show`, or the user asks for routing advice): show the full Route block in step 7, run nothing.

## Workflow

1. **Interpret.** Settle silently: outcome, target, constraints, deliverable, done-when. Resolve "this/that" from context. Keep paths, IDs, commands, numbers and quoted wording verbatim. Honour the verb: fix/build/create → do it; why → diagnose; how → plan; draft → text; review → findings.

2. **Ask or stop early.** Ask one question and stop only when a gap would change the outcome and cannot be discovered, or the action is production-impacting (deploy, publish, billing, production data, destructive deletes) without approval in this conversation. With `--show`, put a `[placeholder]` instead of asking.

3. **Size.** Read `references/routing.md`. Classify by difficulty, not by the tools needed; the hardest part decides. The class sets the effort here, and the model only if you hand off. "Be thorough" / "double check" raise effort one level (and leave the prompt). `--model <alias>` overrides the model.

4. **Pick the agent type** per `routing.md` "Agent type". Never `fork` when the route differs from the session's model (a fork ignores `model`).

5. **Load guidance:** `references/<model id without "claude-">.md`, plus `general.md` in shown mode. A model file missing or `last_verified` over 30 days old: refresh it per `general.md` "Live fetch" and say so.

6. **Brief (hand-offs only).** The user's request goes in word for word; a summary loses nuance. Below it, a short facts block from this conversation (the agent starts with none): paths, decisions, constraints, done-when. Then only these additions:
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

8. **Do it here, or hand off.**
   - Default: do the work in this session at the class's effort. Raise effort before changing model.
   - Hand off only for: bulk or context-flooding work (many files or items, long logs, wide searches) to the table's model; class 5 long-horizon work to Fable; independent parallel parts; an independent check before something goes public; or work that already fell short here at higher effort, to the next model up. Spawn the step 4 agent with `model: <alias>`, `effort: <level>` and the step 6 brief.
   - A follow-up on an agent's work continues that agent with SendMessage, keeping its context.
   - Check what comes back before relying on it, then reply outcome first.

## Example

Session on Sonnet: "the checkout tests fail randomly on CI, find out why and fix it. be really thorough". Class 4 complex, no hand-off trigger, so Sonnet does it here at high effort ("be thorough" = +1). Only if that falls short does it go to Opus.

Session on Sonnet: "research the Australian rental market over the last 10 years and produce a finished 20-page report". Class 5, so it is handed to Fable:

```
Route: fable · high · class 5 long-horizon
```

The brief is the request word for word, a facts block (where to save the report, sources already named in the conversation), and Fable's additions: a "finishing work" line and a low-context report style.
