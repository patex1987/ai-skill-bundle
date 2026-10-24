# Attack Surfaces

Each class lists what to trace and the questions that settle it. Choose classes
from the architecture. Do not walk the whole list for a small change. In a full
audit, the class names below are the `attack_class` values in the coverage
ledger.

## access-control

- **Object-level authorization:** every read, update, delete, list, search,
  export, and bulk path binds the resource to the verified principal and
  tenant. Check nested IDs, foreign keys in the body, and IDs in background-job
  payloads.
- **Function-level authorization:** admin and maintenance routes, feature flags
  used as permissions, GraphQL fields and mutations, and RPC methods.
- **Tenant context:** taken from the verified identity, never from a header,
  path, or body the caller sets. Check that caches, search indexes, queues,
  object keys, and logs are partitioned the same way.
- **Policy and query disagreement:** the policy check approves one record,
  while the query, update, or join touches another.
- **Self-service escalation:** users granting themselves roles, joining
  organizations without an invite, or changing their own tenant or owner fields
  through mass assignment.
- **Derived copies:** exports, backups, analytics, audit search, and caches
  that keep data after access was revoked or the record was deleted.

## authentication-and-session

- **Token validation:** the verifier pins the issuer, audience, algorithm,
  key source, expiry, and token type. Untrusted token content must not select
  the issuer, JWKS URL, or algorithm. ID tokens must not be accepted as access
  tokens.
- **OAuth and OIDC:** check `state` and PKCE binding, exact redirect URI
  matching, `nonce` on ID tokens, the client type (public vs. confidential),
  and whether the code is redeemed on the server.
- **Sessions:** random identifiers, rotation at login and on privilege change,
  server-side invalidation at logout and password reset, and `HttpOnly`,
  `Secure`, and `SameSite` cookie attributes set for the deployed scheme.
- **Account flows:** reset tokens (single use, expiry, bound to the account),
  email-change and account-linking collisions, MFA enrollment and step-up that
  can be skipped, and recovery paths that bypass MFA.
- **Browser token storage:** access or refresh tokens readable by JavaScript
  are exposed to any script in the origin. Prefer a backend-for-frontend
  pattern with a session cookie for sensitive applications.

## injection

- SQL and NoSQL built from strings. Check raw-query escape hatches in ORMs and
  dynamic `ORDER BY` or column names.
- OS commands (`shell=True`, `exec`, backticks, `child_process.exec`) and
  argument injection into CLIs (`--` handling, leading-dash values).
- Templates: server-side template injection, and rendering of user content
  with auto-escaping turned off.
