# 0001. Store sessions in Postgres

Status: accepted
Date: 2026-09-14
Deciders: the service owner

## Context and problem

Sessions must survive a restart, and the service already runs a Postgres database.

## Considered options

- Postgres table for sessions
- A dedicated cache cluster: rejected, because it adds an operational dependency
  for a few thousand sessions

## Decision

Chosen: a Postgres table, because it adds no new infrastructure.

## Consequences

- Good: one store to operate and back up.
- Bad: session reads add database load; moving them later needs a data migration.

## Links

- Source: the session persistence plan
