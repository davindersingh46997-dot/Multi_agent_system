# Feature 10: Durable Orchestration and Task History

## Goal

Make long-running project tasks recoverable and observable, with explicit state transitions, checkpointing, cancellation, idempotency, and per-task audit history.

## Current state

- Project tasks persist in SQL, but `brain\api\tasks_api.py` dispatches them through FastAPI `BackgroundTasks`; `brain\services\task_service.py` runs the work.
- Standalone file generation has a separate SQL-backed queue, claim token/lease, worker loop, stale-lease recovery, and artifact cleanup.
- Startup uses SQLAlchemy `Base.metadata.create_all` in `brain\main.py`; migration-managed schema evolution is not present.
- Do not merge the two workflow state machines merely to share infrastructure.

## Implementation steps

1. Specify separate typed state machines for project tasks and generation tasks. Include `queued`, active stage(s), `awaiting_clarification`, `awaiting_approval`, `completed`, `failed`, `blocked`, and `cancelled` as applicable.
2. Define allowed transitions centrally and reject illegal or stale transitions. Record transition actor, timestamp, task version, and reason.
3. Select a durable worker/queue based on deployment needs. Start with the current SQL lease pattern only if concurrency and atomic-claim semantics are proven for the production database; otherwise use an operated queue such as Redis-backed jobs with documented persistence.
4. Add schema migrations and remove production dependence on startup `create_all`. Keep a rollback/backup strategy and test upgrades from existing SQLite and production database schemas.
5. Use atomic claims, leases/heartbeats, attempt counters, bounded retries, idempotency keys, and dead-letter/blocked states. Ensure a worker crash cannot duplicate an applied side effect.
6. Persist checkpoints at safe boundaries (analysis, plan, patch, validation, review, approval, Git operation). Resume only when referenced input hashes and authorization are still valid.
7. Add cancellation requests and cooperative checks before/after provider calls, tool calls, validation, and side effects. Record cancellation outcome and clean worker resources.
8. Store task events and redacted execution records separately from the current summary. Bound retention, payload size, and access by owner.
9. Expose stable status, event history, retry, cancellation, and resume APIs. Use transactional outbox/event delivery if browser push notifications are later added.
10. Test shutdown, stale workers, duplicate submissions, retries, partial provider failures, and exactly-once-or-idempotent side effects.

## Acceptance checks

- Restarting API and worker processes does not lose accepted tasks or corrupt state.
- State transitions are validated and retained as history; terminal and waiting states are distinguishable.
- Duplicate submissions and worker retries do not duplicate file writes, commits, or artifacts.
- A task cannot resume against changed repository evidence or expired approval.
- Migration and recovery procedures are tested, not merely documented.

