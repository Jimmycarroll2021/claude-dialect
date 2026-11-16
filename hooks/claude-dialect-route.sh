#!/usr/bin/env bash
# UserPromptSubmit: route every prompt. Full rules: ~/.claude/skills/optimise-prompt (routing.md + model files).
cat >/dev/null
cat <<'TXT'
Route this request with the optimise-prompt skill. Classify by how hard the work is (the hardest part decides), not by the tools it needs:
| class | short-name | what it looks like | alias · starting effort |
| 1 | lookup | find, list, grep, classify, extract fields, map code without changing it | haiku · medium (bulk: low) |
| 2 | everyday | write a function, draft copy, analyse a CSV, routine tool use; scope not fully pinned | sonnet · high |
| 3 | bounded | exact files AND exact change AND a named check are all given; one coherent change | sonnet · medium |
| 4 | complex | unknown root cause, debugging, refactor, architecture, review or audit | opus · medium |
| 5 | long-horizon | hours of research or analysis ending in a finished report, document or deck | fable · high |
| 6 | chat | answerable in chat with no tool call: explanation, quick fact, wording help | this session · current |
Unclear: opus · medium. "Be thorough / double check" = effort +1, not extra words. Falling short: raise effort, then haiku > sonnet > opus > fable.
Then: if the routed model differs from this session's model, hand the work to an agent with that model and effort, whatever its size, prompt rewritten per the skill's references/<model>.md. Same model as this session, or class 6: do it here. Show one line "Route: <alias> · <effort> · class N <short-name>" only when you spawn.
TXT
