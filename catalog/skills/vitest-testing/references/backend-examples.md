# Vitest Backend Testing Examples

Use these examples as patterns, not templates to copy blindly.

## Basic Test Shape

```ts
import { describe, expect, it } from 'vitest';

function add(left: number, right: number): number {
  return left + right;
}

describe('add', () => {
  it('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

## Factory Function

```ts
type Booking = {
  id: string;
  customerName: string;
  status: 'CONFIRMED' | 'CANCELLED';
};

function createBooking(overrides: Partial<Booking> = {}): Booking {
  return {
    id: 'booking-1',
    customerName: 'Ada Lovelace',
    status: 'CONFIRMED',
    ...overrides,
  };
}

it('creates a cancelled booking variant', () => {
  const booking = createBooking({ status: 'CANCELLED' });

  expect(booking).toMatchObject({
    id: 'booking-1',
    status: 'CANCELLED',
  });
});
```

Use factories to avoid noisy object setup. `Partial<Booking>` allows each test to override only the fields that matter.

## Fake Implementation

```ts
interface BookingRepository {
  findById(id: string): Promise<Booking | null>;
  findAll(): Promise<readonly Booking[]>;
}

class FakeBookingRepository implements BookingRepository {
  private readonly bookings = new Map<string, Booking>();

  seed(booking: Booking): void {
    this.bookings.set(booking.id, booking);
  }

  async findById(id: string): Promise<Booking | null> {
    return this.bookings.get(id) ?? null;
  }

  async findAll(): Promise<readonly Booking[]> {
    return [...this.bookings.values()];
  }
}
```

Use a fake when stateful behavior matters. Keep the fake intentionally smaller than production infrastructure, but behaviorally honest.

## Stub Implementation

```ts
function createStubRepository(): BookingRepository {
  return {
    async findById() {
      return createBooking();
    },
    async findAll() {
      return [createBooking()];
    },
  };
}
```

Use a stub when the dependency behavior is irrelevant and fixed return values are enough.

## Mock Or Spy

```ts
import { expect, it, vi } from 'vitest';

type EmailSender = {
  sendEmail(to: string, subject: string): Promise<void>;
};

class BookingNotifier {
  constructor(private readonly emailSender: EmailSender) {}

  async notifyCustomer(email: string): Promise<void> {
    await this.emailSender.sendEmail(email, 'Booking confirmed');
  }
}

it('sends a confirmation email', async () => {
  const emailSender: EmailSender = {
    sendEmail: vi.fn(),
  };
  const notifier = new BookingNotifier(emailSender);

  await notifier.notifyCustomer('ada@example.com');

  expect(emailSender.sendEmail).toHaveBeenCalledWith('ada@example.com', 'Booking confirmed');
});
```

This is appropriate because the behavior is the outbound interaction.

## beforeEach

```ts
import { beforeEach, describe, expect, it } from 'vitest';

describe('BookingsService', () => {
  let repository: FakeBookingRepository;
  let service: BookingsService;

  beforeEach(() => {
    repository = new FakeBookingRepository();
    repository.seed(createBooking());
    service = new BookingsService(repository);
  });

  it('returns a booking', async () => {
    await expect(service.getBooking('booking-1')).resolves.toMatchObject({
      id: 'booking-1',
    });
  });
});
```

Use `beforeEach` for fresh mutable state. Avoid hiding important scenario-specific setup there.

## Vitest test.extend Fixtures

```ts
import { expect, test as baseTest } from 'vitest';

const test = baseTest
  .extend('repository', () => {
    const repository = new FakeBookingRepository();
    repository.seed(createBooking());
    return repository;
  })
  .extend('service', ({ repository }) => {
    return new BookingsService(repository);
  });

test('gets a booking through a fixture-created service', async ({ service }) => {
  await expect(service.getBooking('booking-1')).resolves.toMatchObject({
    id: 'booking-1',
  });
});
```

Use this when fixture composition is clearer than repeated setup.

## Fixture Cleanup

```ts
import { expect, test as baseTest } from 'vitest';

type FakeServer = {
  url: string;
  close(): Promise<void>;
};

async function startFakeServer(): Promise<FakeServer> {
  return {
    url: 'http://127.0.0.1:9999',
    async close() {},
  };
}

const test = baseTest.extend('server', async ({}, { onCleanup }) => {
  const server = await startFakeServer();
  onCleanup(() => server.close());
  return server;
});

test('uses a server fixture', ({ server }) => {
  expect(server.url).toBe('http://127.0.0.1:9999');
});
```

Use cleanup for app/server/database lifecycle resources.

## Parameterized Tests

```ts
import { describe, expect, it } from 'vitest';

function isTerminalStatus(status: string): boolean {
  return status === 'CONFIRMED' || status === 'CANCELLED';
}

describe('isTerminalStatus', () => {
  it.each([
    ['CONFIRMED', true],
    ['CANCELLED', true],
    ['REQUESTED', false],
  ])('returns %s for %s', (status, expected) => {
    expect(isTerminalStatus(status)).toBe(expected);
  });
});
```

Use this for compact table-driven tests.

## Testing Errors

```ts
class BookingNotFoundError extends Error {}

async function requireBooking(repository: BookingRepository, id: string): Promise<Booking> {
  const booking = await repository.findById(id);

  if (booking === null) {
    throw new BookingNotFoundError(`Booking ${id} was not found`);
  }

  return booking;
}

it('throws when a booking is missing', async () => {
  const repository = new FakeBookingRepository();

  await expect(requireBooking(repository, 'missing')).rejects.toThrow(BookingNotFoundError);
});
```

Use `toThrow` for sync functions and `rejects.toThrow` for promises.

## Nest Provider Override

```ts
const repository = new FakeBookingRepository();
repository.seed(createBooking());

const moduleRef = await Test.createTestingModule({
  imports: [BookingsCompositionModule],
})
  .overrideProvider(BOOKING_REPOSITORY)
  .useValue(repository)
  .compile();
```

Use this when testing framework wiring while replacing infrastructure dependencies.

## E2E With supertest

```ts
import type { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

describe('GraphQL bookings', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createApp();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('returns bookings', async () => {
    const response = await request(app.getHttpServer())
      .post('/graphql')
      .send({
        query: `{
          bookings {
            id
            customerName
          }
        }`,
      });

    expect(response.status).toBe(200);
    expect(response.body.errors).toBeUndefined();
    expect(response.body.data.bookings).toHaveLength(2);
  });
});
```

Use e2e tests to verify request/response behavior, schema, serialization, and DI together.

## Storytelling Inside Tests

Prefer a descriptive test name first:

```ts
it('rejects the second reservation when the class has one available seat', async () => {
  const repository = new FakeReservationRepository({ capacity: 1 });
  const service = new ReservationService(repository);

  await service.reserve({ userId: 'user-1', classId: 'class-1' });

  await expect(service.reserve({ userId: 'user-2', classId: 'class-1' })).rejects.toThrow(ClassFullError);
});
```

Add a block comment when the story is the point of the test:

```ts
it('does not reserve the last available seat twice', async () => {
  /*
   * This documents the race-sensitive business rule:
   * once capacity is reached, later reservations must be rejected.
   * The fake repository keeps state so the service behavior is tested
   * without asserting private method calls.
   */
  const repository = new FakeReservationRepository({ capacity: 1 });
  const service = new ReservationService(repository);

  await service.reserve({ userId: 'user-1', classId: 'class-1' });

  await expect(service.reserve({ userId: 'user-2', classId: 'class-1' })).rejects.toThrow(ClassFullError);
});
```

Avoid comments that only restate the code.
