# pytest Examples

Use these examples as patterns, not templates to copy blindly.

## Fake Implementation

```python
from uuid import UUID


class FakeRunStore:
    def __init__(self) -> None:
        self._runs: dict[UUID, RunStatus] = {}

    def seed(self, run_status: RunStatus) -> None:
        self._runs[run_status.id] = run_status

    async def get_status(self, run_id: UUID) -> RunStatus | None:
        return self._runs.get(run_id)

    async def save(self, run_status: RunStatus) -> None:
        self._runs[run_status.id] = run_status
```

Use a fake when stateful behavior matters. Keep it smaller than production
infrastructure, but behaviorally honest.

## Lightweight Spy

```python
class EventSpy:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    async def emit(self, event_type: str, payload: dict[str, object]) -> None:
        self.events.append((event_type, payload))
```

Use a spy when the output is an observed interaction and a full fake would be
ceremony. A small explicit spy is often clearer than `Mock` for async tests.

## Mock For A Narrow Failure Path

```python
from unittest.mock import AsyncMock


async def test_translates_client_timeout() -> None:
    client = AsyncMock()
    client.fetch.side_effect = TimeoutError("upstream timeout")

    service = StatusService(client=client)

    with pytest.raises(UpstreamUnavailable):
        await service.get_status()
```

This is acceptable when the test needs a hard-to-trigger exception and the mock
is not replacing meaningful stateful behavior.

## Dependency Override at the App Boundary

```python
def test_create_order_uses_fake_repository() -> None:
    fake_repository = FakeOrderRepository()
    app = create_app()
    app.dependency_overrides[get_order_repository] = lambda: fake_repository

    with TestClient(app) as client:
        response = client.post("/api/v1/orders", json={"sku": "A-1", "quantity": 2})

    assert response.status_code == 201
    assert fake_repository.saved_skus() == ["A-1"]
```

Override dependencies at the composition boundary the app already uses:
FastAPI `dependency_overrides`, a DI container's override registration (for
example `svcs`), or a test registrar. Do not monkey-patch production modules.
When a container caches acquired dependencies, reset or close it before
expecting an override to take effect.

## Folder-Specific conftest

```text
tests/thin_integration/
  conftest.py
  test_agent_run_orchestration.py
  test_canceled_runs.py
```

```python
# tests/thin_integration/conftest.py
import pytest


@pytest.fixture
def in_memory_runtime() -> InMemoryRuntime:
    return create_default_in_memory_runtime()
```

Move this fixture higher only when tests outside `thin_integration/` reuse it.

## Async Event-Driven Test

```python
@pytest.mark.asyncio
async def test_checkpoint_completes_before_cancellation_stops_execution() -> None:
    executor = SingleCheckpointExecutor(checkpoint_duration_seconds=0.1)
    consumer = create_consumer(run_executor=executor)
    consumer_task = asyncio.create_task(consumer.consume_and_execute_loop())

    try:
        await asyncio.wait_for(executor.checkpoint_started.wait(), timeout=2.0)

        await request_cancellation()

        await asyncio.wait_for(executor.checkpoint_completed.wait(), timeout=1.0)
        await asyncio.wait_for(executor.execution_stopped.wait(), timeout=1.0)

        assert executor.execution_cancelled
    finally:
        await consumer.shutdown_execution()
        consumer_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await consumer_task
```

Prefer explicit events and bounded waits over arbitrary sleeps.
