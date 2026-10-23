---
name: cdk-infra-testing
description: Create, refactor, review, or explain infrastructure tests for AWS CDK apps, including CloudFormation assertion tests (Template, Match), offline synth contracts, shell smoke-tool self-tests, and dashboard JSON validation. Use when infrastructure behaviour, CDK configuration, or infra CI checks change.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# CDK Infrastructure Testing

Pair with `aws-cdk-iac` when assertions depend on CloudFormation, ECS, IAM,
networking, assets, or synth behaviour.

## Core preferences

- Prefer behaviourally meaningful CloudFormation assertions
  (`Template.fromStack`, `hasResourceProperties`, `resourceCountIs`, `Match`)
  over snapshots.
- Assert deployment contracts, not incidental generated details such as logical IDs.
- Keep CI synth offline (`--no-lookups`, with explicit context) and free of credentials.
- Use fake account, Region, repository, and digest values for contract tests.

## What to test

For stacks, prefer focused assertions for:

- public ingress boundaries, including rejecting `0.0.0.0/0` where it is not intended;
- presence or absence of NAT gateways and the required VPC endpoints;
- load balancer scheme, listeners, target groups, and health-check paths;
- task definition shape, container environment, image source, and logging;
- IAM separation between execution and task roles, with no wildcard actions or resources;
- optional context flags and their effect;
- outputs consumed by smoke tooling, dashboards, or other stacks.

For scripts: `bash -n` syntax checks, deterministic `--self-test` paths,
argument and environment validation, bounded polling, and clear timeout messages.

For dashboards: JSON syntax, required panels and datasource inputs, and stable
metric names, labels, and filters.

## Anti-patterns

- Asserting every generated logical ID.
- Broad snapshots of large templates that nobody realistically reviews.
- CI checks that need AWS credentials on public pull requests.
- Tests that depend on sibling repositories.

## Workflow

Build, run the assertion tests, then synth with the contract context values,
using the repository's scripts. Run the full CI script before handing back.
