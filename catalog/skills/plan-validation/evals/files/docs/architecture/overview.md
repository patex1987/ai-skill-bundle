# Architecture Overview

Last verified against 3f2a9c1 on 2026-10-01.

## Purpose and boundaries

A small HTTP API that serves account data to API-key holders.

## Components

- HTTP handlers: `src/handlers.py`
- Account store: `src/store.py`

## Data and control flow

A request is authenticated by API key, then handled and answered from the store.

## External dependencies

- A relational database for accounts.

## Key decisions

None recorded yet.

## Known gaps

- No request limits.
