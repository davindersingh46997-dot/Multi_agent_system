# Implementation Plan

The repository contains a local MVP with two independent workflows: standalone Hugging Face-backed file generation and project-aware coding tasks. This plan records the generator delivery sequence and the remaining operational work. Project tasks keep their existing auth, retrieval, MCP, and approval contracts.

## Phase 0: Hugging Face Provider Boundary

- Configure the hosted Hugging Face Inference Providers client through server-side settings.
- Keep the access token secret and model identifiers out of browser/API request fields.
- Support one default chat model and per-agent overrides; default provider routing is `auto`.
- Bound provider request timeouts and surface missing configuration, unavailable models, and provider errors as explicit task failures.
- Mock provider calls in tests; use a credentialed smoke test only as a separately configured release check.

**Exit criteria:** settings reject missing token/model configuration clearly; provider errors do not expose credentials; mocked chat-completion calls exercise the selected model and typed JSON output path.

## Phase 1: Typed Multi-Agent File Workflow

- Analyze requirements and pause for user clarification when a critical detail is missing.
- Plan exactly one artifact with a language, filename suggestion, and acceptance criteria.
- Generate complete file contents, have a separate reviewer request bounded corrections, and run a separate validator.
- Enforce typed hand-offs, deterministic stage order, prompt/output limits, and a configured maximum number of review rounds.
- Apply deterministic syntax parsing to JSON and Python. Do not execute generated programs or grant agents filesystem, shell, or arbitrary network tools.

**Exit criteria:** tests prove role order, clarification handling, bounded revisions, complete output, and rejection of invalid JSON/Python without execution.

## Phase 2: Owner-Scoped Generation Tasks and Artifacts

- Persist generation prompts, selected format, status/stage, clarification state, safe filename, error, and timestamps independently of project tasks.
- Claim queued work with a database lease and recover stale tasks after worker restarts.
- Persist one artifact per task with owner, media type, bytes, creation time, and configured expiry.
- Provide authenticated submit, list, status, clarification, retry, cancel, and download operations.
- Make submission idempotent per owner and key; enforce request/output size limits and check ownership on every status or artifact access.
- Delete expired artifacts without exposing artifact storage paths to the client or model.

**Exit criteria:** API tests cover state transitions, restart recovery, idempotent submission, artifact expiry, and cross-user access denial.

## Phase 3: Chat UI Integration

- Keep standalone generation independent of project selection and preserve the supported output format list.
- Poll persisted generation status and show agent stage, clarification prompts, errors, cancellation, and retry actions.
- Download through the authenticated endpoint and display the server-sanitized filename.
- Ensure the UI never requests or exposes model IDs or Hugging Face credentials.

**Exit criteria:** frontend build and targeted lint pass; API-backed UI flow handles progress, failed/clarification states, reload, cancellation, and download.

## Phase 4: Production Reliability and Evaluation

- Move the worker to a separately deployed durable worker/queue when scaling beyond the in-process database-backed worker.
- Add database migrations, deployment-specific queue/storage configuration, metrics, structured redacted logs, quotas, rate limits, and artifact retention operations.
- Track provider capability, latency, quality, and cost for each configured model; test model/provider changes with mocked regression suites and a manual smoke test.
- Add integration tests for timeouts, stale leases, partial provider failures, cancellation boundaries, retries, and application shutdown.
- Consider broader language-specific static validation only after selecting safe parsers. Keep execution disabled unless a separately reviewed sandbox is implemented.

**Exit criteria:** worker and artifact recovery procedures are documented and tested; provider and storage failures have observable, non-success states; all model changes are validated before release.

## Separate Project-Aware Workflow

The existing project task path remains separate. It uses project-filtered lexical retrieval, optional safe image uploads, the project supervisor, MCP tools, and approval-bound file changes. Do not route standalone generation through project retrieval or mutate its API contracts as part of the file-generator work.

Production follow-up for that path remains:

- Replace startup `create_all` with migrations and move project work to durable background execution.
- Add auditable task events, cancellation, quotas, observability, and database backups.
- Do not enable command execution, unattended writes, or remote MCP servers without isolated workers and a separate security review.

## Cross-Cutting Validation

- **Unit:** model configuration, HF adapter response/error mapping, schema parsing, output-format validation, filename sanitization, PDF generation, task state transitions, lease claims, and expiry.
- **Integration:** authenticated API submission/status/download, user isolation, idempotency, worker stage updates, clarification/retry/cancel behavior, and safe static validation.
- **Frontend:** TypeScript/Vite build, targeted ESLint, persisted task reload, progress refresh, and authenticated blob download.
- **Adversarial:** blank/oversized prompts, malformed model JSON, empty/oversized output, path-like filenames, unsafe format mismatch, leaked credentials, cross-user task/artifact IDs, stale worker claims, and provider outage.
- **Regression:** run the existing project-workflow suite to verify RAG, image validation, MCP boundaries, and approved-change behavior remain unchanged.

## Release Gates

- Do not deploy with a blank Hugging Face token/default model; do not put credentials or model selection in the browser.
- Do not treat reviewer approval as proof of execution or test success.
- Do not execute generated source code in the API or worker.
- Do not expose artifact downloads without checking owner and expiry.
- Do not claim production durability/scaling for the in-process worker; move to a separately operated queue before horizontal scaling.
