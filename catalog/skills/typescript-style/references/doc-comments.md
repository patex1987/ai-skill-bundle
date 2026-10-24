# Doc Comments

TSDoc is the standard comment syntax for TypeScript. It looks like JSDoc, but types
come from the code, so comments describe only behaviour. Editors show these comments
on hover, and documentation generators such as TypeDoc and API Extractor read them.

## What to write

Ask what a caller would get wrong if they had only the signature:

| The signature cannot say | Write |
|---|---|
| Units and ranges | "Timeout in milliseconds, from 1 to 30000." |
| Defaults | `@defaultValue 3` or "Defaults to three attempts." |
| Side effects | "Writes a temporary file and deletes it before returning." |
| Errors the caller should handle | `@throws` with the condition |
| Invariants and ordering | "Call `open` first. Calling it twice is safe." |
| Ownership and lifetime | "The caller must close the returned handle." |
| Why it exists, if not obvious | `@remarks` with one or two sentences |

## Functions

```ts
/**
 * Polls the job until it finishes or the deadline passes.
 *
 * Retries transient errors with exponential backoff. Other errors stop polling
 * immediately.
 *
 * @param jobId - Identifier returned by `startJob`.
 * @param deadlineMs - Absolute deadline as a Unix timestamp in milliseconds.
 * @returns The final job status. Never returns a pending status.
 * @throws `TimeoutError` when the deadline passes before the job finishes.
 */
export async function waitForJob(jobId: string, deadlineMs: number): Promise<JobStatus> {
```

Avoid comments like these:

```ts
/**
 * Waits for job.
 * @param {string} jobId the job id
 * @param {number} deadlineMs the deadline
 * @returns {Promise<JobStatus>} the job status
 */
```

That comment restates the name, repeats the types, and leaves out the unit, the
retry behaviour, and the error.

## Interfaces and options

Document the type in one line, and each property where its name and type leave a
question:

```ts
/** Settings for the alarm that rolls back a deployment. */
export interface RollbackAlarmProps {
  /** Error rate, as a fraction from 0 to 1, that triggers the alarm. */
  readonly errorRateThreshold: number;

  /**
   * Consecutive one-minute periods above the threshold before the alarm fires.
   *
   * @defaultValue 3
   */
  readonly evaluationPeriods?: number;

  readonly serviceName: string;
}
```

`serviceName` needs no comment. A comment such as "The service name." adds nothing.

## Classes and constructors

Document what an instance represents and its lifecycle. Document constructor
parameter properties with `@param` on the constructor.

```ts
/**
 * Caches parsed configuration files by path.
 *
 * Entries never expire. Create one instance for each process run.
 */
export class ConfigCache {
  /**
   * @param readFile - Reads the file at a path. Injected so tests can avoid the file system.
   */
  constructor(private readonly readFile: (path: string) => Promise<string>) {}
```

## Implementation comments

Use `//` comments for reasons the code cannot show:

```ts
// The provider returns 200 with an error body on throttling, so check the body too.
if (response.status === 200 && isThrottled(response.body)) {
```

Avoid comments like these:

```ts
// Loop over the users
for (const user of users) {
```

## Deprecation

Always name the replacement:

```ts
/** @deprecated Use {@link waitForJob}, which supports deadlines. */
```

## Tag reference

| Tag | Use |
|---|---|
| `@param name - text` | A parameter. Use the hyphen, and no `{type}`. |
| `@typeParam T - text` | A generic type parameter, when its role is not obvious |
| `@returns text` | The returned value, when it is not obvious from the summary |
| `@throws text` | An error the caller is expected to handle |
| `@remarks` | Longer explanation, after the summary |
| `@defaultValue value` | The default of an optional property |
| `@example` | A fenced code example, for non-obvious public APIs |
| `@deprecated text` | Deprecation, with the replacement |
| `{@link Symbol}` | An inline link to another symbol |
| `@internal`, `@beta` | API visibility and stability, when the repository uses them |
