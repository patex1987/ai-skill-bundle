---
name: aws-cdk-iac
description: Design, implement, review, or explain AWS CDK infrastructure in TypeScript, including construct levels, synthesized CloudFormation, networking and VPC endpoints, IAM, ECS/Fargate, assets, configuration boundaries, synth/diff/deploy safety, and CDK versioning.
metadata:
  routing-tier: deep
  routing-effort: high
---

# AWS CDK IaC

Pair it with `principal-engineer-planner` before non-trivial infrastructure
changes, `typescript` for stack props and config types, and `cdk-infra-testing`
for assertion tests.

## Before you start

Find how this repository runs CDK: the app entrypoint (`cdk.json` `app`), the
package scripts for build, test, and synth, and the required context values.
Run CDK through the repository's scripts or a local `npx cdk`, not a global
`cdk` binary. Record the commands you used.

## Core Mental Model

Teach and reason through the three layers explicitly:

- CDK code: TypeScript constructs and props.
- Synthesized CloudFormation: the template CDK emits.
- Deployed AWS resources: what CloudFormation creates or updates in an AWS account.

When explaining a change, connect the construct to its CloudFormation resource
where practical. For example, `ec2.Vpc` synthesizes VPC, subnet, route table,
route, internet gateway, and endpoint resources; `ecs.FargateService`
synthesizes an `AWS::ECS::Service` with networking, deployment, and load
balancer configuration.

## Current-Information Rule

AWS service behavior, CDK APIs, and package versions change frequently.

Use the installed package types first:

```bash
rg -n "interface FargateServiceProps" node_modules/aws-cdk-lib
rg -n "InterfaceVpcEndpointAwsService" node_modules/aws-cdk-lib
```

When current AWS/CDK facts materially affect the answer, verify with official
AWS/CDK documentation or official package metadata. Prefer:

- AWS CDK Developer Guide
- AWS CDK API reference
- AWS service docs
- npm package metadata for version checks

If AWS MCP documentation tools are available in the active environment, use
them. If they are not available, use official docs or the installed package
types instead. Do not claim MCP tools are available when the current session has
not exposed them.

## CDK Versioning

CDK has two important packages:

- `aws-cdk-lib`: the construct library used by the app code.
- `aws-cdk`: the CLI/toolkit used to synthesize and deploy.

The CLI and construct library no longer need matching version numbers. The
practical rule is: keep the CLI new enough to understand the cloud assembly
schema emitted by the construct library. Newer CLI versions are generally the
safe direction.

Check versions with:

```bash
npm outdated
npm view aws-cdk-lib version
npm view aws-cdk version
npm view constructs version
```

## Construct-Level Guidance

Choose construct level deliberately:

- L1 constructs map directly to CloudFormation resources. Use them when CDK has
  no higher-level construct or when exact CloudFormation control is needed.
- L2 constructs model AWS resources with safer defaults and ergonomic methods.
  Prefer these for most first-party resources.
- L3 pattern constructs are useful for common production patterns, but they can
  hide details that are important for learning, security review, or unusual
  networking.

Explicit L2 composition is often better than an L3 pattern for a first
implementation, for learning, and for security review. Extract custom constructs only after the
resource graph works and the duplication is real.

## Naming Guidance

Avoid explicit physical names unless there is a concrete reason:

```typescript
// Prefer this for reusable stacks.
new logs.LogGroup(this, 'AppLogGroup', {
  retention: logs.RetentionDays.ONE_WEEK,
});
```

Use explicit names only when they are part of a human workflow, external
contract, stable dashboard/search path, or learning/demo requirement. When
choosing explicit names, document the tradeoff: easier inspection versus harder
parallel deployment and possible replacement/name collision issues.

## Configuration Boundaries

Treat CDK context and environment variables as external input.

Use a small typed config boundary instead of scattering `tryGetContext` calls
through a stack:

```typescript
export interface PlatformConfig {
  readonly allowedIngressCidr: string;
  readonly maxAzs: 1;
  readonly enableEcsExec: boolean;
}
```

Normalise once, validate, and pass typed data inward, as you would for an
application's configuration boundary.

## Networking Guidance

Make network intent visible:

- Which subnets are public?
- Which subnets host private compute?
- Is there a NAT Gateway?
- Which VPC endpoints replace NAT for private AWS service access?
- Which security group allows each edge?

For private ECS tasks without NAT, explicitly reason about required endpoints
for the current workload. For image pulls and logs, the usual minimum is:

- S3 gateway endpoint for ECR image layers.
- ECR API interface endpoint.
- ECR Docker interface endpoint.
- CloudWatch Logs interface endpoint.

Add additional endpoints only when the workload actually uses them, such as
`ssmmessages` for ECS Exec, X-Ray for ADOT trace export, or AMP/STS for
Prometheus remote write.

## IAM Guidance

Use the narrowest practical permissions:

- Prefer CDK grant methods when a resource exposes them.
- Keep task execution role and task role responsibilities distinct.
- Avoid `actions: ['*']` and `resources: ['*']` unless there is a documented
  bootstrap or service limitation.
- For ECS:
  - execution role pulls images and writes logs;
  - task role is for application/sidecar AWS API calls.

## Asset Guidance

CDK Docker image assets hash the Docker build context. Keep `.dockerignore`
accurate so docs, generated output, local tool directories, and unrelated
workspaces do not perturb image hashes or slow synth/deploy.

Prefer digest-pinned image references for application images built elsewhere.

## Testing Guidance

Infrastructure tests should assert the behaviorally important CloudFormation
shape, not every generated detail.

Prefer focused assertions for:

- absence of NAT Gateway in the no-NAT path;
- required VPC endpoints;
- ALB scheme, listener, target group, health check path;
- ECS task networking mode and container port;
- security group ingress boundaries;
- context flags such as `enableEcsExec`.

Avoid brittle assertions on generated logical IDs unless the ID itself is the
subject under test.

## Validation Workflow

Use the narrowest useful loop while editing: build (type-check), run the
assertion tests, then synthesise with the required context values. Inspect the
synthesised template for the resources you changed. Use `cdk diff` against a
real environment only when the user has authorised access to it.

## Deployment Safety

Before any real deploy:

- confirm the AWS account and region;
- confirm the stack name;
- run `cdk diff`;
- verify required context values such as `allowedIngressCidr`;
- understand public exposure, IAM, data persistence, and teardown implications.

Never deploy or destroy infrastructure unless the user explicitly asks for that
operation.

## Reference Material

Read [references/cdk-patterns.md](references/cdk-patterns.md) only when deeper pattern examples are useful.
