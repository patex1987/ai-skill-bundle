# Cost-Aware Model Routing: Design

## Question

Can the catalog default each skill or agent to the cheapest adequate model, so
that summarisation does not run on the strongest model at maximum effort, and
adjust that choice while multi-agent work runs?

## Answer in one paragraph

Partly through configuration, and the rest through orchestration policy. A
static label per entity is a good **default** for work that is delegated to a
separate context (subagents), because the tools let an agent file pin model and
effort. It cannot be the whole answer. The right tier depends on the *unit of
work*, not the skill. "Planning" a typo fix is not deep work, and "implementing" an
authorization check is. The evidence that should change the tier, such as failed
checks, review findings, or discovered risk, only appears while work runs. The
bundle therefore routes at three levels and keeps a human or test-based check as
the arbiter of quality.

## Three levels

| Level | Who decides | Mechanism in this bundle | Can it change mid-run? |
|---|---|---|---|
| Static default | Catalog author, overridden per repo | `metadata.routing-tier/effort` → `routing/tiers.json` → rendered agent `model`/`effort` | No |
| Plan-time | Planner | "Suggested tier" per implementation step, with the reason | When the plan is revised |
| Run-time | Lead agent following `model-routing` | Per-spawn model/effort override; escalation and de-escalation rules; logged decisions | Yes |

## Why inline skills stay advisory

In Claude Code, a skill's `model` changes the model for the current turn of the
**main** session, and `effort` applies while the skill is active. Pinning
`model: haiku` on a summarisation skill would downgrade whatever the main
session does in that turn, including unrelated reasoning. Pinning `opus` on a
planner would silently override a user who chose a cheaper session. The
renderer therefore:

- renders model and effort for **agents** (separate context, so pinning is safe);
- leaves **inline skills** advisory, with their tier shown in the index, unless the
  repository opts in with `routing.apply.skills: "enforce"` (effort only);
- renders model and effort for skills marked `metadata.context: fork`, because
  those run in their own subagent.

This keeps a user's explicit choice authoritative, which matches the
`model-routing` rule "an explicit user or repository choice wins".

## Why cascades are limited to cheaply checked work

Cascades such as FrugalGPT call cheaper models first and stop when a scorer
accepts the answer. Routers such as RouteLLM pick one model up front from a learned
difficulty estimate. Both rely on something that judges quality cheaply. A
cascade adds cost on hard inputs, because it pays for the failed cheap attempt too.
In coding work, tests, type checks, linters, and schema validators are cheap and
objective scorers. Design quality and security reasoning are not. The
`model-routing` skill therefore permits "try cheap first" only where the check is
objective, and starts at the capable tier otherwise. This is a design inference
from the routing literature, not a measured result for coding agents. No
benchmark for agentic coding cascades was found during this research.

## What is deliberately not automated

- **No automatic task classifier.** A tool-side router that guesses difficulty per
  request would need evaluation data that this platform does not yet have. The
  plan-time tier plus run-time escalation rules are reviewable, and their logs
  produce that data.
- **No silent fallback to other providers.** Fallback improves availability but
  does not establish that a different model suits the task. See the KB note
  *Model Routing and Fallback Boundaries*.
- **No vendor model IDs in the catalog.** Model names change faster than skills.
  Claude tier aliases (`haiku`/`sonnet`/`opus`) are the only defaults. Codex,
  Cursor, and Gemini inherit the session model until a repository maps tiers in
  `bundle.json`.

## Evidence loop (next step)

`plan-execution` records the tier, effort, actual model, escalations, and the
verification result for each delegated unit. After a few weeks, review those
records. Look for tiers that frequently escalate (start higher) and `deep` units
that passed first time with cheap checks (try `balanced`). Then adjust
`routing/tiers.json` or per-repository overrides. A deterministic recorder
(for example a Claude Code `SubagentStop` hook writing JSONL) would make this
data less dependent on agents following instructions. It is not implemented here.

## Sources

- Claude Code subagents and skills frontmatter, model precedence:
  <https://code.claude.com/docs/en/sub-agents>, <https://code.claude.com/docs/en/skills> (accessed 2026-10-23)
- Codex subagents (sandbox inheritance, `model_reasoning_effort`) and skills
  (`.agents/skills`, `allow_implicit_invocation`):
  <https://learn.chatgpt.com/docs/agent-configuration/subagents>, <https://learn.chatgpt.com/docs/build-skills> (accessed 2026-10-23)
- Cursor subagents and skills: <https://cursor.com/docs/context/subagents>,
  <https://cursor.com/docs/context/skills> (accessed 2026-10-23)
- Gemini CLI context files and imports: <https://geminicli.com/docs/cli/gemini-md/> (accessed 2026-10-23).
  Subagent field names come from secondary sources and are not verified.
- RouteLLM: <https://arxiv.org/abs/2406.18665>. Survey of routing and cascading:
  <https://arxiv.org/abs/2603.04445>. FrugalGPT was referenced through secondary
  summaries only; its headline cost figures were not verified.
- Local Programming KB: *Model Routing and Fallback Boundaries*, *Agent
  Orchestration Layers*, *Coding Agent Context Budgeting*, *Coding Agent Context
  Configuration*, *Reviewing Agent Skills and Tool Dependencies* (read 2026-10-23).
