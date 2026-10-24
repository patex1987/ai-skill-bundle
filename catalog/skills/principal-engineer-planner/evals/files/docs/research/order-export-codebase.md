# Research: Order Export

Revision: working tree, fixture.

- `OrderRepository.findByCustomer(customerId, cursor, limit)` pages by cursor;
  ordering is by `createdAt`, which is not unique.
- The job queue (`jobs/queue.ts`) delivers at least once and redelivers a job
  whose worker does not acknowledge within 5 minutes.
- Export limits are configured in `config/exports.json`.
- No object storage client exists yet; the e-mail service uploads attachments
  through a shared `StorageClient` in another package.
