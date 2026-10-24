# Sources

The text of this skill is original. The ideas below come from published skills,
which were read on 2026-10-24. Nothing was copied verbatim.

| Source | Licence | Ideas adapted |
|---|---|---|
| [xpepper/pr-review-agent-skill `guided-flow-review`](https://github.com/xpepper/pr-review-agent-skill) at `3435e5190593dd94299815c66c803c4a2492c092` | MIT | Runtime-flow tracing from entry points, pinned comparison and head check, one step per message with a decision gate, evidence before findings, finding tags, routing sections, test-quality checks, resumable review file |
| [aidankinzett/claude-git-pr-skill](https://github.com/aidankinzett/claude-git-pr-skill) | see repository | Posting as one pending review after the user approves the comments |
| [Boris Tane, How I use Claude Code](https://boristane.com/blog/how-i-use-claude-code/) | article | Terse, document-backed steering; short corrections |

This skill differs from `guided-flow-review` in five ways:

- It groups the change by idea (topic) rather than by file.
- It opens with an overview and a map.
- It orders topics so that each builds on the ones before it.
- It shows a `Topic M/N` counter.
- It requires a plain-language explanation and snippets in every topic.

It also has an explain-only mode for onboarding.
