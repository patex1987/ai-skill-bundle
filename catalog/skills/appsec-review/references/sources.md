# Sources and Provenance

This skill is original text written for this catalog. It adapts ideas, not
wording, from the sources below. They were reviewed on 2026-10-23 at the pinned
commits. Re-review a source before adopting newer ideas from it. A
public repository or a high star count is not a security endorsement.

| Source | Revision reviewed | License | Ideas adopted |
|---|---|---|---|
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` | MIT | Guidance vs. full-audit modes; boundary-and-result candidate gate; `needs-validation` without severity; severity anchors; coverage ledger and coverage critic; fresh verifiers that never verify their own candidates; sandbox-only local execution; prior-run reuse; budget reservations; AI/agent, supply-chain, cloud, and data-lifecycle attack classes |
| [Cloudflare: Orchestrating AI Code Review at scale](https://blog.cloudflare.com/ai-code-review/) (2026-04-20) | n/a | n/a | Explicit "what not to flag" lists; diff noise filtering with migrations kept; risk tiers where security-sensitive paths always get full review; a coordinator that deduplicates and filters; approval-biased verdict rubric; incremental re-review rules; stronger models reserved for coordination |
| [trailofbits/skills](https://github.com/trailofbits/skills) (`differential-review`, `fp-check`, `insecure-defaults`, `supply-chain-risk-auditor`, `static-analysis`) | `196a9073ab10d35bacf111f945e02c00b2c6883a` | CC-BY-SA-4.0 (ideas only, no text copied) | Risk-first triage; scaling depth to change size; blast radius and removed-code history; rejected rationalizations; restating the claim before verifying; checking chains after triage; scanner telemetry off and reporting tools that did not run |
| [getsentry/skills](https://github.com/getsentry/skills) (`security-review`, `gha-security-review`) | `f57ada2d0b640406ea7e25b11d636c530e77c58b` | Apache-2.0 | Research wide, report narrow; server-controlled vs. attacker-controlled sources; framework-mitigated patterns; workflow injection classes |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | `0c6a49f1fa56a1d472575da86a94dbc1edb78eda` | MIT | Diff-scoped review; a separate false-positive filtering pass per candidate; exclusions and precedents (adapted into context-dependent rules) |
| [openai/skills](https://github.com/openai/skills) (`security-best-practices`, `security-threat-model`) | `49f948faa9258a0c61caceaf225e179651397431` | not declared at the repository root | Guidance and fix etiquette; repository-grounded threat-model shape with attacker non-capabilities and clarifying questions |
| OWASP ASVS 5.0, Top 10:2025, API Security Top 10, WSTG, Cheat Sheet Series | current releases | CC-BY-SA | Referenced, not copied |

The workflow design also follows the user's programming knowledge base notes on
evidence-driven security review agents, finding evidence and confidence,
layered CI scanning, framework security boundaries, cross-tenant authorization
tests, and agent trust boundaries.
