# Evidence and Severity

These rules decide what becomes a finding. They apply in every mode, every
profile, and to every candidate source: your own tracing, another agent's
claim, or a scanner alert.

## Candidate gate

A candidate is reportable only when all of these are written down:

| Element | Question |
|---|---|
| Actor | Which lower-trust principal acts, and what can it already do by design? |
| Input or action | Which value, request, file, message, state transition, or selector does it control? |
| Intended control | Which check should reject, bind, isolate, limit, or revoke it, and where does it live? |
| Path | The exact trace from entry point to effect, with `path:line` anchors at the reviewed commit |
| Effect | The concrete result for another principal or resource: data read or changed, code run, money moved, authority gained, shared service stopped |
| Counterevidence | Which defenses you looked for, and why they do not apply |

If the effect lands only on the actor itself, or matches the authority the actor
already has by design, it is not a finding. Do not strengthen an effect beyond
what the trace shows: a crash is not code execution, slow work for one caller is
not a shared outage, and an action by the same principal is not privilege gain.

## States

| State | Evidence required | Severity | Reported in |
|---|---|---|---|
| `confirmed` | Complete, unambiguous source trace with defenses checked, or a bounded local observation in an approved sandbox | Yes | Findings |
| `likely` | Strong source evidence, but one named runtime or deployment condition is unverified | Yes, stated as conditional on that fact | Findings, with the condition |
| `needs-validation` | A plausible, source-grounded path blocked by one exact unknown fact (for example "is `/admin` reachable from the internet?") | No | Open questions, with a safe check for the owner |
| `rejected` | Specific counterevidence disproves it | No | Audit ledger only; summarize the count in change reviews |

A source-confirmed finding does not mean an exploit was run. Report the method
(source trace, existing test, local harness) separately from what was observed.
Do not wait for an exploit demonstration when the vulnerable flow is already
unambiguous and a safe fix exists.

## Severity anchors

Severity is likelihood × impact for the conditions that were demonstrated. If
you cannot state the concrete damage, the severity is lower than it feels.

- **critical**: an unauthenticated or external actor gains code execution, full
  data-store access, arbitrary account takeover, or control of the deployment
  pipeline.
- **high**: an explicit security control is fully defeated with real
  consequences. Examples: authentication bypass, a cross-tenant read or write,
  stored script execution against other users, authenticated code execution, a
  CI path that exposes deploy credentials to untrusted code.
- **medium**: a real boundary violation with limited blast radius, uncommon
  preconditions, or effects confined to a narrow set of resources.
- **low**: disclosure of non-secret internals, or an effect that needs sustained
  effort for little gain.
- **informational**: confirmed but minimal on its own. Useful mainly as a step
  in a chain.

To choose between high and medium, ask: does the result fully defeat an
explicit control for an action with consequences, or only weaken it? Network
locality alone does not lower severity. An internal-only flaw can still be high
when the internal network is part of the threat model.

## Falsify before reporting

Restate the claim in one precise sentence. Many false positives collapse at
this step. Then check:

- Is authentication or authorization applied globally (middleware, guards,
  router-level dependencies, gateway policy) rather than at this handler?
- Does the data layer already scope the query by owner or tenant? Does
  row-level security apply under the runtime database role, not the owner role?
- Is the value attacker-controlled, or does it come from server configuration,
  environment, constants, signed session data, or an administrator?
- Does the framework neutralize it (auto-escaping, parameterized queries,
  schema validation that strips unknown fields)?
- Is the code reachable in production, or is it dead, test-only, or behind a
  disabled flag?
- Does an existing test demonstrate the defense?
- Is the behaviour intentional and documented, such as a public endpoint or a
  same-principal capability?

Do not accept these shortcuts. Each needs the evidence named after it:

