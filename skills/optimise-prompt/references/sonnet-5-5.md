# Sonnet 5.5

model_id: claude-sonnet-5-5
source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5 (S55)
source: https://platform.claude.com/docs/en/models/overview (MO)
source: https://platform.claude.com/docs/en/build-with-claude/effort (EF)
last_verified: 2026-11-17

## Profile (MO)

- Fast. Default effort high.

## Effort (S55)

- high by default; medium for well-specified agentic coding; medium or low for chat.
- At low or medium it may check in with the user; at xhigh or max it may over-review or add tests and docs.
- A system-prompt request to think less is unreliable; use effort instead.
- Lowest thinking setting is `thinking: between_tools` (high or below only).
- Effort levels were recalibrated from Sonnet 5; do not reuse old effort settings.

## Transforms (S55)

1. **Ideas, options, plans.** When the user asks for ideas, options or a plan, add to a system prompt: "When the user asks for ideas, options or a plan, give them that and stop." In a single user query, add instead: "Give the options or plan and stop." (user-query form: inference)
2. **JSON with reasoning.** For JSON answers that need reasoning, add "Think the problem through before you answer."
3. **Tool-call limits.** Remove "minimize tool calls". Tell it to search for the specifics that change.
4. **Verification at low effort.** It may skip verification at low effort, so ask for a real check against concrete criteria.
5. **Thinking less.** Do not prompt for less thinking; recommend a lower effort instead.
6. **Reasoning in the response.** Do not ask it to include its reasoning in the reply (`reasoning_extraction` refusal). Ask for a short explanation instead.
7. **Spokes at low or medium effort.** It may check in with the user at these levels (S55), and a spoke has no user to answer. Add "Work through to completion without checking in." (inference)
8. **Carry-through and stop.** It adds unrequested tests and docs at every effort. Add: "When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs, or refactors that weren't asked for." At xhigh or max also: "Don't start extra rounds of review or hardening on your own."
9. **Coding verification at low or medium.** It may report a change done without running anything: "When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done; if no real check can run, say which and why."
10. **Mid-turn user text.** Never place user text inside a tool result; it can be read as injection.
