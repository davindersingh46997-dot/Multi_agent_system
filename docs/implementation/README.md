# Multi-Agent Software Developer: Implementation Brief

## Purpose

Define the architecture and implementation status for a multi-agent software development assistant. The assistant understands a user's request, inspects an authorized project, retrieves project evidence, interprets code screenshots with a configured vision model, stages changes through MCP tools, and applies only explicitly approved changes.

These documents describe the implementation and distinguish working local capabilities from deferred production features.

## Documents

- [Target architecture](ARCHITECTURE.md): components, request flows, RAG, image understanding, MCP boundaries, APIs, and security model.
- [Implementation plan](IMPLEMENTATION_PLAN.md): staged delivery, dependencies, validation gates, and completion criteria.

## Implemented Local MVP

The repository has a Python/FastAPI backend under `brain/` and a React/TypeScript/Vite client under `Face/`.

- Email/password registration and JWT login are available under `/api/auth`; development signing keys are ephemeral unless configured.
- Projects and tasks are owner-scoped. Project roots resolve only under `PROJECTS_ROOT/user-<owner-id>/`.
- The task UI supports project registration/selection, prompt submission, screenshot uploads, status refresh, diff review, and approve/reject actions.
- Repository files are chunked into SQL rows and ranked with project-filtered BM25-style lexical retrieval. Secret files, binary files, generated folders, and oversized files are excluded.
- The supervisor coordinates read-only repository and image analysts, a programmer with MCP-backed list/read/search/propose tools, and a read-only diff reviewer.
- FastMCP runs in-process. Changes are staged, hash-bound, and only applied after user approval and a fresh source-hash check.
- `MODEL_PROVIDER`, `MODEL_NAME`, `MODEL_API_KEY`, and `MODEL_BASE_URL` are blank in `.env.example`. The model and key remain a user decision; model construction is lazy.
- Face-authentication embeddings remain isolated from code retrieval.

This is a local MVP, not a production execution environment. It does not run commands/tests, use a durable background queue, store task event history, use database migrations, or connect to remote MCP servers. Dense vector embeddings are also deferred; current retrieval is lexical.

## Target Outcome

An authenticated user selects an authorized project and submits a task, optionally attaching one code screenshot. The system indexes project source, retrieves relevant context, asks the configured multimodal model to analyze the image, stages proposed edits, requires approval, applies changes only when the original file hash still matches, and reports reviewer notes. Project test execution is not yet implemented.

The agent must distinguish observed facts from inferred code, cite retrieved files and image regions in its reasoning/result, and request clarification when an image is unreadable or its intended change is ambiguous. A screenshot is evidence, not permission to overwrite a project file.

## Architectural Decisions

- Keep FastAPI as the authenticated public API and orchestration boundary.
- Use explicit agent roles coordinated by a supervisor; agents do not get direct unrestricted filesystem or process access.
- Keep RAG retrieval-grounded and project-scoped. Use a persistent vector store only as an index; canonical source remains the user's project files.
- Treat image OCR/vision as a separate ingestion and interpretation step before retrieval and planning.
- Use MCP/FastMCP for typed, auditable tool interfaces. Start with a server managed by this application and a small allowlist; remote MCP connections are a later, opt-in capability.
- Require workspace-root validation, per-user authorization, bounded execution, audit events, and approval before high-impact actions.
- Keep face authentication isolated from coding assistance, project indexing, and all RAG data.
