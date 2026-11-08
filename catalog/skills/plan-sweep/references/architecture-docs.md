# Architecture Documents

`docs/architecture/` holds the repository's current shape: what exists now, not
what was planned. A new session reads it instead of reverse-engineering the code.
Plans and their close-out feed it; `plan-sweep` and `plan-validation` propose edits,
and the author approves them. The folder is written by hand and is created when
the first approved edit needs it.

## Layout

- `overview.md` is the entry point. Every other document is linked from it.
- Add a further document (for example `data-model.md` or `integrations.md`) only
  when a topic outgrows its overview section. Keep one topic per document.
- Decisions live in `docs/adr/`. Architecture documents link to them instead of
  restating them.

## `overview.md` sections

```md
# Architecture Overview

Last verified against <commit> on <YYYY-MM-DD>.

## Purpose and boundaries

<What this repository does and what it deliberately does not do.>

## Components

<Main modules or services, each with its responsibility and entry point path.>

## Data and control flow

<How a typical request or job moves through the components. A diagram is optional.>

## External dependencies

<Services, stores, queues, and third-party APIs, and how each is reached.>

## Key decisions

- [NNNN. <Title>](../adr/NNNN-kebab-title.md)

## Known gaps

<Known limits, debt, and unverified areas, each with a link to an issue where one exists.>
```

## Rules

- Describe what the code does now, with `path` references. Do not copy plan intent
  or future work into it. Future work goes under known gaps, with a link.
- When you update a section, check it against the code and update the "last
  verified" line. Do not change that line for sections you did not check.
- Keep it short. If a section needs more than about a screen, move the detail to
  its own document and link it.
