# Implementation Plan

The local MVP has implemented configurable model settings, auth, per-user project roots, task APIs/UI, lexical RAG, multimodal image analysis hooks, supervisor roles, FastMCP tools, and approval-bound patch application. The remaining phases below describe hardening and deferred production capabilities; API key and model selection remain intentionally blank.

## Phase 0: Stabilize the Prototype

- Confirm supported Python version and declare actual backend dependencies in project metadata, including currently imported frameworks.
- Repair the existing agent, service, API, and tool contracts; make an in-process read-only task path work before adding model-driven edits.
- Define configuration and secret loading. Remove credentials/default secrets from source and use environment or secret-manager configuration.
- Align frontend and backend registration/login routes, identity fields, token/session behavior, and API base URL.
- Replace startup schema creation with migrations before production data is introduced.
- Add tests for path containment, API schemas, authentication, and service orchestration.

**Exit criteria:** backend starts from documented configuration; registration and login contracts agree; a deterministic service test can inspect a temporary project without modifying it; tests do not require a live model or production database.

## Phase 1: Project and Task Foundation

- Define project ownership and how a project root is provisioned. Never allow a client to select an arbitrary server path.
- Add persistent project, task, event, attachment metadata, approval, and file-change records with migrations and ownership constraints.
- Add authenticated project/task endpoints and stable request/response models.
- Move task execution out of the request handler into a cancellable background worker; persist status transitions and failures.
- Update the client to submit tasks, show status/history, and handle API errors. Keep image upload disabled until its validation and storage policy exist.

**Exit criteria:** users cannot observe or operate on another user's project/task; task status survives refresh and process restart; cancel and failure states are visible and auditable.

## Phase 2: Read-Only Repository Intelligence

- Implement safe project enumeration, file reading, lexical search, and source parsing behind a workspace policy layer.
- Add project indexing jobs, chunking, metadata, embeddings, vector storage, incremental updates, stale-entry deletion, and rebuild support.
- Enforce project/tenant filters before retrieval results leave the retrieval layer.
- Implement repository analyst and supervisor workflow with typed outputs and evidence citations.
- Build evaluation fixtures with small synthetic repositories and expected relevant-file retrieval; include changed-file and deleted-file cases.

**Exit criteria:** retrieval returns current, attributable files/lines from only the selected project; stale index records are detected; read-only tasks cannot mutate files; indexing can be safely repeated.

## Phase 3: Image Evidence and RAG

- Select OCR and vision providers based on privacy, deployment, latency, and cost requirements. Keep these behind provider interfaces.
- Add safe upload validation, bounded image decoding, private storage, attachment metadata, retention/cleanup, and upload limits.
- Extract code/error evidence with confidence and region references; record uncertainty rather than silently repairing OCR text.
- Query the project index with image evidence and reconcile likely source against canonical files.
- Update the client with image attachment, preview/removal, progress, and extraction/retrieval status.
- Evaluate with screenshots containing code, compiler errors, low resolution, cropped lines, multiple languages, and adversarial embedded instructions.

**Exit criteria:** image-derived observations can be traced to the attachment and region; uncertain or conflicting evidence triggers clarification; no image path can directly cause file mutation.

## Phase 4: MCP Tool Gateway and Approved Edits

- Choose and pin an MCP/FastMCP implementation and supported transport after verifying its current API and security properties.
- Define typed tool schemas, server lifecycle, per-task capability grants, policy checks, audit records, and tool-level timeouts.
- Start with list/read/search/diff tools. Add patch proposal and apply only after approval and optimistic hash validation are tested.
- Add UI for reviewing a unified diff and approving/rejecting a specific change set.
- Keep arbitrary shell execution and third-party MCP servers out of the initial production capability set.

**Exit criteria:** every tool is attributable to a task and project; unauthorized paths and tool capabilities are rejected; approval is bound to an exact change-set hash; rejected changes remain unapplied.

## Phase 5: Validation and Multi-Agent Review

- Add an allowlisted validation catalog for project-defined tests, lint, and type checking; run commands in a restricted worker with resource limits.
- Implement programmer and reviewer/test agents with bounded budgets, explicit hand-offs, and no policy bypass.
- Validate patch scope, formatting, and changed-file set before applying or reporting success.
- Report command, exit status, bounded output, and skipped checks. Distinguish tests not run from tests passed.
- Add partial-failure recovery, cancellation, retry policy, and idempotency for queued jobs and tool calls.

**Exit criteria:** successful tasks include the diff and validation evidence; failed checks cannot be reported as passing; edits are limited to approved files and rollback/recovery is documented.

## Phase 6: Production Hardening and Optional Remote MCP

- Add deployment secrets management, database/vector-store backups, retention jobs, observability, rate limits, quotas, and incident procedures.
- Threat-model prompt injection through user prompts, repository content, images, retrieved chunks, and MCP output.
- If remote MCP is required, add administrator-configured server allowlists, isolated credentials, egress rules, reviewed capabilities, and per-integration policy. Do not accept arbitrary endpoints from users.
- Establish model and retrieval evaluations, latency/cost budgets, regression thresholds, and provider fallback behavior.
- Conduct security review before enabling unattended writes or broad command execution.

**Exit criteria:** documented deployment and recovery procedures; security controls verified in integration tests; remote integrations disabled by default and individually governed.

## Cross-Cutting Validation Matrix

- **Unit:** path normalization, policy decisions, chunk boundaries and metadata, upload validation, task state transitions, approval/hash binding, tool schemas.
- **Integration:** FastAPI authorization, database ownership, index filtering, MCP tool policy, patch apply/reject, command sandbox limits.
- **End-to-end:** submit prompt and optional screenshot, retrieve project evidence, review diff, approve/reject, validate, and reload task history.
- **Adversarial:** path traversal and symlink escape, cross-user project IDs, poisoned repository instructions, malicious screenshot text, oversized/deceptive image formats, MCP tool overreach, stale file hashes, command timeout/output exhaustion.
- **Evaluation:** retrieval precision on representative repositories; OCR/code extraction accuracy and uncertainty calibration; patch correctness; reviewer detection of regressions; end-to-end latency and token/cost limits.

## Release Gates

Do not enable file writes until the workspace boundary, ownership checks, diff review, approval binding, audit events, and safe apply behavior pass tests. Do not enable command execution until the isolated worker and allowlist are in place. Do not enable remote MCP until server identity, capability review, credential isolation, network restrictions, and per-task authorization are verified. Do not describe image analysis as code correction until image evidence is reconciled with canonical project source and changes are validated.
