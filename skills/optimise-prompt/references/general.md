# General prompting guidance (all current Claude models)

last_verified: 2026-10-23

## Sources

| Code | URL |
|---|---|
| BP | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| OV | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview |
| MO | https://platform.claude.com/docs/en/models/overview |
| EF | https://platform.claude.com/docs/en/build-with-claude/effort |
| CS | https://code.claude.com/docs/en/model-config.md |

Model-specific pages are listed in each model file. Rules marked "(inference)" are this skill's extrapolation, not a documented statement. Rules marked "(skill rule)" are this skill's own policy.

## Live fetch

When a model file is missing or a `last_verified` date is more than 30 days old, get the best-practices page and the model's prompting page, plus MO and CM (in `routing.md`) when `routing.md` is stale. Fetch the pages directly (or have a small Haiku agent fetch them) and update the files. If that fails, use the nearest file in the same family and say so. (skill rule)

- Best practices: the BP URL above.
- Model page: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-<model id without date suffix>`
  - `claude-opus-5-5` → `.../prompting-claude-opus-5-5`
  - `claude-opus-5` → `.../prompting-claude-opus-5`
  - `claude-fable-5-2` → `.../prompting-claude-fable-5-2`
  - (inference: derived from the published page slugs; if the URL 404s, check the MO page for the current model list and the BP page for links.)

## General rules

1. Be explicit. "If you want Claude to do more than the task strictly requires, explicitly request it". (BP)
2. Colleague test: a prompt that would confuse a colleague with little context will confuse Claude. (BP)
3. Use numbered steps when order or completeness matters. (BP)
4. Give the reason behind a constraint, because Claude generalises from it. "Read aloud by TTS, so no ellipses" beats "NEVER use ellipses". (BP)
5. If examples are used, make them relevant and varied, wrap each in `<example>` tags, and use 3–5. (BP)
6. Separate content types with XML tags such as `<instructions>`, `<context>`, `<input>`, `<documents>`. (BP)
7. A one-sentence role helps. (BP) Keep it to one sentence, with no elaborate persona. (skill rule, resolving `interpret.md` conflict (a))
8. With long inputs (20k+ tokens), put the documents first and the query last ("up to 30 percent" better), and ask for supporting quotes first. (BP)
9. Say what to do, not what not to do. The prompt's own style shapes the output's style. (BP)
10. Claude takes wording literally: "can you suggest changes" gets suggestions, not edits. Use action verbs when action is wanted. (BP)
11. Replace "CRITICAL" / "You MUST" style emphasis with plain wording. (BP, documented for Opus 4.5/4.6; applying it to 5.x is an inference.)
12. Cut back older prompting that pushed for thoroughness or heavier tool use (4.6 and later). (BP)
13. "Think thoroughly" beats a hand-written step plan for reasoning. (BP)
14. On current models (Fable 5.2, Opus 5.5, Sonnet 5.5 and older 5.x), a request to write out reasoning in the response, in `<thinking>` tags or a fixed format, may be declined as `reasoning_extraction`; ask for a short explanation instead. (BP, O5, O55, S55, F52) On the always-thinking models (Fable 5.2, Opus 5.5; "Thinking always on" in their model files), also remove generic "think step by step" requests; any thoroughness signal goes to effort per checklist item 8. (skill rule)
15. "Before you finish, verify your answer against [test criteria]" helps, except on Opus 5 and Opus 5.5, which verify unprompted; there use a testable done-criterion only. (BP, O5; 5.5 inference) Sonnet 5.5 and Haiku 5.5 at low or medium do need an explicit "run a real check" line (S55, H55).
16. For research, define what a successful answer looks like. (BP)
17. Prefill is gone (400 error) on 4.6 and later; remove any prefilled assistant turn. (BP)
18. Start from clear success criteria and a way to test them. (OV)

## Effort

| Level | Use for (EF) |
|---|---|
| low | Most efficient; simple, fast, cheap work such as subagents |
| medium | Balanced; the default on Opus 5.5 and Haiku 5.5 |
| high | Spends what the task needs; complex reasoning, coding and agentic work |
| xhigh | Long-horizon agentic work (30+ minutes) |
| max | Deepest reasoning, with no limit on spend |

- "Effort is a behavioral signal, not a strict token budget." (EF)
- Lower effort means fewer and terser tool calls. (EF)
- Level names do not mean the same amount of thinking on every model. (EF)
- The per-model recommendations in each model file override this table. (skill rule)
- Claude Code's effort setting maps to the API effort setting. (inference, unverified)
- Claude Code settings keys do not accept `max`. (CS)

## Rewrite checklist (apply in order, skip what does not apply)

1. **Success criteria.** State what a successful result looks like and how to test it, using only what the user said or implied. (OV 18, BP 16)
2. **Action wording.** If the user wants something done, use an action verb ("Fix", "Write", "Rename"). If they asked for suggestions or a plan, keep it that way. (BP 10)
3. **Explicit scope.** Spell out anything beyond the bare task that the user actually asked for. Add nothing they did not ask for. (BP 1)
4. **Missing context.** Apply the colleague test; add context from the user's words or the session only. (BP 2)
5. **Reasons.** Attach the user's reason to each constraint where it is known. (BP 4)
6. **Positive phrasing.** Turn "don't do X" into "do Y" where Y is clear. (BP 9)
7. **Tone down emphasis.** Replace capitalised or "you have to" emphasis with plain wording plus the reason. (BP 11, inference for 5.x)
8. **Remove legacy pushes.** Drop "be really thorough", "use as many tools as possible" and similar from the prompt text. (BP 12) When the user explicitly asks for thoroughness or care ("be thorough", "double check", "EXTREMELY thorough"), do not just delete it: raise the class's starting effort one level and say so in a bullet (`routing.md`). (skill rule)
9. **Reasoning requests.** Replace a hand-written reasoning plan with "Think thoroughly" (BP 13), unless the model file says to use effort instead. Remove requests for `<thinking>` tags on the models in rule 14, and generic "think step by step" requests on the always-thinking models named there. Keep numbered steps where order or completeness matters. (BP 3)
10. **Structure.** For distinct parts, wrap them in XML tags (BP 6). With long documents, documents first, query last, quotes first (BP 8). Add a one-sentence role if it helps (BP 7). Keep examples only if the user supplied them or asked for them; format per BP 5.
11. **Verification.** Add "Before you finish, verify your answer against [criteria]" when criteria exist (BP 15), except where the model file says otherwise.
12. **API-only cleanup.** If the user is writing an API prompt, remove any prefill (BP 17).
13. **Model transforms.** Apply the model file's transforms last.
14. **Style.** Write the rewrite in the style you want back (BP 9).
15. **Length and narration.** Effort does not shorten replies on 5.x models; when a short answer or quiet progress is wanted, say so in the prompt. (O5, F52)
