# Feature 1: Authentication and Project Access

## Goal

Keep every task, project, upload, index result, proposed change, and generated artifact confined to its authenticated owner. Make the current local account and path model safe to operate as a multi-user service.

## Current state

- Registration, login, and current-user routes exist under `brain\api\auth_api.py`.
- JWT and password handling are under `brain\auth\`; project and task APIs use the authenticated user dependency.
- Project roots resolve under `PROJECTS_ROOT/user-<owner-id>/` through `brain\core\workspaces.py`.
- Generated files and project tasks use owner-filtered queries. Existing API tests cover several ownership checks.
- Production secret checks exist in `brain\core\settings.py` and startup in `brain\main.py`.
- Deployment-grade account recovery, role-based access, rate limits, and security event auditing are not evidenced by the inspected routes.

## Implementation steps

1. Inventory every API and service path that reads or mutates a user-owned resource. Document the required owner/project/task relationship for each access.
2. Keep authentication dependencies at the route boundary and enforce project/task ownership in database queries before reading files, accepting uploads, or making tool calls.
3. Centralize project-root resolution. Verify containment after resolving paths, reject symlinks/junctions and path escapes, and account for path replacement races before writes.
4. Add database constraints and indexes for ownership and foreign-key relationships. Keep generated artifacts and project uploads separate and use server-generated storage names.
5. Require stable production signing secrets and database configuration at deployment start. Never return secret values or provider credentials in API responses.
6. Add configurable login, task-submission, upload, and per-owner concurrency limits; return consistent `401`, `403`/`404`, `409`, and `429` responses without confirming another user's resource exists.
7. Add security audit events for login outcomes, project access, approval decisions, and administrative actions, with sensitive values redacted.

## Acceptance checks

- A user cannot list, read, update, cancel, download, approve, or apply another user's resource by guessing its ID.
- Traversal paths, symlinks, junctions, and path swaps cannot escape the assigned project root.
- Missing or weak production signing configuration prevents startup; development behavior remains explicitly development-only.
- Tests cover endpoint and service-level authorization, upload path containment, path race boundaries, and rate-limit responses.

