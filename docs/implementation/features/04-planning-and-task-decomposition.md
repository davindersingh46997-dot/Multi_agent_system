# Feature 4: Planning and Task Decomposition

## Goal

Convert a user's request and repository evidence into a bounded, reviewable plan with acceptance criteria and dependencies before code changes begin.

## Current state

- `brain\agents\supervisor.py` coordinates the existing project-aware workflow.
- The project path has a repository analyst, programmer, and reviewer/test role, but a persisted plan/task DAG and explicit plan-approval stage are not evidenced in the inspected architecture.
- Standalone generation has a typed one-file planner in `brain\agents\file_generation.py`; do not reuse its one-file contract for multi-file project work.

## Implementation steps

1. Define typed plan and work-item schemas: goal, repository evidence references, files likely affected, acceptance criteria, dependencies, risk, estimated resource budget, and unresolved questions.
2. Validate input limits and identify blockers before scheduling work. Ask the user only for information that affects implementation or acceptance.
3. Have the repository analyst provide evidence first; require the planner to distinguish observed facts from assumptions and cite evidence.
4. Generate a dependency graph with bounded work-item count, depth, and estimated tokens/time. Reject cycles and plans outside configured limits.
5. Persist the plan and version it against task ID and repository/index snapshot. Define statuses such as `draft`, `awaiting_approval`, `approved`, `superseded`, and `rejected`.
6. Add optional approval for high-impact tasks or plans that involve dependencies, sensitive files, broad refactors, or later command execution.
7. Only dispatch coding work from an approved, current plan. If the repository changes materially, invalidate affected evidence and ask for replanning or confirmation.
8. Keep planning model output advisory: deterministic application logic owns budgets, authorization, transition checks, and allowed operations.

## Acceptance checks

- Schema tests reject missing acceptance criteria, over-budget plans, invalid dependencies, and cyclic graphs.
- Plans distinguish evidence-backed facts from assumptions and unresolved questions.
- Approval is bound to a plan version/hash; superseded plans cannot authorize work.
- Prompt-injection text in repository evidence cannot expand the plan's permissions.