| Shortcut | Required instead |
|---|---|
| "This pattern looks dangerous" | A complete source-to-sink trace |
| "Similar code was vulnerable elsewhere" | Verify this instance's callers and guards |
| "Small change, low risk" | Classify by what the code touches, not by line count |
| "Just a refactor" | Check that every invariant the old code enforced still holds |
| "This is clearly critical" | Models over-rate severity, so argue the impact from the trace |

## Attacker-controlled vs. server-controlled

| Usually attacker-controlled (investigate) | Usually server-controlled (not a source by itself) |
|---|---|
| Request path, query, body, most headers, unsigned cookies | Settings, configuration files, environment variables, CLI flags of the service |
| Uploaded file content and file names | Constants and compile-time values |
| Webhook and message payloads from outside the trust boundary | Signed or encrypted session data verified by the server |
| Data written by other users or tenants | Records written only by administrators or migrations |
| Model output, retrieved documents, tool results in LLM features | Internal service URLs taken from configuration |
| Pull-request content, branch names, and issue text seen by CI | Repository secrets in a workflow that never runs untrusted code |

The right column turns into a source when an attacker can write to it, for
example a multi-tenant settings table or CI variables taken from a fork.

## Do not flag (unless the trace shows a concrete abuse)

- A missing hardening measure or best practice with no reachable abuse path.
- A missing second layer when the first layer holds. Mention it as hardening only
  if the user asked for hardening advice.
- A theoretical race condition or timing side channel without a practical
  trigger and effect.
- Denial of service, rate limiting, or resource exhaustion. Report these only
  when the user includes availability in scope, or when one cheap request
  degrades a shared service for others.
- Outdated dependencies with known advisories, during a change review that does
  not touch them. Those belong to SCA tooling. Report one when the change adds
  or upgrades the dependency, or when the vulnerable function is reachable.
- Problems in unchanged code during a change review, unless the change newly
  exposes them.
- Test-only code, fixtures, examples, documentation, and commented-out code.
- Missing authentication or authorization checks in client-side code, when the
  server enforces them.
- XSS in auto-escaping frameworks unless an escape hatch is used
  (`dangerouslySetInnerHTML`, `v-html`, `|safe`, `mark_safe`, `innerHTML` with
  untrusted data).
- SSRF where the attacker controls only the path, not the scheme, host, or port
  (unless the path reaches a sensitive internal route).
- Log content concerns, unless secrets, credentials, or personal data are
  written to logs.
- Memory-safety claims in memory-safe code outside `unsafe` and FFI blocks.
- Shell-script command injection, unless untrusted input actually reaches the
  script.
- Weak hashing used for non-security purposes (checksums, cache keys).
- Guessability concerns for random UUIDs, or missing TLS, `Secure` cookies, or
  HSTS in local-development configuration.

Treat these as context-dependent, not absolute. User-controlled text in a model
prompt is not a vulnerability by itself. It becomes one when the model can act
with authority (tools, data, approvals) that the text's author lacks. A workflow
input becomes one when an untrusted trigger can set it.

## Root causes, variants, and chains

- Deduplicate by root cause. Give each a stable fingerprint, such as the control
  location plus the missing invariant. Never use a line number or agent name.
  Several call sites with one missing guard are one finding with listed
  locations.
- When a high or critical root cause is found, search for variants: sibling
  routes, bulk and export paths, background jobs, GraphQL resolvers, retries,
  and legacy versions that perform the same effect. Establish each variant's
  conditions separately.
- After triage, check whether two individually weak findings combine into a
  real path, such as an information leak that supplies the identifier an
  authorization flaw needs. Report the chain as one finding that references
  both.

## Fix recommendations

Name the invariant the code must enforce. Then name the narrowest change that
enforces it at the last trusted decision point, usually the service or
data-access layer rather than the UI or controller. Pair it with a regression
test that fails before the fix. For authorization tests, assert both the denial
and that the protected state did not change. Prefer repository-specific
changes over generic advice, and note any compatibility risk the fix
introduces.
