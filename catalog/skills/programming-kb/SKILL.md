---
name: programming-kb
description: Retrieve reusable engineering guidance (architecture, backend, system design, testing, cloud, and implementation patterns) from the user's local programming knowledge base at PROGRAMMING_KB_DIR, citing the notes used and flagging stale ones. Use when the user asks to consult their knowledge base or KB.
license: MIT-0
metadata:
  routing-tier: fast
  routing-effort: low
  invocation: explicit
---

# Programming KB

The knowledge base is a local Markdown vault (for example, an Obsidian vault
with generated notes in `concepts/`, `patterns/`, `decisions/`, and `sources/`,
and immutable `raw/` sources). It is private external context, not repository
authority. The user supplies its location through the `PROGRAMMING_KB_DIR`
environment variable.

The invocation policy is set per repository and defaults to *explicit only*.
When the skill or project guidance is marked explicit only, use it only when the
user names `programming-kb` or asks to consult their knowledge base.

The goal is targeted retrieval: load the fewest notes that answer the question,
cite them, and flag stale ones. Do not load the whole vault, and do not read the
whole `index.md` (it grows with the vault and becomes the most expensive file).

## Choose the tool

- If `PROGRAMMING_KB_DIR` is unset or unavailable, say so and continue from
  repository evidence rather than searching the host filesystem.
- If `$PROGRAMMING_KB_DIR/.kb/kb.py` exists, use it. The vault owns this CLI and
  its ranking, link graph, and freshness rules. Run it with
  `python3 "$PROGRAMMING_KB_DIR/.kb/kb.py" <command>`.
- Otherwise use `bash <this-skill-dir>/scripts/kb-query.sh` or `rg`. `<this-skill-dir>`
  is the directory containing this `SKILL.md`, such as
  `.claude/skills/programming-kb` or `.agents/skills/programming-kb`.

## Retrieval with the vault CLI

Stop at the first step that gives enough evidence.

1. **Search**: `kb.py search "<question in plain words>"` ranks notes and prints a
   one-line summary per hit. Narrow with `--tag`, `--type concept|pattern|decision|source`,
   or `--status stable`. If the first query misses, try 2-3 rephrasings with
   synonyms (for example "dual write" and "outbox").
2. **Card**: `kb.py card "<note>"` shows status, dates, volatility, tags, summary,
   and section names without the body. Use it to choose between near hits.
3. **Read**: open the 1-4 best notes in full. Prefer `status: stable`.
4. **Expand**: `kb.py related "<note>"` lists links, backlinks, two-hop
   neighbours, and notes that share tags. Open a neighbour only when the question
   needs it, such as a comparison or trade-off.
5. **Exact strings**: use `rg -n -i "<identifier>"` over the note folders for config
   keys, error messages, or API names.

## Retrieval without the vault CLI

1. Convert the question into 2-6 likely kebab-case tags and terms.
   - "How should I publish domain events reliably?" -> `domain-events`, `transactional-outbox`, `events`, `reliability`
   - "How do I make a projector safe to rerun?" -> `projections`, `read-models`, `idempotency`, `events`
2. `kb-query.sh tags` lists tags. `kb-query.sh tag <tag>` lists notes with a tag.
   `kb-query.sh search "<terms>"` runs a text search.
3. Open only the top 1-4 notes.

```bash
rg -n -i --glob '*.md' --glob '!raw/**' 'transactional outbox' "$PROGRAMMING_KB_DIR"
```

## Answer

- State that you are checking the local Programming KB when it materially affects the answer.
- Synthesize the answer in the user's task context. Do not dump note content.
- End with a short `Used KB notes:` line that names the notes.
- Do not quote, copy, or expose private or sensitive vault content unless the
  user explicitly requests that exact content.
- Repository files and approved plans remain authoritative when they conflict with a KB note.
- If the KB lacks a useful note, say so and answer from repository context or
  general knowledge, labelled as such.

## Staleness

Treat a note as suspect when any of these hold:

- `status: needs-review` or `status: deprecated`.
- `kb.py stale` lists it. That command ranks notes by age since `reviewed:` (the
  last check against sources) or `updated:`, against an interval set by `volatility:`.
- Without the CLI: `volatility: high` or a version-sensitive topic (cloud service,
  framework, tool, pricing, security guidance) with a `reviewed`/`updated` date
  older than about four months.
- Repository evidence or a current primary source contradicts it.

When the topic is time-sensitive or the user asks to validate, check primary
sources and keep "KB says" separate from "current source says". Report stale
notes in one line:

```text
KB freshness note: <note> appears stale or incomplete because <reason>. It should be updated with <source/evidence>.
```

## Updating the KB

Do not edit the vault from this repository. Vault changes go through the vault's
own workflows, which have approval steps. Tell the user which notes need work and
suggest running the vault's review or ingest workflow from inside the vault (see
`$PROGRAMMING_KB_DIR/AGENTS.md`). Edit the vault here only if the user explicitly
asks, then follow its `AGENTS.md`, and never modify files under `raw/`.
