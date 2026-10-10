# Feature-by-Feature Implementation Guides

These guides break the platform roadmap into independently implementable increments. They describe work to perform; they do not claim that a planned capability is already implemented. The current codebase is an MVP with two intentionally separate workflows: standalone file generation and project-aware coding tasks.

## Recommended implementation order

| Order | Feature guide | Primary prerequisite |
|---|---|---|
| 1 | [Authentication and project access](features/01-authentication-and-project-access.md) | Existing owner-scoped auth and workspace paths |
| 2 | [Hugging Face model integration](features/02-model-provider.md) | Existing Hugging Face adapter; complete compatibility gates |
| 3 | [Repository analysis and retrieval](features/03-repository-analysis-and-retrieval.md) | Project authorization and safe workspace access |
| 4 | [Planning and task decomposition](features/04-planning-and-task-decomposition.md) | Repository evidence and persisted task state |
| 5 | [Controlled code changes](features/05-controlled-code-changes.md) | Planning, evidence, and approval policy |
| 6 | [Sandboxed commands and validation](features/06-sandboxed-validation.md) | Isolated worker and execution policy |
| 7 | [Bounded debugging and repair](features/07-debugging-and-repair.md) | Validation results and repair budget |
| 8 | [Review and security checks](features/08-review-and-security-checks.md) | Stable diff and validation evidence |
| 9 | [Git and GitHub integration](features/09-git-and-github.md) | Approval-bound changes and credential isolation |
| 10 | [Durable orchestration and task history](features/10-durable-orchestration.md) | Explicit task lifecycle and chosen job backend |
| 11 | [Frontend task experience](features/11-frontend-task-experience.md) | Stable task, event, approval, and diff APIs |
| 12 | [Operations, observability, and scale](features/12-operations-and-scaling.md) | Durable workers and production deployment design |

The ordering is a dependency-aware recommendation, not a requirement to implement every feature before shipping a smaller local increment. Keep standalone file generation separate from repository-aware tasks; do not route generator requests through project retrieval or workspace tools.

## How to use a guide

Implement one guide at a time. Start by checking its current-state notes against the code and tests, then complete the ordered steps and acceptance checks before moving on. Preserve the existing project approval boundary and do not enable unrestricted shell access, unattended writes, local model weights, or host/Docker socket access as shortcuts.

## Existing implementation references

- [Target architecture](ARCHITECTURE.md)
- [Current implementation plan](IMPLEMENTATION_PLAN.md)
- Backend source is under `brain\`; tests are under `tests\`; the React client is under `Face\`.
