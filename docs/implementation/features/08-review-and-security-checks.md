# Feature 8: Review and Security Checks

## Goal

Assess proposed changes against requirements, repository conventions, regression risk, and security policy, while keeping review separate from proof that tests passed.

## Current state

- `brain\agents\tester.py` defines `ReviewerAgent`; the project supervisor includes a reviewer role.
- The project flow stages diffs and only applies them through a user approval endpoint.
- There is no verified project test execution or comprehensive automated security scanning in the current path.
- Standalone generation has a separate reviewer and static validator; it must remain distinct from project code review.

## Implementation steps

1. Define review input as immutable task requirements, approved plan, evidence references, diff/base hashes, and actual validation results.
2. Add deterministic checks first: diff bounds, secret-pattern scanning with reviewed false-positive handling, prohibited path checks, dependency-change detection, and required static validation.
3. Require the model reviewer to return typed findings with severity, file/line references, rationale, confidence, and actionable recommendation. Reject malformed or ungrounded locations.
4. Treat reviewer output as advisory; deterministic policy gates decide whether a proposal is blocked, requires additional approval, or can be presented.
5. Ensure reviewers cannot approve their own proposal or apply changes. Keep security review separate from coding and validation execution.
6. Run regression/security checks against the exact diff hash. Invalidate previous check results whenever the diff changes.
7. Report unavailable checks, skipped checks, and tool errors explicitly. Never label unexecuted tests or checks as passing.
8. Add adversarial fixtures for prompt injection in source/comments, secret exposure, unsafe dependency changes, path traversal, and misleading test output.

## Acceptance checks

- Findings map to real files/lines in the reviewed diff and retain severity/confidence.
- Review and test results refer to the exact proposal hash and become stale after changes.
- Model review cannot bypass policy, apply changes, or certify unrun checks.
- False positive, unavailable scanner, and scanner failure states are explicit and tested.

