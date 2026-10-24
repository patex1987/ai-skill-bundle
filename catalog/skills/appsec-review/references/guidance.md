# Guidance Mode

Use guidance mode for security questions, design reviews, secure-by-default
implementation help, and explanations. The answer stays in the conversation.
Write files only when asked.

## Answer shape

1. **Context:** what in this repository the question touches, with file
   references. Say so when the repository has nothing relevant.
2. **Recommendation:** the default to adopt, stated plainly.
3. **Why, and the main trade-off:** what it protects against, what it costs,
   and when the alternative is the better choice.
4. **How to verify:** the test or check that proves the control works,
   including a denial case.
5. **Sources:** primary references for anything version-sensitive, such as
   standards, framework documentation, or cloud provider documentation.

Keep it short. Give one recommendation with its reasoning, not a survey.
Respect project decisions recorded in the repository. If a decision weakens
security, explain the risk once and suggest documenting the exception rather
than arguing.

## When to check current sources

Security guidance ages quickly. Verify against primary sources before answering
when the topic involves:
- specific library, framework, or cloud-service behaviour or defaults
- token, cookie, or browser behaviour
- standards versions (OWASP Top 10:2025, ASVS 5.0, API Security Top 10, the
  LLM Top 10)
- vulnerability advisories
- tool flags

Use requirement IDs only from the official release you checked. Leave a mapping
blank rather than inventing an ID.

## Primary references

| Topic | Start with |
|---|---|
| Control requirements and audit ledgers | OWASP ASVS 5.0 (versioned requirement IDs) |
| Risk categories for discussion | OWASP Top 10:2025, OWASP API Security Top 10 |
| Testing procedure | OWASP Web Security Testing Guide |
| Implementation advice per control | OWASP Cheat Sheet Series (authentication, authorization, session management, SSRF prevention, secrets management, CSRF, XSS prevention, file upload, logging, AI agent security) |
| LLM and agent systems | OWASP Top 10 for LLM Applications, the OWASP AI Agent Security Cheat Sheet |
| Supply chain | SLSA, OpenSSF Scorecard, GitHub Actions security hardening guide |
| Cloud | The provider's security best-practice and IAM documentation |
| Framework behaviour | The framework's security documentation for the version in the lockfile |

## Common questions and the usual default

These are starting points to adapt to the repository's actual architecture.

- **Where to enforce authorization:** authenticate globally, and authorize per
  operation at the service or data-access layer with the resource in hand.
  Gateway and middleware checks are coarse filters. UI checks are not
  security.
- **Multi-tenancy:** derive the tenant from the verified identity and carry it
  through every query, cache key, object key, queue message, and log. Test with
  two synthetic tenants, and assert both denial and non-mutation.
- **Browser tokens:** for sensitive applications, keep OAuth tokens on the
  server (backend-for-frontend) with an `HttpOnly` session cookie. A public
  SPA client uses Authorization Code with PKCE and short-lived tokens.
- **JWT validation:** pin the issuer, audience, algorithms, and key source.
  Check expiry and token type. Keep tokens lean and look up entitlements on
  the server.
- **Secrets:** use a managed secret store or workload identity, give secrets
  short lifetimes, never put them in images or frontend bundles, and rotate on
  exposure.
- **Webhooks:** verify the signature over the raw body, check the timestamp
  window, process idempotently, and keep the endpoint narrow.
- **File uploads:** apply size limits, use generated storage names, serve
  uploads from a separate origin or as attachments, and scan or transform
  before rendering.
- **Outbound requests from user input:** use an allowlist of destinations,
  resolve and check the address, disable or re-check redirects, and route
  through an egress proxy when it matters.
- **CI security:** use least-privilege tokens, cloud access through OIDC, SHA
  pinning, no secrets on untrusted triggers, and scanners as a separate job.
  See [scanners](scanners.md).
- **AI features with tools:** give tools narrow capabilities, take identity and
  approval from application state, keep credentials outside the model's reach,
  and treat model output as untrusted input. See the `ai-and-agents` class in
  [attack surfaces](attack-surfaces.md).

## Threat model (when asked)

Produce a concise, repository-grounded model rather than a generic checklist:

1. **Scope and system model:**
   - components, data stores, and integrations, with file evidence
   - how the system runs
   - which parts are runtime vs. CI, dev, or test
2. **Assets:** credentials, personal data, integrity-critical state, money, and
   availability-critical components.
3. **Trust boundaries:** concrete edges between components. For each, note the
   protocol, authentication, authorization, and validation.
4. **Actors and capabilities:**
   - realistic attackers given the exposure
   - what each attacker **cannot** do, to avoid inflated ratings
5. **Abuse paths:** a small number of high-quality paths. For each: attacker
   goal → entry point → boundary → asset, with likelihood and impact
   (low/medium/high) and a short justification.
6. **Existing vs. recommended mitigations:**
   - existing controls, with evidence
   - recommended controls, tied to a specific location and control type
7. **Assumptions and questions:** list the assumptions that change the
   ranking. Ask the user one to three targeted questions (deployment and
   exposure, data sensitivity, tenancy, identity provider) before finalizing.

Write the model to a file only when the user asks, at the path they choose.
