# Routing Mechanics by Tool

Checked against vendor documentation on 2026-10-23. Re-check before relying on a
field that is not listed here. Unrecognised frontmatter is usually ignored without
an error, so a misspelled field fails quietly.

## Claude Code

- **Subagents** (`.claude/agents/*.md`): `model` accepts `haiku`, `sonnet`, `opus`,
  a full model ID, or `inherit`. `effort` accepts `low` to `max`, depending on the
  model. Precedence: a per-invocation model chosen when spawning the agent, then the
  agent's `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the session model.
  `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` makes the environment variable win.
  Organisation `availableModels` policy can substitute a permitted model.
- **Skills** (`.claude/skills/*/SKILL.md`): `effort` applies while the skill is
  active. `model` applies to the current turn only. With `context: fork`, the skill
  runs in a subagent and `model` sets that subagent's model. That is the only way a
  skill gets its own model without changing the main session.
- **Dynamic adjustment:** when the lead agent spawns a subagent, the spawn
  call can pass `model` (and, where the tool exposes it, `effort`). That value
  overrides the agent file for this one invocation, so it is how you escalate or
  de-escalate a single unit during execution without editing configuration.
- **Effort support:** current Opus, Sonnet, and Haiku models accept `low` to `max`.
  A level the active model does not support is clamped to the highest supported
  level below it, not rejected.
- **Session:** `/model` and `/effort` change the main conversation. The
  `opusplan` model alias uses Opus in plan mode and switches to Sonnet for
  execution. It is the session-level version of "deep for planning, balanced for
  routine slices". Generated skill files leave the main session's model alone
  unless a skill is forked.
- Docs: <https://code.claude.com/docs/en/sub-agents>, <https://code.claude.com/docs/en/skills>

## Codex

- **Custom agents** (`.codex/agents/*.toml`): `model` and `model_reasoning_effort`
  (documented values `low` to `ultra`, depending on client and model). Values in
  the file take precedence over spawn and `[agents]` defaults. A model pinned in an
  agent file therefore cannot be escalated at spawn time. To escalate, delegate to a
  different agent, or leave that tier unmapped so the agent inherits the session model.
- **Sandbox:** subagents inherit the parent session's sandbox and approval policy.
  `sandbox_mode` in an agent file does not make it read-only. Enforce read-only
  review through the parent session's sandbox.
- **Skills** are discovered in `.agents/skills/`. `agents/openai.yaml`
  `policy.allow_implicit_invocation: false` makes a skill explicit-only.
- Docs: <https://learn.chatgpt.com/docs/agent-configuration/subagents>, <https://learn.chatgpt.com/docs/build-skills>

## Cursor

- **Subagents** (`.cursor/agents/*.md`): `model` is `inherit` or a specific model ID.
  `readonly: true` blocks edits and state-changing commands. Cursor also reads
  `.claude/agents/` and `.codex/agents/`, and `.cursor/` wins on name conflicts.
- **Skills:** `.agents/skills/` and `.cursor/skills/`, plus `.claude/skills/` and
  `.codex/skills/` as compatibility paths. `disable-model-invocation: true` makes a skill explicit-only.
- No documented reasoning-effort field.
- Docs: <https://cursor.com/docs/context/subagents>, <https://cursor.com/docs/context/skills>

## Gemini CLI

- **Subagents** (`.gemini/agents/*.md`): `model` defaults to `inherit`. Restrict
  `tools`, because subagents may run tools without confirmation.
- **Skills:** `.gemini/skills/` or the `.agents/skills/` alias.
- **Context file:** `GEMINI.md` by default. Set `context.fileName` in
  `settings.json` to read `AGENTS.md` instead.
- Field names come from launch material and secondary guides. Verify them against
  <https://geminicli.com/docs/> before depending on them.

## What the repository renderer does

`python3 .ai/render.py` maps each agent's `routing-tier` and `routing-effort`
through `.ai/routing.json`, as overridden by `.ai/bundle.json` `routing.models`
and `routing.overrides`:

- Agents receive model and effort fields (`routing.apply.agents: enforce`, the default).
- Skills stay advisory by default: their tier appears in the generated index, but
  the session model is not changed. Set `routing.apply.skills: enforce` to emit
  Claude `effort` for skills. A skill with `metadata.context: fork` always gets its
  tier's model and effort, because it runs in its own subagent.
- A tier with no model configured for a tool renders as `inherit`.
