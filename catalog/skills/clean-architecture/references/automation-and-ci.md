# Clean Architecture for Automation, CI, and Infrastructure Control Planes

Small scripts should stay small. Apply these boundaries when automation makes
trust, admission, or promotion decisions, or integrates several external systems.

```text
CLI / workflow entry point      -> parses untrusted input, wires adapters, renders output, exit code
application workflow (use case) -> sequences named operations
policy                          -> pure decisions: admissible, trusted, promotable, valid
adapters                        -> filesystem, subprocess, schema loading, GitHub, registries, cloud APIs
```

- Policy never parses arguments, prints, reads files, spawns processes, or calls
  external APIs. Test it with plain values.
- Ports describe only the operation the caller needs: a Python `Protocol` or
  callable, a TypeScript function type, a Rust trait or function. Do not pass a
  general command runner or full SDK client through the system.
- Every executable building block has a documented local entry point, and CI
  calls that same entry point. YAML and shell stay thin glue. CI is the final
  verifier, not the primary debugging environment.
- Validate structure at the edge before mapping untrusted JSON, environment
  values, or command output into typed values. Keep schema validation mechanical
  and semantic trust decisions in policy.
- Architecture cleanup must not erase security mechanics: bounded reads,
  no-follow file opening, archive-path validation, exact digest checks, atomic
  outputs, argument arrays instead of shell strings, and credential redaction.
  Give adapters the least authority they need.
- Preserve fail-closed behaviour. Emit proof or attestations only after the
  required verification succeeds.
- Start with well-named modules (`models`, `policy`, a capability-named use case,
  boundary-named adapters, `cli`). Add `domain/`/`application/`/`adapters/`
  packages only when several implementations make navigation easier. Avoid
  `utils`, `common`, and grab-bag shared packages.
- Extract a shared package only after the capability's behaviour, trust
  contract, and tests are stable, credible cross-repository consumers exist, and
  versioning, publishing, and ownership are decided. Plan that decision explicitly.

## GitHub Actions

- Keep profile selection, admission rules, and value validation pure.
- Treat each executable entrypoint as a composition root. Keep Git, GitHub CLI,
  filesystem, environment, and output operations in narrow adapters.
- Composite YAML owns step order, the permissions expected from the caller, and
  immutable (SHA-pinned) third-party action references.
- Trace inputs from action metadata and runner environment through validation,
  external commands, retained files, and outputs. Policy code must not be able
  to choose arbitrary repositories, workflows, paths, or artifact names.

## Infrastructure as code

Do not force service layers onto straightforward construct or stack code.
Apply ports and adapters only to control-plane automation that makes decisions:
promotion, drift handling, or environment admission.
