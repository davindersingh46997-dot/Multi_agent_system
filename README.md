# Multi-Agent Software Developer

An authenticated coding assistant for projects placed beneath a server-managed workspace. It indexes source for lexical retrieval, analyzes optional code screenshots with a configured vision-capable chat model, coordinates analyst/programmer/reviewer roles, stages file changes through FastMCP tools, and applies only changes explicitly approved by the user.

## Local Setup

Requirements: Python 3.10+, `uv`, and Node.js with npm.

1. Run `uv sync --extra dev` from the repository root.
2. Merge the blank settings in `.env.example` into the existing `.env`; do not replace an existing `.env` containing credentials.
3. Start the backend with `uv run uvicorn brain.main:app --reload`.
4. Start the client with `npm --prefix Face run dev`.
5. Register an account, sign in using the account email in the username field, and register one or more project directories.

The default project store is `workspace/`. Each account is confined to `workspace/user-<id>/`; a project path entered in the client is relative to that directory. The directory must exist before registration.

## Model Configuration

Model choice and credentials are intentionally not selected or included. Set these values in the ignored `.env` only after choosing a provider and model:

```dotenv
MODEL_PROVIDER=
MODEL_NAME=
MODEL_API_KEY=
MODEL_BASE_URL=
```

The selected model must support tool calling; image tasks also require image input. Until `MODEL_PROVIDER` and `MODEL_NAME` are configured, tasks validate uploads and index project source, then remain in `awaiting_configuration` without image analysis, retrieval results, or proposed edits. Restart the backend after changing `.env`.

In development, a temporary signing key is generated when `AUTH_SECRET_KEY` is empty, so login tokens stop working after a backend restart. Production requires a stable `AUTH_SECRET_KEY` of at least 32 bytes and a production database URL.

## Safety and Current Limits

- Images are validated and sent to the configured multimodal model; image code is evidence and is not directly copied into files.
- Retrieval currently uses project-filtered BM25-style lexical ranking. Dense embeddings/vector storage are not configured.
- Proposed file changes are stored with a unified diff and source hash. Approval is bound to the proposal hash and current source hash.
- The initial runtime does not execute shell commands or run project tests. The reviewer reports checks to run; it does not claim they passed.
- Task work currently uses FastAPI background tasks, which are not a durable job queue. Database migrations, production worker isolation, retention policies, and remote MCP servers remain follow-up work.
- Face-authentication data remains separate from developer task data and code retrieval.

Run backend tests with `uv run pytest`. The implementation and architecture details are in [docs/implementation](docs/implementation/README.md).
