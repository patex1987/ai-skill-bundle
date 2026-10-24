# Scanners and Deterministic Checks

Scanners and AI review answer different questions. A scanner finds known
patterns, advisories, secrets, and misconfigurations cheaply and repeatably. The
reviewer decides reachability, attacker control, and impact, and finds logic
flaws that no rule encodes. Use scanner output as **leads** and put each through
the evidence gate. A clean scan describes only the rules that ran, on the
inputs they saw.

## What each category answers

| Category | Typical tools | Answers | Leaves open |
|---|---|---|---|
| SAST | Semgrep or Opengrep, CodeQL, Snyk Code, language linters (Bandit, ESLint security rules, Clippy) | Does source contain a risky pattern or tainted flow? | Real attacker control, complete defenses, deployment reachability |
| SCA | OSV-Scanner, Trivy (vuln), Snyk Open Source, `npm`/`pnpm audit`, `pip-audit`, `cargo audit`/`cargo deny` | Does a resolved dependency have a known advisory? | Whether the vulnerable function is reachable, and what is actually deployed |
| Secrets | Gitleaks, Trivy (secret), TruffleHog | Is a credential-like string in files or history? | Whether it is valid, who saw it, and whether it was rotated |
| IaC and config | Checkov, Trivy (misconfig/config), KICS, cfn-lint, Snyk IaC | Does a template or manifest violate a policy? | Actual provisioned state and effective cross-account behaviour |
| CI workflows | zizmor, actionlint | Are there injection, permission, trigger, or pinning hazards in workflows? | Whether an untrusted actor can reach the trigger in this repository's settings |
| Image and SBOM | Trivy (image), Grype, Syft | What ships in the built artifact? | Runtime authority and reachability |
| DAST | ZAP baseline or full scan | How does a running target behave on the network? | Untested paths and identities. Needs an owned, isolated target, and is never run on your own initiative |

## Before running anything

1. **Prefer existing results.** Look for CI artifacts, SARIF uploads, or
   code-scanning alerts for the reviewed commit. Consuming them is cheaper and
   matches what the team gates on.
2. **Use only installed, pinned tools.** Never `curl | sh` an installer or pull
   a mutable `latest` image during a review. Scanners are executable
   dependencies too. Malicious scanner releases and retagged actions have
   happened (for example, the Trivy incident in March 2026).
3. **Mind the data flow.** Some tools upload source or dependency lists to a
   service: Snyk (all products), Semgrep `--config auto` and registry rules,
   OSV-Scanner online mode, and Trivy and Grype database downloads. Run them
   only with the user's consent or when CI already does. Turn telemetry off
   (Semgrep `--metrics=off`).
4. **Write outside the repository.** Put reports in the session scratch area or
   the audit output directory, never in the working tree.
5. **Build steps execute code.** `cdk synth`, `npm install`, `pip install`,
   CodeQL database builds, and Gradle or Maven runs execute repository code.
   Run them only in an isolated sandbox, without credentials.

## Typical invocations

These are typical forms as of 2026-10-23, not verified against every tool's
current documentation. Flags change between versions, so run `<tool> --help` on
the installed version first.

```sh
# Semgrep / Opengrep: pinned local or repo-owned rules, diff-aware for change review
semgrep scan --metrics=off --config <rules-dir-or-pack> --sarif --output <out>/semgrep.sarif \
  [--baseline-commit <base>] <paths>

# CodeQL: build a database, then run a query suite (licence depends on repo visibility)
codeql database create <out>/db --language=<lang> --source-root .
codeql database analyze <out>/db <suite> --format=sarif-latest --output=<out>/codeql.sarif

# Trivy: dependency advisories, secrets, and misconfiguration over the filesystem
trivy fs --scanners vuln,secret,misconfig --format sarif --output <out>/trivy.sarif .
#   offline when a database is already cached: add --skip-db-update

# Checkov: IaC; for CDK scan the synthesized templates, not the TypeScript
checkov -d <iac-dir-or-cdk.out> --output sarif --output-file-path <out>

# OSV-Scanner v2: lockfiles and manifests (online by default)
osv-scanner scan source -r . --format sarif > <out>/osv.sarif

# Gitleaks: history for a range, or a directory; always redact
gitleaks git --log-opts="<base>..HEAD" --redact --report-format sarif --report-path <out>/gitleaks.sarif
gitleaks dir <path> --redact --report-format sarif --report-path <out>/gitleaks-dir.sarif

# zizmor: GitHub Actions workflows (offline mode unless online audits are wanted)
zizmor --offline --format sarif .github/workflows > <out>/zizmor.sarif

# Snyk: only with consent or an existing CI integration (uploads data)
snyk test --json > <out>/snyk-oss.json      # dependencies
snyk code test --sarif > <out>/snyk-code.sarif
snyk iac test --sarif > <out>/snyk-iac.sarif
```

## Execution states

Record one state per tool and target. Never collapse them into "clean":

| State | Meaning |
|---|---|
| `PASS` | Ran on the declared input; nothing above the threshold |
| `FAIL` | Ran; reported findings at or above the threshold |
| `WARN` | Ran; findings below the threshold, or only informational ones |
| `ERROR` | Crashed, failed authentication, could not parse the input, or produced no artifact |
| `NOT_RUN` | Not installed, not permitted, or out of scope. Say which |

Exit codes differ by tool. Some exit 0 even with findings unless asked
otherwise (Semgrep without `--error`, Trivy without `--exit-code`). Others use
non-zero for both findings and failures (Snyk: 1 means findings, 2 means
failure, 3 means no supported project). Map them deliberately. A missing or
empty report file is `ERROR`, not `PASS`.

## Triage of scanner output

1. **Normalize.** Read SARIF `runs[].results[]` (rule ID, level, location, and
   message), or the tool's JSON. Group results by rule and root cause.
2. **Filter to scope.** In a change review, keep only results on changed lines,
   or on new or changed dependencies. Report the other results only as a count.
3. **Gate.** For each lead:
   - Is the source attacker-controlled?
   - Is the sink reached on a production path?
   - Does a framework or global defense apply?
   - For SCA: is the vulnerable function used, and is the advisory's version
     range what actually resolves in the lockfile?
4. **Secrets.** Treat a credential that reached git history as exposed even
   after deletion. The fix is rotation plus removal, not only removal. Do not
   test whether it is valid against the live service.
5. **IaC.** Confirm the setting is not overridden elsewhere (another construct,
   stack policy, organization guardrail). Check the effective permission, not
   just the resource's own policy.
6. **Record rejections.** Note why a scanner result was dismissed (for example,
   "server-controlled config" or "test fixture"), so the next run and the team's
   suppression list stay consistent.

## Recommending CI changes

When the user asks how to add scanners to CI:
- Run them in a job without deploy credentials or write tokens, especially
  for fork PRs.
- Pin actions and images by digest, and pin rule packs.
- Upload SARIF for code scanning.
- Baseline existing findings, giving each suppression an owner and expiry.
- Gate on new, high-confidence results rather than the whole backlog.
- Schedule SCA re-scans, because advisories appear without code changes.
- Keep the AI review advisory: deterministic checks and regression tests should
  decide failures, not model prose.
