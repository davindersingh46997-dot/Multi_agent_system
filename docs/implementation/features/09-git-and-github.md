# Feature 9: Git and GitHub Integration

## Goal

Provide deterministic, approval-controlled branch, commit, push, and pull-request operations without granting models direct Git authority or repository credentials.

## Current state

- No Git branch/commit/push or GitHub pull-request service is evidenced in the inspected application.
- Current project edits are proposed and applied to server-managed workspaces through an approval-bound route.
- GitHub credentials, installation/app authorization, branch policy, and remote repository mapping are future design work.

## Implementation steps

1. Decide the supported repository source and ownership model (server workspace, user-connected GitHub repository, or both) before adding remote operations.
2. Implement Git operations in a deterministic service with fixed argument construction and strict repository-root validation. Do not expose a generic Git command or shell tool to agents.
3. Create a task-specific branch/worktree from a recorded base commit. Confirm clean/expected starting state and prevent concurrent tasks from sharing a mutable checkout.
4. Stage only approved, validated paths and diffs. Re-check hashes and policy immediately before commit; generate commit messages from bounded task metadata and require user confirmation if policy requires it.
5. Store base/head commit IDs, branch name, proposal/check hashes, author identity, and operation outcomes as task history.
6. Use a least-privilege GitHub App or equivalent short-lived scoped credentials for push/PR operations. Keep credentials in a server-side secret manager; never send them to agents, workers' logs, or browser clients.
7. Require explicit user approval for push and PR creation. Validate target repository, base branch, permissions, and branch protections on the server.
8. Make operations idempotent where possible and report partial outcomes (commit succeeded, push failed, PR unavailable) without claiming end-to-end success.
9. Add cleanup and recovery for abandoned worktrees/branches without deleting user data or shared repository state.

## Acceptance checks

- An agent cannot choose an arbitrary repository, remote URL, branch target, or Git argument.
- Credentials are scoped, short-lived, server-side, and redacted.
- Approval is bound to exact commit content and target branch; changed content requires fresh approval.
- Tests cover branch isolation, concurrent tasks, dirty worktrees, stale base commits, push failure, duplicate requests, and PR authorization.