- XSS sinks in the frontend: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`,
  unsafe Markdown rendering, and `javascript:` URLs in links.
- Header and log injection, but only when it changes behaviour (response
  splitting, forged audit records). Plain log text is not a finding.
- LDAP, XPath, regular-expression construction, and GraphQL query
  construction from user input.

## deserialization-and-parsing

- Unsafe loaders: `pickle`, `yaml.load` without a safe loader, Java and .NET
  object deserialization, and `eval` or `Function` on data.
- XML external entities and entity expansion.
- Archive extraction (zip slip, symlinks in archives, decompression bombs).
- Parser differentials between two components that read the same input
  differently (URL parsers, JSON duplicate keys, multipart boundaries, path
  normalization).

## ssrf-and-outbound

- User-influenced scheme, host, or port in server-side requests, webhooks,
  importers, image proxies, PDF renderers, and link previews.
- Redirect following, DNS rebinding, IPv6 and decimal IP forms, and access to
  metadata addresses (`169.254.169.254`, `fd00:ec2::254`).
- Credentials forwarded to an origin other than the intended one after a
  redirect.
- Allowlists checked on the string instead of the resolved address.

## files-and-paths

- Path traversal on read, write, and delete. Check the normalization order and
  symlink following.
- Upload type and size limits, content sniffing, serving uploads from the
  application origin, and files that are later executed or rendered.
- Temporary files with predictable names, and permissive file modes on
  secrets.

## secrets-and-crypto

- Hardcoded credentials, keys in frontend bundles or mobile apps, and secrets
  in images, logs, error messages, traces, or CI output.
- Purpose-appropriate primitives: password hashing (Argon2id, scrypt, bcrypt),
  authenticated encryption, CSPRNG for tokens, and constant-time comparison
  for secrets.
- TLS verification turned off, certificate pinning bypassed, and key reuse
  across environments.
- Key and secret lifecycle: rotation, revocation, and what happens when a
  secret store is unreachable (fail closed or fall back to a default?).

## business-logic

- Server-side computation of prices, totals, quotas, and entitlements. The
  client never decides them.
- State machines: skipped steps, replayed steps, transitions from terminal
  states, and cancellation and refund races.
- Idempotency of payments, webhooks, and queue consumers. Duplicate delivery
  must not double the effect.
- Concurrency: double-spend and check-then-act races on limited resources.
  Report these only with a concrete interleaving.
- Abuse of legitimate features: invitations, sharing links, exports, and
  notifications used to reach other users' data.

## web-platform

- CSRF on cookie-authenticated, state-changing requests, including
  method-override tricks and GET requests with side effects.
- CORS: reflected origins with credentials, and `null` or wildcard
  subdomain trust.
- Caching: private responses cached by shared caches or CDNs, unkeyed headers
  that change responses, and cache deception through path suffixes.
- `Host` and `X-Forwarded-*` trust used to build links (password reset) or to
  make access decisions.
- Open redirects that feed token or code flows. Plain open redirects are low
  severity.
- Clickjacking for sensitive one-click actions, and `postMessage` handlers
  without an origin check.

## api-and-graphql

- Missing authorization on resolvers or fields, and introspection exposing
  internal operations (the latter is a hint, not a finding).
- Unbounded query depth, breadth, aliases, and batching that give one caller
  outsized cost.
- Mass assignment through DTOs and partial-update endpoints.
- Excessive data in responses: serializing whole entities instead of response
  models.

## ci-cd-and-supply-chain

- Untrusted code in privileged workflows: `pull_request_target` or
  `workflow_run` that checks out or runs head code with secrets or a write
  token.
- Expression injection: `${{ github.event.* }}` interpolated into `run:`
  scripts. The fix is passing values through environment variables.
- Token scope: default `GITHUB_TOKEN` permissions, `id-token: write` on jobs
  that run untrusted code, and OIDC trust policies with wide `sub` patterns.
- Pinning: third-party actions by commit SHA, container images by digest, and
  install scripts from mutable URLs.
- Cache and artifact poisoning between untrusted and trusted jobs.
- Dependencies: namespace or registry confusion, typosquats, install-time
  scripts, and new dependencies with a single maintainer or no maintenance.
- Release and promotion: whether the artifact deployed is the one that was
  tested (digest-bound promotion) and who can approve or trigger deploys.
- Agent automation in CI: model output passed to `eval` or a shell, issue or
  PR text reaching an agent that has write tokens, and wildcard tool
  allowlists.

## cloud-and-infrastructure

- IAM: wildcard actions or resources, `iam:PassRole` without conditions, trust
  policies that admit broad principals, and deploy roles that can modify their
  own permissions.
- Indirect authority: what the deployer can make AWS do for it (stack
  execution roles, Lambda and ECS task roles, service-linked actions).
- Network reachability: public load balancers and security groups, management
  ports, internal services without authentication behind "it is private"
  assumptions, and metadata endpoint access from workloads.
- Data stores: public buckets, overly broad KMS key policies, and database
  exposure, backups, and deletion protection.
- Events and messaging: resource policies on buses and queues that accept
  other accounts, consumers that trust event fields as identity, and poison
  messages and retries.
- Containers: privileged mode, host mounts, the Docker socket, running as
  root, and secrets in build arguments or layers.
- Secrets in environment variables, task definitions, or synthesized
  templates.

## ai-and-agents

Apply when the system calls a model, runs agents, or exposes tools (including
MCP).

- **Indirect prompt injection:** retrieved documents, web pages, emails,
  tickets, and tool output reach a model that can act. The finding is the
  authority the injected text gains, not the injection itself.
- **Excessive agency (confused deputy):** tools that act with the service's
  credentials instead of the requesting user's permissions. Generic
  `http_request` or shell tools are a much wider surface than a narrow
  `send_message(channel, text)`.
- **Authorization in the model's hands:** `approved: true`, role, or tenant
  values accepted from model-produced arguments. Identity and approval must
  come from trusted application state.
- **Approval binding:** approval must be bound to the exact action, target, and
  parameters, with expiry and replay protection. A changed proposal needs a
  new approval.
- **Unsafe output handling:** model output rendered as HTML or Markdown with
  images and links (data exfiltration), executed as code or SQL, or used as a
  file path or URL.
- **Context bleed:** conversation, memory, or retrieval data shared across
  users or tenants. Memory that one user can poison for another.
- **Credential custody:** API keys visible to the model or the sandbox. Prefer
  a broker that adds credentials outside the agent's execution environment.
- **MCP and subagents:** tool and server identity, schema descriptions treated
  as policy, subagents inheriting more authority than the task needs, and
  unbounded delegation loops that spend money.
- **Sandbox boundaries:** a compute sandbox does not limit what valid
  credentials inside it can do. Check egress paths that bypass the proxy.

## data-lifecycle

- Export, backup, and restore paths that widen scope or restore records
  without their access rules.
- Soft-deleted records still reachable through search, caches, or relations.
- Migrations that set permissive defaults on new columns (`is_public`,
  `tenant_id` nullable).
- Personal data in logs, analytics, traces, error trackers, and support
  tooling.
- Retention: deletion requests that miss derived copies or queued work.

## availability (only when in scope)

- One cheap request that causes expensive work for a shared service:
  regular-expression backtracking, decompression, image or PDF processing,
  unbounded pagination, or GraphQL cost.
- Missing timeouts on outbound calls in request paths, unbounded queues, and
  per-tenant fairness.
- Panics or unhandled errors on attacker-controlled input that crash a shared
  worker.
- Spend amplification: model calls, paid APIs, or email and SMS triggered
  without limits.
