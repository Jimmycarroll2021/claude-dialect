# Haiku 5.5

model_id: claude-haiku-5-5
source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5 (H55)
source: https://platform.claude.com/docs/en/models/overview (MO)
source: https://platform.claude.com/docs/en/build-with-claude/effort (EF)
last_verified: 2026-11-17

## Profile (MO, EF)

- Fastest current model. Default effort medium. First Haiku with effort.

## Effort (H55)

- low for chat and high-volume work.
- medium as the default, including agentic coding.
- high for knowledge work and strict instruction following.
- "Answer directly" does not stop thinking; use effort instead.
- Thinking can be disabled at high or below; `budget_tokens` returns 400. At xhigh in multi-turn chat the reply can be empty.

## Transforms (H55)

1. **Dates and search.** When search is available, give today's date and tell it, in your own words, that its training data ends well before that date. Attribution: H55's sentence opens "Your training data ends well before today's date"; do not paste a fragment of it. For the exact wording, get H55 per the live-fetch rule in `general.md`.
2. **No blanket search rule.** Do not add "search for any present-day factual question"; it caused needless searches with no accuracy gain. Name the specific facts that need checking instead (inference).
3. **Early stopping.** At low effort with long prompts it can stop early; add an instruction, in your own words, to keep working until everything the user asked for is done. Attribution: H55's sentence opens "Keep working until everything the user asked for is done"; do not paste a fragment of it.
4. **Chatbot rules.** For chatbot system prompts, its rules hold even when the user argues; state rules once, plainly, with reasons (BP 4, BP 11).
5. **Thinking less.** Do not prompt for less thinking or "answer directly"; recommend a lower effort instead.
6. **Coding verification.** At low or medium, ask for a real check that exercises the change before reporting done (same wording as Sonnet 5.5 transform 9).
7. **Finish then stop.** Pair the keep-working line with "When the work the user asked for is done and checked, stop and report."
8. **Reasoning out of the reply.** Reasoning leaks into visible text more at low effort or thinking off; prefer medium with thinking on.
9. **JSON plus own tools.** With thinking off and JSON output it may skip a needed tool call; prefer adaptive thinking.
