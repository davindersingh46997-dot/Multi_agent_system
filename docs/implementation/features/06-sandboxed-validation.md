# Feature 6: Sandboxed Commands and Validation

## Goal

Run approved tests, linters, type checkers, and other validation safely and reproducibly without granting agents ambient host privileges.

## Current state

- Project task execution does not run shell commands or project tests; the reviewer reports checks rather than claiming they passed.
- Standalone generation validates JSON and Python syntax without executing generated programs.
- The repo documents MCP-backed workspace tools but no sandboxed command runner. This feature requires an explicit isolation design before implementation.

## Implementation steps

1. Specify supported execution profiles and allowed command templates. Start with deterministic test/lint commands discovered from repository manifests; do not expose arbitrary shell strings to models.
2. Run each validation job in a disposable isolated worker/container or equivalent OS sandbox. Never mount the host home directory, production secrets, Docker socket, or unrelated repositories.
3. Mount a task-specific workspace with least-privilege permissions. Decide whether validation sees a read-only snapshot or an approved patch overlay; deny writes to the canonical workspace unless explicitly required by a controlled process.
4. Enforce CPU, memory, process count, wall-clock time, disk, output size, and network-egress limits. Default to no network; allow only documented dependencies/cache endpoints when policy permits.
5. Pin or record toolchain versions and dependency lock state. Do not run install hooks or arbitrary build scripts without a reviewed policy.
6. Treat repository scripts, tests, package hooks, and build configuration as untrusted code. Separate validation authorization from model-generated commands.
7. Return a structured result: command profile ID, exit code, timeout/cancel state, bounded stdout/stderr, duration, environment image/version, and artifact references. Redact secrets and cap output.
8. Implement cancellation, worker cleanup, image/workspace lifecycle, and resource accounting before exposing the feature to users.
9. Keep source-generation static validation separate from command execution; never execute standalone generated programs by default.

## Acceptance checks

- A hostile test fixture cannot read host files/secrets, access the Docker socket, escape its workspace, or reach blocked network destinations.
- Time, memory, process, disk, and output limits are enforced and reported explicitly.
- Cancellation destroys the execution environment and releases resources.
- Results distinguish pass, fail, timeout, cancelled, blocked, and infrastructure error; no unrun command is reported as passed.

