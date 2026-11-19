#!/usr/bin/env bash
# UserPromptSubmit hook (claude-dialect): injects the work-here-by-default rule and the class table.
# Full rules: ~/.claude/skills/optimise-prompt (references/routing.md + one file per model).
cat >/dev/null
cat <<'TXT'
claude-dialect: do this request here, on this session's model, by default. Size it with the table (the hardest part decides) to set effort, and to pick the model only if you hand off:
| class | looks like | model if handed off · effort |
| 1 lookup | find, list, grep, classify, extract | haiku · medium (bulk: low) |
| 2 everyday | write a function, draft copy, analyse a CSV | sonnet · high |
| 3 bounded | exact files + exact change + a named check | sonnet · medium |
| 4 complex | unknown root cause, refactor, architecture, review | opus · medium |
| 5 long-horizon | hours of research ending in a finished document | fable · high |
| 6 chat | answerable with no tool call | never handed off |
Hand off to an agent only when one of these holds:
- bulk or context-flooding work (many files or items, long logs, wide searches): an agent on the table's model;
- class 5 long-horizon work: a Fable agent;
- independent parts that can run in parallel;
- an independent check of something about to go public;
- you already tried it here at higher effort and it fell short: the next model up (haiku > sonnet > opus > fable).
Otherwise raise effort before changing model; "be thorough" = effort +1, not extra words.
When you hand off: the brief is the user's request word for word (never a summary), then a short block of the facts the agent needs from this conversation (paths, decisions, constraints, done-when), then the additions in the skill's references/<model>.md. A follow-up on that agent's work continues it with SendMessage. Check what comes back before relying on it, and show one line "Route: <alias> · <effort> · class N <short-name>".
TXT
