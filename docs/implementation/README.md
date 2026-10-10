# Multi-Agent Software Developer: Implementation Brief

## Purpose

The application offers two separate authenticated coding workflows:

1. **Standalone file generation:** turn a user's requirements into one downloadable file in a selected format, without requiring a project.
2. **Project-aware development:** inspect an authorized project, retrieve relevant source, stage proposed changes, and apply them only after user approval.

These documents distinguish the current local implementation from production follow-up work.

## Documents

- [Target architecture](ARCHITECTURE.md): workflows, APIs, Hugging Face model boundary, agents, artifacts, RAG, MCP, and security.
- [Implementation plan](IMPLEMENTATION_PLAN.md): current delivery status, remaining phases, and validation/release gates.

## Standalone Generator

- The React chat supports PDF, Python, JavaScript, TypeScript, HTML, CSS, Java, C++, JSON, Markdown, and plain text output.
- The authenticated `/api/files/generate` route persists a generation request and returns its task status; users can poll status, answer a clarification request, retry a failed generation, cancel work, and download an unexpired artifact.
- A database-backed worker claims queued work with a lease. Generation task and artifact records are owner-scoped; artifact bytes are retained for the configured duration.
- The agent workflow uses Hugging Face Inference Providers through `huggingface_hub.AsyncInferenceClient`. `HF_TOKEN` remains server-side; a default model ID can be overridden per agent via environment settings.
- Requirements analyst, planner, programmer, reviewer, and validator have typed hand-offs and a deterministic stage order. Reviewer revisions are capped. JSON and Python receive deterministic syntax parsing; other formats receive bounded model-assisted checks.
- Generated source is never executed. PDF output wraps the generated contents as a PDF document. Agent-suggested filenames are sanitized and cannot select a path.

The hosted provider integration is covered by mocked tests. A live integration smoke test requires a valid Hugging Face token and configured model IDs with chat-completion and JSON response-format support.

## Project-Aware Workflow

- Email/password registration and JWT login are available under `/api/auth`.
- Projects and tasks are owner-scoped; project roots resolve only under `PROJECTS_ROOT/user-<owner-id>/`.
- Project tasks use lexical repository retrieval, optional validated image uploads, the existing project supervisor, MCP-backed list/read/search/propose tools, and hash-bound approval before applying proposed edits.
- The standalone generation path does not inspect a project, invoke MCP tools, or change project files.

## Current Limits

- The generation worker runs inside the FastAPI process. Queued task state survives restarts and stale leases can be recovered, but independent worker deployment and operational scaling are not yet provided.
- Generated code is not executed or tested. The validator uses deterministic syntax checks only for JSON and Python, plus a configured review model.
- Database startup uses SQLAlchemy `create_all`; schema migrations, production deployment procedures, observability, request quotas, and operational retention configuration remain follow-up work.
- Hugging Face model IDs must be selected for supported chat-completion and structured JSON output. No model is selected by default; model selection and a live provider smoke test remain operator responsibilities.
- Face-authentication embeddings remain isolated from code generation and project retrieval.
