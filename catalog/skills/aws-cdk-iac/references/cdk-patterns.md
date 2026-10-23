# AWS CDK Patterns And Review Notes

This reference is a compact checklist for CDK work.

## Construct Choice

Use the construct level that matches the job:

- L1: exact CloudFormation control.
- L2: normal resource modeling with ergonomic CDK APIs.
- L3: common patterns when hiding detail is acceptable.

For ECS and sidecar-telemetry (for example ADOT) stacks, prefer explicit L2 composition until the first
deploy works. This keeps VPC, endpoint, security group, ALB, ECS, IAM, and log
resources reviewable.

## Naming

Prefer generated physical names unless a stable name is useful for humans or an
external contract.

Good:

```typescript
new logs.LogGroup(this, 'AppLogGroup', {
  retention: logs.RetentionDays.ONE_WEEK,
});
```

Acceptable with a documented reason:

```typescript
new logs.LogGroup(this, 'AppLogGroup', {
  logGroupName: `/${projectName}/${environmentName}/${serviceName}/app`,
  retention: logs.RetentionDays.ONE_WEEK,
});
```

Tradeoff: explicit names are easier to find in the AWS console, but they can
block parallel stacks and can make replacement harder.

## Config Boundary

Prefer a typed platform config:

```typescript
export interface PlatformConfig {
  readonly allowedIngressCidr: string;
  readonly maxAzs: 1;
  readonly enableEcsExec: boolean;
}
```

Avoid scattered context reads:

```typescript
// Avoid this inside every resource block.
this.node.tryGetContext('allowedIngressCidr');
```

## Networking

Review these edges explicitly:

```text
internet -> public ALB -> private ECS task -> AWS service endpoints
```

For no-NAT private ECS tasks that pull from ECR and write logs:

- S3 gateway endpoint
- ECR API interface endpoint
- ECR Docker interface endpoint
- CloudWatch Logs interface endpoint

Add `ssmmessages` only when ECS Exec is enabled. Add X-Ray, AMP, STS, Secrets
Manager, or SSM only when the current wave uses those services.

## Security Groups

Prefer source security groups over CIDRs for internal edges:

```typescript
serviceSecurityGroup.addIngressRule(
  albSecurityGroup,
  ec2.Port.tcp(3000),
  'Only the ALB can call the application container',
);
```

Use CIDR rules only at real network boundaries, such as developer access to a
public ALB:

```typescript
albSecurityGroup.addIngressRule(
  ec2.Peer.ipv4(allowedIngressCidr),
  ec2.Port.tcp(80),
  'Demo HTTP access restricted by explicit source CIDR',
);
```

## IAM

Prefer resource-specific grant helpers:

```typescript
bucket.grantRead(taskRole);
```

When adding explicit policy statements, explain why a grant helper is not
available or not sufficient.

For ECS:

- Execution role: image pulls, log driver, secret injection.
- Task role: application or sidecar AWS API calls.

## Docker Image Assets

CDK Docker assets hash the build context. Keep `.dockerignore` current.

Application images built by other pipelines should be referenced by digest,
not built as assets.

Keep generated output, local AI tool state, and unrelated files out of Docker
build contexts when they are not needed for the image.

## Tests

Assert stable intent, not incidental generated details.

Useful CDK assertions:

```typescript
template.resourceCountIs('AWS::EC2::NatGateway', 0);
```

```typescript
template.hasResourceProperties('AWS::ElasticLoadBalancingV2::TargetGroup', {
  HealthCheckPath: '/health',
  TargetType: 'ip',
});
```

```typescript
template.hasResourceProperties('AWS::ECS::Service', {
  LaunchType: 'FARGATE',
  EnableExecuteCommand: false,
});
```

Avoid snapshot-only tests for large templates. They are useful as a smoke net
but weak as design documentation.

## Deployment Review

Before `cdk deploy`, review:

- target AWS account and region;
- public ingress CIDRs;
- whether the stack creates public endpoints;
- whether NAT gateways, VPC endpoints, ALBs, AMP, AMG, or log groups incur cost;
- IAM broadness;
- removal policies and data persistence;
- how to destroy or roll back.

Run `cdk diff` through the repository's script with the same context values
used for synth, and review it before any deploy the user has authorised.
