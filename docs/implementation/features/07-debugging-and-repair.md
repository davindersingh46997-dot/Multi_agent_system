# Feature 7: Bounded Debugging and Repair

## Goal

Use structured validation failures to diagnose and repair changes in a limited, auditable loop without allowing open-ended agent execution.

## Current state

- A distinct debugging agent and repair loop for project tasks are not evidenced in the current agent list.
- The standalone generator has a bounded reviewer-driven revision loop, configured by `generation_max_revision_rounds`; it does not execute generated source.
- Project validation results are not currently produced by an isolated command runner.

## Implementation steps

1. Define a typed failure packet containing the validation run ID, command profile, exit state, relevant bounded output, changed-file list, and repository snapshot hash.
2. Add a debugging role only after the sandboxed-validation feature can supply trustworthy, bounded failures. Keep its permissions read-only during diagnosis.
3. Require a minimal repair proposal that cites the failing evidence and identifies impacted acceptance criteria and files.
4. Apply repairs only through the same patch-validation and user-approval policy as coding changes. Never let the debugger directly modify files or invoke commands.
5. Set explicit per-task limits for repair iterations, changed files, wall time, provider calls, and total execution cost. Do not reset the budget on retry or worker restart.
6. Re-run only relevant validation first, then the required regression set. Preserve each run/result and link it to the exact patch hash.
7. Stop and report blocked if failures are ambiguous, environment-related, persist after the budget, or require new permissions/dependencies.
8. Prevent repeated application of an identical patch or identical failing attempt; mark no-progress loops clearly.

## Acceptance checks

- Every repair is linked to a prior failure and a new patch hash.
- The loop stops at configured budgets across retries and worker restarts.
- A failure packet cannot inject tool instructions or expand the task's command permissions.
- Tests cover successful repair, no progress, repeated failure, timeout, cancellation, and exhausted budget.

