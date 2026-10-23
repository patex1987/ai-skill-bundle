# Platform Migration Map

A suggested pack selection per platform repository, and the repository facts
that need an overlay before the old `.ai/` copies are deleted. Each row is one
issue, one branch, and one PR in that repository. Only `movie-reservation-service`
has a written migration kit ([`movie-reservation-service/.ai/`](movie-reservation-service/.ai/)).

| Repository | Packs | Overlays to write from the old `.ai/skills` | Renamed or removed |
|---|---|---|---|
| movie-reservation-service | core, review, knowledge-base, teaching, nestjs | written: clean-architecture, nestjs, typescript, vitest-testing | — |
| movie-reservation-agent | core, review, knowledge-base, teaching, fastapi | clean-architecture (`llm_agent/` layer paths, `svcs` registrars, `docs/patterns/svcs_notes.md`), fastapi-service (Python 3.12, Piccolo, `svcs`), pytest-testing (`tests/fake_implementations`, `DependencyOverrideRegistrar`) | `testing` → `pytest-testing`; `agent-inspiration` stays **local** (host-specific reference corpus); `skills/README.md` stays local |
| movie-recommendation-service | core, review, knowledge-base, teaching, rust-axum | clean-architecture and rust-axum-service (routes `/health` `/ready` `/movies` `/recommendations`, catalog snapshots, provenance of `axum_tools_random_api@3ea72f3`), rust-testing (regression suite origin) | — |
| movie-platform-infra | core, review, knowledge-base, teaching, aws-cdk, architecture | aws-cdk-iac (`bin/infra.ts`, synth context flags, `adot-collector/`, `audit-router/`, `validate-stack.sh` as a local script), cdk-infra-testing (`npm run synth:ecr-contract`, `npm run ci`) | `infra-testing` → `cdk-infra-testing`; the planner overlay replaces the CDK-specific planner metadata |
| movie-reservation-web | core, review, knowledge-base, teaching, react | typescript (GraphQL adapters, static artifacts), vitest-testing (`npm run check`, header propagation contract) | — |
| movie-reservation-mcp, movie-recommendation-mcp | core, review, knowledge-base, teaching, python-mcp | python-mcp-service (downstream API, coordination with `movie-reservation-agent`, demo-fault metadata) | `testing` → `pytest-testing` |
| movie-platform-actions | core, review, knowledge-base, github-actions, architecture | github-actions-authoring (`actions/container-evidence/src` → `lib`, Node 24, `npm run ci`) | `testing` + `typescript` + `clean-architecture` variants merge into `github-actions-authoring` plus the generic skills |
| movie-platform-environments | core, review, knowledge-base, teaching, python, architecture | python-tooling (`movie_platform_automation` entry points, release sets), clean-architecture (incubator package and extraction policy), pytest-testing (validator test conventions) | `python-automation` → `python-tooling` plus `references/readability-and-cli.md`; `testing` → `pytest-testing` |
| golden-path-ecs-template | none: legacy migration source | — | keep its current `.ai/` until it is retired |

Notes:

- References to old names (`$testing`, `.ai/skills/infra-testing/…`) in a
  repository's own docs must be updated in the same PR.
- `programming-kb` defaults to explicit-only. Repositories that used the auto
  variant set `"invocation": {"programming-kb": "auto"}` and export
  `PROGRAMMING_KB_DIR` (the old hard-coded vault path no longer exists in the catalog).
- Codex agents previously defaulted to `gpt-5.4` (or `gpt-6-astra` in the
  environments repos). Map tiers in `bundle.json` `routing.models.codex` to
  keep that, knowing a pinned model blocks spawn-time escalation in Codex.
