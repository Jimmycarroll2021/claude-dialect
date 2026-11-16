<div align="center">
  <img src="media/logo.svg" alt="claude-dialect logo" width="200" height="200">

  <h1>🗣️ claude-dialect</h1>
  <h3><em>Every prompt, routed to the right Claude model — in its own dialect.</em></h3>

  <p>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/Jimmycarroll2021/claude-dialect?style=flat-square" alt="License: MIT"></a>
    <a href="https://github.com/Jimmycarroll2021/claude-dialect/stargazers"><img src="https://img.shields.io/github/stars/Jimmycarroll2021/claude-dialect?style=flat-square" alt="GitHub stars"></a>
    <a href="https://github.com/Jimmycarroll2021/claude-dialect/commits/main"><img src="https://img.shields.io/github/last-commit/Jimmycarroll2021/claude-dialect?style=flat-square" alt="Last commit"></a>
    <img src="https://img.shields.io/badge/Claude%20Code-add--on-D97757?style=flat-square" alt="Claude Code add-on">
  </p>
</div>

Every prompt you type into Claude Code gets sized, sent to the Claude model that fits it, and rewritten in that model's own dialect.

- **Lookups** (find, list, classify, extract) go to **Haiku 5.5**.
- **Everyday and well-defined work** goes to **Sonnet 5.5**.
- **Complex work** (unknown root cause, refactors, reviews) goes to **Opus 5.5**.
- **Hours-long research ending in a finished document** goes to **Fable 5.2**.
- **Quick chat answers** stay in your session.

Each hand-off prompt is rewritten using that model's prompting guide from Anthropic's docs. For example, Opus gets "double-check" lines removed because it verifies on its own, while Sonnet gets told to stop when the work is done instead of adding extras.

<div align="center">
  <img src="media/demo.svg" alt="Demo: a prompt about flaky checkout tests is routed to Opus, medium effort, class 4 complex" width="820">
</div>

## How it works

<div align="center">
  <img src="media/how-it-works.svg" alt="Flow: prompt, hook adds routing table, class 1-6, same model or chat?, do it here or rewrite in the model's dialect and spawn an agent, check, reply" width="760">
</div>

| Piece | Installed to | Job |
|---|---|---|
| `hooks/claude-dialect-route.sh` | `~/.claude/hooks/` | `UserPromptSubmit` hook: injects the six-class routing table and hand-off rule on every message, so routing does not depend on the model remembering to load the skill |
| `skills/optimise-prompt/` | `~/.claude/skills/` | The skill: interpret, route, rewrite, hand off. `references/` holds the routing table and one guidance file per model |
| `bin/claude-dialect-check.py` | `~/.claude/bin/` | `SessionStart` hook: warns if the prompt hook is missing or any guidance file is more than 30 days old |
| `CLAUDE.snippet.md` | appended to `~/.claude/CLAUDE.md` | The hand-off rule, between `claude-dialect:start/end` markers |

### The classes

| Class | Looks like | Model · starting effort |
|---|---|---|
| 1 lookup | find, list, grep, classify, extract | Haiku · medium (bulk: low) |
| 2 everyday | write a function, draft copy, analyse a CSV | Sonnet · high |
| 3 bounded | exact files + exact change + a named check | Sonnet · medium |
| 4 complex | unknown root cause, refactor, architecture, review | Opus · medium |
| 5 long-horizon | hours of research ending in a finished document | Fable · high |
| 6 chat | answerable with no tool call | this session |

"Be thorough" raises effort one level instead of adding words. If a result falls short, effort goes up before the model does: Haiku, then Sonnet, then Opus, then Fable.

## Install

Needs Claude Code and `python3`.

```bash
git clone https://github.com/Jimmycarroll2021/claude-dialect
cd claude-dialect
./install.sh
```

Then start a new Claude Code session. The installer is safe to rerun. It backs up `settings.json` and `CLAUDE.md` first, keeps any hooks you already have, and moves an existing `optimise-prompt` skill aside instead of overwriting it.

Uninstall with `./uninstall.sh`. It removes only what the installer added.

## Prove it works

```bash
python3 tests/run.py          # 12 sample prompts, dry run: checks the class picked (~2 min)
python3 tests/delegation.py   # 3 real tasks in a temp folder: checks the hand-off happens (~5 min, uses tokens)
```

Both run `claude -p --model sonnet`. Expected delegation results in a Sonnet session: the ticket-sorting task spawns Haiku, the small script stays in the session, and the flaky-test bug spawns Opus.

Results on the author's machine (2026-11-17): routing was 5/12 with a plain "use the skill" hook and is 12/12 with the routing table in the hook. Delegation was 3/3.

## Using it

- Just type as normal. When work is handed off you see one line, e.g. `Route: opus · medium · class 4 complex`.
- `/optimise-prompt --show <query>` shows the route and the rewritten prompt without running anything.
- `/optimise-prompt --model opus <query>` forces a model.

## Cost note

Complex work now runs on Opus and long research on Fable, which cost more per token than Sonnet (Fable is about 4x Sonnet). Small lookups pay a few seconds of hand-off overhead. To cap it, edit the class table in `hooks/claude-dialect-route.sh` and `references/routing.md`, then rerun `./install.sh` and the tests.

## Keeping it current

The guidance files carry a `last_verified` date. The session-start check warns after 30 days. To refresh, ask Claude to "refresh the optimise-prompt guidance from the Claude prompting docs". The sources are listed at the top of each file:

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Per model: [Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5), [Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5), [Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2), [Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5), [Haiku 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5)
- [Models overview](https://platform.claude.com/docs/en/models/overview), [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)

Then rerun both tests.

## License

MIT. See `LICENSE`.
