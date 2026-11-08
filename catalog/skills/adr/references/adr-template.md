# ADR Template

A minimal layout based on MADR (Markdown Architectural Decision Records). Keep each
ADR to one decision and about one page. Delete optional lines that add nothing.

```md
# NNNN. <Decision as a short imperative phrase>

Status: proposed | accepted | superseded by NNNN | deprecated
Date: <YYYY-MM-DD>
Deciders: <who made the decision>

## Context and problem

<The forces at play and the question the decision answers, in a few sentences.
Link the plan, issue, or PR it came from.>

## Considered options

- <Chosen option>
- <Rejected alternative>: <why it lost>
- <Further alternatives, if any>

## Decision

Chosen: <option>, because <the deciding reasons>.

## Consequences

- Good: <what becomes easier>
- Bad: <what becomes harder, and the cost of reversing it>

## Links

- Supersedes: <NNNN, if any>
- Source: <plan, issue, or PR>
```

Index line in `docs/adr/README.md`:

```md
- [NNNN. <Title>](NNNN-kebab-title.md): accepted
```
