# Feature 5: Controlled Code Changes

## Goal

Let coding agents propose precise repository modifications while keeping file access scoped, changes auditable, and application approval-controlled.

## Current state

- `brain\agents\programmer.py` and `brain\services\programmer_service.py` provide project coding behavior.
- `brain\services\task_service.py` gives the programmer narrow FastMCP tools for list, read, search, and propose.
- `brain\tools\workspace_mcp.py` stages changes; `brain\api\tasks_api.py` applies approved changes after checking a hash and current source.
- There is no unrestricted generic file-write or shell tool in the documented project workflow.

## Implementation steps

1. Keep file read/search/propose capabilities in a task-scoped policy gateway. Enforce owner, project, task, allowed root, and remaining tool-call budget on every operation.
2. Use repository-relative paths only. Normalize and resolve paths, reject traversal and symlinks/junctions, and prohibit sensitive/configuration paths according to an explicit policy.
3. Prefer unified patches with expected old-file hashes over whole-file replacement. Validate patch syntax, target path, changed-line limits, and file-size limits before staging.
4. Store immutable proposal versions with task, authoring agent, path, base hash, proposed hash, diff, status, and timestamps. Keep logs from storing secret-bearing full contents.
5. Make application atomic where the filesystem supports it. Re-check the current base hash immediately before application; reject conflicts rather than overwriting concurrent edits.
6. Bind approval to the proposal hash and include a clear diff in the user interface. Any modification creates a new proposal requiring fresh approval.
7. Add rollback metadata or a recoverable backup strategy for applied proposals. Record apply/reject/conflict outcomes as task events.
8. Keep dependency changes and generated configuration changes under stricter approval rules; do not let an agent commit or push as a side effect of patch application.

## Acceptance checks

- Agent tools cannot write outside the assigned project or bypass proposal/approval.
- Tampered diffs, stale base hashes, duplicate approval requests, path aliases, symlinks, and concurrent edits are safely rejected.
- Tests prove approval of one proposal cannot authorize a changed proposal or a different path.
- Applied changes are atomic or fail with the original file intact; outcomes are auditable and recoverable.

