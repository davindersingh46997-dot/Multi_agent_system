# Feature 12: Operations, Observability, and Scale

## Goal

Operate the platform reliably across API and worker deployments, measure model/task quality and cost, and scale without weakening isolation or changing task outcomes silently.

## Current state

- Configuration is based on Pydantic settings and `.env`; a local SQLite database and in-process generation worker are the default.
- Project tasks use FastAPI background execution; generation has a database-backed worker loop.
- Startup creates tables automatically; production requires a configured non-SQLite database and stable signing secret.
- Metrics, quotas, structured task events, deployment health/readiness, backups, and worker fleet operations are not shown as complete in the inspected files.

## Implementation steps

1. Create deployment profiles for local development, test, staging, and production. Keep secrets in a secret manager in deployed environments; never commit `.env` values.
2. Define API, worker, database, queue, artifact-storage, and optional sandbox boundaries. Run workers separately before horizontally scaling API instances.
3. Add health/readiness checks that distinguish database, queue, provider configuration, and worker health without exposing secret/config values.
4. Emit structured, correlated logs with request/task/worker IDs. Redact authorization headers, tokens, passwords, prompts where sensitive, image bytes, source contents, and provider payloads.
5. Add metrics for queue depth/age, stage duration, provider latency/error/rate limit, retries, cancellation, task outcomes, artifact bytes/expiry, sandbox resources, and per-owner quotas.
6. Define per-user request, concurrency, token, storage, upload, and execution budgets. Enforce server-side and make quota failures explicit.
7. Add alert thresholds and operational runbooks for provider outage, queue backlog, stale leases, database saturation, artifact cleanup failures, and sandbox exhaustion.
8. Configure encrypted backups, retention, restore testing, schema migration sequencing, artifact deletion, and account/data deletion procedures.
9. Track model quality, completion rate, review rejection, validation pass rate, latency, and cost by model/provider/version. Use offline/mocked regression sets before rollout and canary model changes.
10. Document scaling limits and perform load/failure testing before claiming capacity. Keep a single deployment/worker configuration until durable shared storage and atomic claims are verified.

## Acceptance checks

- Operators can determine task and dependency health without seeing sensitive content or credentials.
- Queue, provider, quota, storage, and worker failures become observable non-success states with alerts/runbooks.
- Backup restore, artifact retention/deletion, migration, and worker restart procedures are exercised.
- Capacity claims are backed by measured concurrency, latency, and resource tests.

