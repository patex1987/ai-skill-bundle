# Report Format

Keep reports target-neutral and safe to share with the owning team. Include
minimal reproduction ideas against local or synthetic fixtures, never live-probe
instructions, real tokens, or customer data.

## Change review

```markdown
## Security review: <PR #n | branch | range>

**Verdict:** <No blocking issues | Approve with comments | Changes recommended | Changes required>
**Reviewed:** `<base>..<head>` (<n> files, <n> high-risk), uncommitted changes <included|excluded>

### Findings
#### 1. <Title> (<severity>, <confirmed|likely>)
- **Location:** `path/to/file.ts:42` (also `other.ts:88`)
- **Actor and preconditions:** <who, what they need>
- **Path:** <entry point> → <missing control> → <effect>
- **Impact:** <concrete result>
- **Why it is real:** <evidence; defenses checked and why they don't apply>
- **Likely depends on:** <the one unverified condition> (likely findings only)
- **Fix:** <smallest change at the last trusted decision point>
- **Regression test:** <test that fails before the fix>

### Needs validation
- <claim>: depends on <exact fact>. Check: <safe owner-side check>.

### Coverage
- Deep-reviewed: <files or areas>. Surface read: <files>. Not reviewed: <files and why>.
- Tools: semgrep PASS (diff-aware) · gitleaks NOT_RUN (not installed) · CI code scanning: <state>
- Rejected candidates: <count> (for example "IDOR in X: scoped by repository query at Y")
```

When nothing survives, replace Findings with "No material issues found in
<scope>". Keep the coverage section and add the residual assumptions.

## Guidance

Use the answer shape in [guidance](guidance.md). Use no finding template unless
the user asked for a review.

## Full audit records (`findings.json`)

An array with one record per root-cause fingerprint:

```json
{
  "fingerprint": "invites-service:missing-org-membership-check",
  "state": "confirmed",
  "severity": "high",
  "title": "Any authenticated user can invite members to another organization",
  "reviewed_commit": "<sha>",
  "locations": [{"path": "src/services/invites.ts", "line": 31}],
  "entry_point": "POST /orgs/:id/invites",
  "actor": "authenticated user of organization A",
  "preconditions": "knows organization B's identifier",
  "source_to_effect": "route param id -> InvitesService.create -> insert without membership check",
  "missing_control": "membership and role check for the target organization",
  "counterevidence_checked": ["global auth guard (authentication only)", "repository query has no org predicate"],
  "impact": "attacker adds themselves to organization B with member role",
  "method": "source trace",
  "observed": null,
  "classification": ["OWASP Top 10:2025 A01", "CWE-639"],
  "fix": "check caller membership and invite permission for :id in InvitesService.create",
  "regression_test": "user of org A receives 403 inviting to org B; org B membership unchanged",
  "coverage_ids": ["POST /orgs/:id/invites::org-membership-check::access-control"],
  "verified_by": "verifier-07"
}
```

The record rules:

- `severity` is present only for `confirmed` and `likely` records.
- A `likely` record adds a `depends_on` field naming the one unverified
  condition.
- A `needs-validation` record has `unresolved_fact` and `owner_check` instead
  of `severity`.
- A `rejected` record keeps `counterevidence` so later runs do not re-raise
  it.
- `observed` is filled only when a check actually ran. Give the environment,
  the result, and a sanitized artifact path.
- `classification` contains only labels you verified. Never invent an ASVS
  requirement ID.

Derive `REPORT.md` and `NEEDS-VALIDATION.md` from these records, as described
in [full audit](full-audit.md).
