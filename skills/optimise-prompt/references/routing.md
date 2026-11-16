# Model and effort routing

last_verified: 2026-11-17

## Sources

| Code | URL |
|---|---|
| MO | https://platform.claude.com/docs/en/models/overview |
| CM | https://platform.claude.com/docs/en/about-claude/models/choosing-a-model |
| EF | https://platform.claude.com/docs/en/build-with-claude/effort |
| CS | https://code.claude.com/docs/en/model-config.md |
| F52, O55, S55, H55 | The model prompting pages listed in each model file |

Rules marked "(inference)" are this skill's extrapolation; "(skill rule)" is this skill's own policy.

## Models at a glance

| Alias | Model ID | Positioning (MO) | Speed (MO) | Price in/out per MTok (MO) | Default effort |
|---|---|---|---|---|---|
| `fable` | `claude-fable-5-2` | Demanding reasoning and long-horizon agentic work | Moderate | $8 / $40 | high (F52; Claude Code default medium) |
| `opus` | `claude-opus-5-5` | Long-running agentic coding and knowledge work | Moderate | $4 / $20 | medium |
| `sonnet` | `claude-sonnet-5-5` | Best combination of speed and intelligence | Fast | $2 / $10 | high |
| `haiku` | `claude-haiku-5-5` | High-volume, latency-sensitive tasks: classification, extraction, routing | Fastest | from $0.10 / $0.50 | medium |

All four: 1M context, 128K max output. The aliases map to these IDs on the Anthropic API (CS).

## Classes

Classify by the task's difficulty, not by the tools of the agent that will run it. Where signals span two classes, the hardest part decides.

| # | Short name | Signals | Alias | Starting effort |
|---|---|---|---|---|
| 1 | `lookup` | Find, list, grep, classify, extract fields, map code without changing it | `haiku` | medium; bulk items: low |
| 2 | `everyday` | Write a function, draft copy, analyse a CSV, routine tool use; scope not fully pinned | `sonnet` | high |
| 3 | `bounded` | Exact files AND exact change AND a named check are all given; one coherent change | `sonnet` | medium |
| 4 | `complex` | Unknown root cause, debugging, refactor, architecture, review or audit | `opus` | medium |
| 5 | `long-horizon` | Hours of research or analysis ending in a finished report, document or deck | `fable` | high |
| 6 | `chat` | Answerable in chat with no tool call: explanation, quick fact, wording help | the session's own | current |

- Unclear class: `opus` at medium. "If you're unsure which model to use, start with Claude Opus 5.5." (MO)
- Thoroughness requests raise the starting effort one level. (skill rule)
- Class 5 work with a lot of fact-gathering: split it. Haiku agents gather sourced facts; one Fable agent writes the finished document. (inference)

## Escalation

Raise effort before switching model. "Tuning effort is often a better lever than switching models." (CM)

1. Start at the class's model and effort.
2. Falls short: raise effort one level on the same model.
3. Haiku at high still short: Sonnet. Sonnet at high still short: Opus at medium (Sonnet at xhigh tends to over-review; S55).
4. Opus: high, then xhigh only for a measured gain. Still short: Fable at high.

Go straight to Fable only for class 5: it costs 2x Opus and 4x Sonnet. (MO)

## Hand-off rule (skill rule)

- Class 6, or the routed model is the session's own model: do it in the session.
- Otherwise spawn an agent on the routed model and effort, whatever the size of the task.

## Agent type

The class sets model and effort; the agent type follows the work. Use whatever agents exist in the Agent tool's list:

| Work | Agent type |
|---|---|
| Read-only search or recon (class 1) | `Explore`, or `general-purpose` when a file must be written |
| Anything that edits files, runs commands or uses MCP tools | `general-purpose` |
| A custom agent whose description matches the work | that agent |

- A custom agent's `model:` frontmatter is a default; the Agent tool's `model` parameter overrides it. (CS)
- `fork` ignores `model`; never use it when the route differs from the session's model.
- Agent tool parameters: `model` = `fable` | `opus` | `sonnet` | `haiku`; `effort` = `low` | `medium` | `high` | `xhigh` | `max`. Settings keys do not accept `max`. (CS)
