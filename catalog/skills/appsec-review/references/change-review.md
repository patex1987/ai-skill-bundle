# Change Review

Review what a PR, branch, commit range, or working-tree diff introduces or newly
exposes. Read the rest of the repository for context, but report only on the
change.

## 1. Resolve the range

State the exact range in the report. Typical commands, all read-only:

```sh
git status --short                                  # uncommitted work in scope?
gh pr view <number> --json baseRefName,headRefOid   # PR base (if the user named a PR)
git merge-base origin/<base> HEAD                    # base commit for a branch
git diff --name-status <base>...HEAD                 # changed files
git log --oneline <base>..HEAD                       # commits in the range
git diff <base>...HEAD -- <path>                     # per-file patch
git diff HEAD                                        # uncommitted changes, if in scope
```

If the base is ambiguous (no upstream, several candidate branches), use the
repository's default branch. Name the assumption, or ask when the answer would
change the scope. Do not fetch, check out, or rebase unless the user asked. Read
the version at the base with `git show <base>:<path>` instead.

## 2. Triage files by risk

Drop before analysis:
- lockfiles whose resolved packages did not change
- minified bundles, source maps, vendored copies
- generated code with a generator marker
- snapshots and binary assets

Keep database migrations even when they are marked as generated.

| Risk | Triggers | Depth |
|---|---|---|
| High | Authentication, sessions, tokens, authorization, tenancy, crypto, secrets, money or quotas, file upload and path handling, outbound requests, deserialization, template rendering, raw queries, CI workflows, IAM/IaC, container and runtime config, agent tools and prompts with authority, **removed or weakened validation** | Full trace, blast radius, history, falsification |
| Medium | New public endpoints or message consumers, business-state transitions, new dependencies, error handling and logging changes, CORS/cookie/header config | Trace the entry point and its controls |
| Low | Pure UI copy, comments, tests, docs, formatting | Skim for secrets and accidental exposure only |

Classify by what the code touches, not by line count. A two-line change to a
guard is high risk. A security-sensitive path always gets the full treatment,
even in a tiny PR.

Scale depth to size:
- Small change: read every dependency of the high-risk files.
- Medium change: follow one hop of callers and callees, starting from the
  high-risk files.
- Large change: trace only the critical paths, and say in the coverage section
  which medium-risk files got a surface read.

## 3. Build context for high-risk hunks

- **Entry points:** which routes, resolvers, consumers, jobs, CLI commands, or
  workflow triggers reach this code? With what identity?
- **Controls:** where are authentication, authorization, validation, and
  tenancy enforced for those entry points? Check global ones too.
- **Blast radius:** find callers (`rg -n '<symbol>\('`) and other paths to the
  same effect. A changed helper used by many handlers changes all of them.
- **Removed code:** for deleted checks, read why they existed with
  `git log -L <start>,<end>:<file>` and `git log -S '<snippet>'`. Look for
  regressions of past security fixes.
- **Tests:** does a test cover the changed behaviour, including the denial case?
  Missing coverage on a high-risk path does not make a finding by itself.
  Mention it under coverage, and propose the test with any finding.
- **Contracts:** did the change alter what a downstream component may assume?
  Examples: a field that used to be validated upstream, an ID that used to be
  server-generated, or an event that used to come only from a trusted producer.

## 4. Deterministic checks

1. Look for scanner output for the head commit first (CI artifacts, code
   scanning alerts).
2. If nothing exists and running tools is permitted, run preinstalled scanners
   in diff-aware mode where they support it. Examples are Semgrep
   `--baseline-commit <base>` and Gitleaks over `<base>..HEAD`. See
   [scanners](scanners.md).
3. Record every tool's execution state.

## 5. Candidate handling

- Put every candidate, from your own tracing or from a scanner, through the
  gate in [evidence and severity](evidence-and-severity.md).
- For high or critical candidates, delegate falsification to a fresh context
  before reporting. Give it the claim, the anchors, and the question "what
  prevents this?" Do not give it your reasoning. Keep the candidate only if the
  verifier cannot find a defense.
- A finding in unchanged code is in scope only when the change makes it
  reachable, removes its mitigation, or widens its effect. Say which.

## 6. Verdict

| Condition | Verdict |
|---|---|
| No findings, or only informational notes | **No blocking issues** |
| Only low or medium findings, or needs-validation items without production risk | **Approve with comments** |
| Several medium findings that form a risk pattern, or any likely high finding | **Changes recommended** |
| Any confirmed high or critical finding, or a likely critical one | **Changes required** |

The verdict is advice. Do not approve, request changes, post comments, or push
unless the user asked for that action.

## 7. Re-review of the same change

When reviewing a later revision:
- Read the previous review first. Report each earlier finding as `fixed`,
  `still present`, or `changed`.
- Respect findings the owner resolved or accepted, unless the risk got
  materially worse.
- Evaluate a reasoned disagreement on its merits. Either withdraw the finding
  or explain the evidence that keeps it.
- Review only the new delta in depth, but re-check that earlier fixes were not
  undone.
