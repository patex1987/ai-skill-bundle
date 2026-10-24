# Findings

A finding is a specific, evidenced reason to change something. A walkthrough raises
few findings, chosen well. Each one is placed under the topic where the engineer can
see the code.

## Contents

- [Tags](#tags)
- [Evidence before a finding](#evidence-before-a-finding)
- [Checks worth running](#checks-worth-running)
- [What not to raise](#what-not-to-raise)
- [Routing](#routing)
- [Posting](#posting)

## Tags

| Tag | Meaning |
|---|---|
| `blocking` | must be fixed before merge: wrong behavior, data loss, security, broken contract |
| `should` | worth fixing in this change: missing test for new behavior, a confusing design |
| `nit` | small and optional; label it `nit, taste` when it is preference |
| `question` | a premise only someone else can settle; name the person or role |

Number findings within a topic (1, 2, …). Raise at most the two highest-leverage
refactoring suggestions per topic, and fold minor naming or nesting points into one `nit`.

## Evidence before a finding

Do not present a suspicion as a finding. Each finding needs:

- **Evidence:** `path:line`, or a command and its relevant output.
- **Impact:** what goes wrong, for whom, and when. Leave it out for an obvious `nit`.
- **Suggestion:** the smallest change that fixes it, or the question to ask.

Confirm runtime or library behavior with the smallest safe check: read the source,
look up the documentation, or run a focused test. Use read-only commands. Running
tests can have side effects, so read what a command does before running it. If
you cannot confirm a finding, say so and tag it `question` rather than `blocking`.

## Checks worth running

- Compare changed tests with their base versions: deleted tests, weakened assertions,
  removed cases.
- Expected values computed from the same production constant or function they verify
  prove nothing. Look for literal expectations.
- Fields mapped or set but never asserted, especially where swapping two would still pass.
- New behavior without a test that fails without it.
- Parallel implementations (two adapters, two handlers) with unequal error handling or
  coverage, unless their contracts differ.
- Claims in the PR description ("tested with X", "no behavior change"): check that
  the named command actually exercises the changed code.
- Code that no entry point reaches; configuration that nothing reads.
- Contract changes: callers, consumers, serialized formats, and migrations outside the diff.
- A smell the change introduces or makes worse, with a concrete payoff from
  refactoring: what becomes easier to change, test, or understand. Name it as a
  possibility ("possible duplicated validation").
- A committed secret: `blocking`, recommend rotation, refer to it by path and key
  name only.

## What not to raise

- Style that formatters, linters, or the type checker already enforce.
- What the repository's documented conventions endorse.
- Problems that existed before this change and that it does not touch. Mention them
  as `Follow-up` only when they get in the way of this change.
- Theoretical edge cases that fail loudly and cheaply, unless the user wants that guard.
- Speculation about code you have not read.

## Routing

The user routes each finding. Propose a route, and let the user override it:

- **Open** — fix before merge.
- **Follow-up** — worth doing, separately (ticket, later PR).
- **Question** — waiting on a named person or role.
- **Drop** — not worth changing; record the reason.

The plain-text answer can be as short as `1 open, 2 drop` or `question: why does 1
fail?`. Answer questions before asking for the routing again. Record routed findings
in the walkthrough record immediately.

Routing is not a request to fix. Change code only when the user explicitly asks to
fix a specific finding. Then fix that item only, run the repository's relevant checks,
record the result, and return to the walkthrough at the current topic. A bare "ok" or
"sounds right" records findings as proposed; it does not authorize edits.

## Posting

Post nothing to the PR unless the user asks. When asked:

1. Draft the comments, each tied to `path:line` in the PR's head commit, plus a short
   summary comment.
2. Show the exact text and target lines to the user and wait for approval. Edit on request.
3. Post them as one pending (batched) review when the platform supports it, so the
   author gets a single notification. Use the review state the user chose
   (comment, approve, or request changes). Never approve on your own judgement.
4. Record what was posted, with links, in the walkthrough record.
