# Building the Topic Map

A topic is one idea the engineer must understand, together with the changed files
that implement it. The order goes from the big picture down to the details, and from
building blocks up to what uses them.

## Contents

- [Find the flows](#find-the-flows)
- [Group into topics](#group-into-topics)
- [Order the topics](#order-the-topics)
- [Size limits](#size-limits)
- [The overview message](#the-overview-message)

## Find the flows

Before grouping, understand how the change runs:

1. Find each entry point the change adds or alters: route, handler, CLI command,
   scheduled job, message consumer, public function, UI action. Include unchanged
   entry points that now reach changed code.
2. Trace each flow inward: entry point, wiring and configuration, orchestration,
   domain logic, then storage and external calls in the order they happen. Read
   unchanged code along the path as context; only changed files become topic material.
3. Note changed code that no entry point reaches. It is either dead code or missing
   wiring, and worth a finding.

This trace drives the overview map and the "how it fits" sentences in each topic.

## Group into topics

- Group by **idea**, not by file or directory: "the coupon rules", "how the total is
  calculated", "how checkout accepts a coupon".
- Keep tightly coupled files together when splitting them would hide the rule
  that connects them (a type and its only validator, a migration and its model).
- Put a test with the topic whose behavior it proves, at the end of that topic. Give
  tests their own topic only when they are substantial or cut across topics
  (end-to-end suites, test infrastructure).
- Collapse mechanical changes into one topic near the end, described rather than
  read line by line: renames, formatting, generated code, lock files, snapshots,
  vendored files. Check that generated output matches its source when it matters.
- Shared code goes in the first topic that needs it. Later topics refer back to it.
- A deleted file belongs with the topic where its former caller lives.

## Order the topics

Each topic may rely only on ideas from earlier topics. In practice:

1. **The shape of the change** (only when the change adds a new component, module,
   or pattern): what new pieces exist and how they connect. Skip it for small changes;
   the overview covers it.
2. **Building blocks**: contracts, types, schemas, data models, migrations, and
   configuration the rest depends on.
3. **Core behavior**: domain rules and logic built on those blocks, following the
   runtime flow inward.
4. **Integration**: how the behavior is wired in: routes, handlers, dependency
   injection, adapters, storage, external clients, UI.
5. **Cross-cutting and supporting changes**: error handling, observability,
   permissions, feature flags, infrastructure, CI.
6. **Mechanical changes and docs.**

Within a level, follow the runtime flow. If the user asks to start somewhere else,
do so and adjust the rest. When two orders are equally valid, prefer the one where
the first topic explains why the change exists.

## Size limits

- Aim for 3–9 topics. A one-topic change gets the overview plus that topic.
- More than about 12 topics, or a change that mixes unrelated work: say so in the
  overview, suggest splitting the PR or walking through a focus area first, and let
  the user choose.
- A topic that needs more than about three snippets to explain is too big; split it
  into separate topics rather than parts.

## The overview message

The overview is the first message, before Topic 1. It does not count in `N`.

```text
Overview — <PR title or short name>

In plain terms: <what the change does and why, 2–3 sentences, no jargon>.

How it fits together:
  POST /checkout ─▶ applyCoupon ─▶ calculateTotal ─▶ order saved
                       │
                       └─ coupon lookup (new in-memory repository)

Size: 7 files, +180/−20, 3 commits. Mode: review.

Topics:
  1. Coupon contract — what a coupon is and when it is valid
  2. Total calculation — how a coupon changes the price
  3. Checkout wiring — how a request carries a coupon in
  4. Tests and docs

Start with Topic 1, or reorder?
```

Keep the map to a few lines of plain text: boxes and arrows only where they help.
Leave it out when the change is a single straight path you can describe in one sentence.
