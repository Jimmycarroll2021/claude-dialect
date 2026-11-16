# Fable 5.2

model_id: claude-fable-5-2
source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 (F52)
source: https://platform.claude.com/docs/en/models/overview (MO)
source: https://platform.claude.com/docs/en/build-with-claude/effort (EF)
last_verified: 2026-11-17

## Profile (MO, EF)

- Moderate latency. Thinking always on. API default effort high; Claude Code default medium (CS).
- $8 / $40 per MTok. Replaces Fable 5.1 as the `fable` alias.

## Effort (F52)

- Effort sets thinking depth, tool calls and tokens; it barely changes reply length. Use the prompt for length and tone.
- low: quick or well-specified work. medium: interactive coding, chat, everyday knowledge work. high: hard coding, research, long unattended runs. xhigh: only for measured gains.
- At high and above it thinks before almost every reply, even greetings.
- "Think less" / "answer directly" lines do not work at medium and above; remove them and lower effort.

## Transforms (F52)

1. **Finish the whole task.** At low and medium it can stop early by listing what is left or offering to continue. For autonomous work add a short "Finishing work" section: keep going while work the user asked for is still owed; work through ordinary obstacles (errors, timeouts, empty results); report deliberate blockers.
2. **Approvals.** Name the exact action approved ("Yes, run the migration on the staging database"), not a bare "continue". Approval rules must name the actions they cover; broad rules make it hold back routine work.
3. **Ownership.** Only when restructuring is wanted, add "You are the owner and long-term maintainer of this codebase, and its design is up to you." It then also makes unrequested changes, which a scope rule does not cancel. Omit it for minimal changes.
4. **Progress updates.** It runs long silent tool sequences. Where a human is watching, ask for a line before starting, brief updates, and a short recap at the end.
5. **Subagents.** At xhigh and max it spawns subagents to review its own work. Remove standing "delegate" lines if it over-delegates.
6. **Stale caution.** It follows old cautions in memory and notes closely and asks for needless approvals. Name the routine steps that need no approval; replace absolute "never" rules with scoped rules plus the reason.
7. **Token budgets in prompt text.** Remove them; they raised cost with no gain.
8. **"Treat that answer as done".** Leave the Opus 5.5 chat line out where mistakes in earlier answers should be flagged.
9. **Hard style limits.** Rules like "20 words or fewer per sentence" are followed so closely that prose turns choppy; remove unneeded ones.
10. **Reports.** For final reports, ask it to write for a low-context reader: key point first, no invented terms or abbreviations, short sentences, bullets only for separate items.
11. **Reasoning in the response.** Do not ask it to write out its reasoning (`reasoning_extraction` refusal); ask for a short explanation instead.
