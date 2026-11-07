# Runtime Validation

Tested on 2026-10-24 with zod 4.6 and TypeScript `strict`. Check the current
library documentation before relying on version-specific behaviour.

## Schema first: one source of truth

```ts
import * as z from 'zod';

/** Postal address where a parcel is collected or delivered. */
export const AddressSchema = z.strictObject({
  street: z.string().min(1),
  city: z.string().min(1),
  postcode: z.string().min(1),
  country: z.string().length(2),
});

/** A confirmed request to move one parcel. */
export const BookingSchema = z.strictObject({
  id: z.string().min(1),
  weightGrams: z.number().int().positive(),
  pickup: AddressSchema,
  dropoff: AddressSchema,
});

export type Address = z.infer<typeof AddressSchema>;
export type Booking = z.infer<typeof BookingSchema>;
```

Use the namespace import, `import * as z from 'zod'`. Named imports such as
`import { object, string } from 'zod'` put type-word names into the module, which
the naming rules in `typescript-style` forbid.

## Error messages: fields, not values

```ts
const UNKNOWN_KEYS_FIRST = (issue: z.core.$ZodIssue): number =>
  issue.code === 'unrecognized_keys' ? 0 : 1;

/**
 * Describes validation issues by field path, unknown keys first.
 *
 * Never includes input values, so the message is safe to log.
 */
export function describeIssues(error: z.ZodError): string {
  const ordered = [...error.issues].sort((a, b) => UNKNOWN_KEYS_FIRST(a) - UNKNOWN_KEYS_FIRST(b));

  return ordered
    .map((issue) => {
      const field = issue.path.join('.') || '(root)';

      if (issue.code === 'unrecognized_keys') {
        return `${field}: unknown keys ${issue.keys.join(', ')}`;
      }

      return `${field}: ${issue.message}`;
    })
    .join('; ');
}

/**
 * Parses an untrusted JSON value into a booking.
 *
 * @throws `Error` naming each invalid field, without echoing values.
 */
export function parseBooking(input: unknown): Booking {
  const result = BookingSchema.safeParse(input);

  if (!result.success) {
    throw new Error(`invalid booking: ${describeIssues(result.error)}`);
  }

  return result.data;
}
```

For input with an extra root key `secret`, an extra nested key, a negative weight,
and a three-letter country code, the formatter produces this message (verified):

```text
invalid booking: pickup: unknown keys extra; (root): unknown keys secret;
weightGrams: Too small: expected number to be >0;
pickup.country: Too big: expected string to have exactly 2 characters
```

Behaviour this relies on, all verified:

- zod reports unknown keys as `unrecognized_keys` issues, *after* the field issues,
  so the formatter sorts them first.
- Default messages describe the expected type or constraint, not the received
  value. Custom messages and error maps must keep that property. Do not enable
  options that copy the input into issues.
- Unknown key *names* are echoed. They are structure rather than values, but cap or
  truncate them if attackers can send arbitrary keys into logs.

## Hand-written validators

When the repository does not allow a schema dependency, keep a single source of
truth and say why in the module doc comment:

```ts
/**
 * Booking parsing without a schema library: this package must stay dependency-free.
 */
const BOOKING_KEYS = ['id', 'weightGrams', 'pickup', 'dropoff'] as const;

type BookingKey = (typeof BOOKING_KEYS)[number];

// Fails to compile if Booking gains or loses a key that BOOKING_KEYS does not list.
type KeysMatch = [BookingKey] extends [keyof Booking]
  ? [keyof Booking] extends [BookingKey] ? true : never
  : never;

true satisfies KeysMatch;
```

The check was verified in both directions: a missing key and an extra key each fail
to compile, and it passes `noUnusedLocals` and the recommended typescript-eslint
rules. Then use `BOOKING_KEYS` at runtime to reject unknown keys first, and validate
each field with verb-named helpers (`requireText`, `requirePositiveInteger`).

## Packaging checklist

- The library is in the `dependencies` of every package that imports it at runtime.
- Docker images, function layers, and other unbundled artefacts install production
  dependencies for that package, and a smoke run of the built artefact passes.
- Bundled consumers either include the library in the bundle or deliberately mark
  it external and install it.
