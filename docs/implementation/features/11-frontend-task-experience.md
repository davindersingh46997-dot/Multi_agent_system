# Feature 11: Frontend Task Experience

## Goal

Present project-aware development tasks with clear progress, plans, diffs, validation results, approvals, cancellation, and final outcomes while preserving the independent file-generation experience.

## Current state

- The React/Vite client lives in `Face\src\`; `Face\src\pages\chat_area.tsx` implements standalone file-generation submission, status polling, clarification, retry/cancel, and authenticated download.
- Project task routes and response schemas exist in the backend, but the inspected `App.tsx` only routes sign-in, signup, and chat; a complete project-task workflow UI is not evidenced.
- The existing client stores an access token in local storage. Revisit the browser credential model before production exposure.

## Implementation steps

1. Define separate navigation and API clients for standalone generation and project-aware tasks; keep output format selection exclusive to standalone file generation.
2. Add project selection and task creation UI backed by authenticated project/task APIs. Display authorization and upload errors without leaking resource existence.
3. Render persisted task states, active stage, plan/clarification/approval waits, errors, and final report. Reloading or reconnecting should restore state from the server.
4. Present patch diffs and approval decisions bound to proposal hashes. Clearly distinguish proposed, applied, rejected, stale, and conflicting changes.
5. Display validation results with command/tool version, exit status, skipped checks, and timestamps; never show “passed” unless the server confirms a successful run for the current diff hash.
6. Add cancellation, retry, and resume controls only where allowed by the task state machine. Explain blocked or exhausted-budget cases.
7. Use polling as the initial transport with backoff and visibility-aware intervals; consider SSE/WebSockets only after persisted event APIs and reconnect behavior are defined.
8. Download generated artifacts through authenticated endpoints and use the server-sanitized filename. Never expose model IDs, HF tokens, workspace storage paths, or raw provider responses.
9. Review session/token storage, XSS protections, CSRF posture as applicable, and logout/expiry handling. Avoid placing credentials in URLs or logs.
10. Add frontend tests for route guards, reload persistence, status transitions, access-denied behavior, diff approval, cancellation, and authenticated downloads.

## Acceptance checks

- Existing generation UI and project-task UI remain distinct and functional.
- Browser reload resumes the correct server-backed task state without duplicate submissions.
- All active, waiting, terminal, failure, and stale-proposal states have explicit UX.
- TypeScript build and focused UI tests pass; no secrets or model-selection controls are sent to the browser.

