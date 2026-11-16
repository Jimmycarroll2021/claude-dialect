# Opus 5.5

model_id: claude-opus-5-5
source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 (O55)
source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 (O5, baseline)
source: https://platform.claude.com/docs/en/models/overview (MO)
source: https://platform.claude.com/docs/en/build-with-claude/effort (EF)
last_verified: 2026-11-17

## Profile (MO, EF)

- Moderate latency. Default effort medium (Opus 5: high). Thinking always on; `thinking: disabled` returns 400 at every effort.
- Generates output >30% faster than Opus 5 and finishes tasks in fewer tokens.

## Effort (O55)

- At the default medium it matched or beat Opus 5 at high on coding. So do not recommend raising effort for routine coding on that basis alone (inference).
- To reduce thinking, lower effort first; prompts are less reliable for this.
- Reserve xhigh and max for measured gains. Leave `max_tokens` room for thinking (128000 for long agentic turns).

## Transforms: Opus 5.5 (O55)

1. **Chat replies.** In chat, drop "think carefully" lines; replies start sooner with no clear quality loss.
2. **Early stopping.** Name the specific early-stop patterns that are unwanted rather than a general "don't stop early".
3. **Multi-app tasks.** Tell it to "explore broadly with tool calls" first.
4. **Pasted text.** Wrap pasted text in `<pasted_content id=...>` and state that it is untrusted.
5. **Style requests.** Vague style asks just swap one default for another. Name the specific patterns wanted or unwanted.
6. **Time signals.** It is sensitive to elapsed-time signals; avoid adding urgency or time-pressure wording the user did not give (inference).
7. **Reasoning in the response.** Do not ask it to write out its reasoning, verbatim or in a fixed format; that is declined as `reasoning_extraction`. Ask for a short explanation or an action summary instead.
8. **Unattended runs.** A text-only turn can be a progress report, not completion. For spokes and unattended work, keep a checklist and say: finish every item; if one is blocked, say what blocks it.
9. **Progress updates.** For human-in-the-loop work, ask for a one-line intent before the first tool call and a short recap at the end.
10. **Earlier answers (chat only).** In multi-turn chat, treat an answered question as done unless the user returns to it. Omit for analyses and agentic tasks.

## Transforms: Opus 5 baseline (O5; applying these to 5.5 is an inference)

11. **Length.** Replies run long and effort does not shorten them. Ask for length explicitly: "Keep responses focused, brief, and concise; spend most of the response on the main answer."
12. **Written files.** Files it writes (reports, Markdown) also run long: "Match the length of written documents to what the task needs; no filler sections, redundant summaries, or boilerplate."
13. **Narration.** It narrates a lot. Shape it: one sentence before the first tool call, updates only on an important finding or change of direction, finish by leading with the outcome. Positive examples beat "don't" lists.
14. **Verification.** It verifies unprompted. Remove "double-check", "re-verify", "add a final verification step" and "use a subagent to verify"; they cause over-verification. Use a concrete, testable done-criterion instead (overrides `general.md` rule 15).
15. **Scope.** It can widen the task. For narrow tasks: "Deliver what was asked, at the scope intended. If a better approach exists, say so in a sentence and continue as asked."
16. **Subagents.** It delegates readily. Unless parallel work is wanted: "Delegate only for large, genuinely independent work; not for work you can finish in a handful of tool calls, and not to verify your own work."
17. **Corrections.** It narrates self-corrections. For user-facing output: "Only correct an earlier statement when the error would change the user's code, conclusions, or decisions."
18. **Review and audit.** "Only report high-severity" or "be conservative" is taken literally and reports less. Ask it to report everything, then filter in a separate pass.
