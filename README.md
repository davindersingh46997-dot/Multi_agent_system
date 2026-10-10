# Multi-Agent Software Developer

An authenticated coding assistant that can generate downloadable files from a user's requirements, as well as review changes in projects placed beneath a server-managed workspace. Project-scoped tasks index source for lexical retrieval, analyze optional code screenshots with a configured vision-capable chat model, coordinate analyst/programmer/reviewer roles, stage file changes through FastMCP tools, and apply only changes explicitly approved by the user.

## Local Setup

Requirements: Python 3.10+, `uv`, and Node.js with npm.

1. Run `uv sync --extra dev` from the repository root.
2. Merge the blank settings in `.env.example` into the existing `.env`; do not replace an existing `.env` containing credentials.
3. Start the backend with `uv run uvicorn brain.main:app --reload`.
4. Start the client with `npm --prefix Face run dev`.
5. Register an account and sign in using the account email in the username field. The chat can generate a downloadable file without a project; project directories are only needed for project-scoped task workflows.

In the chat, describe the file you need and choose an output type: PDF, Python, JavaScript, TypeScript, HTML, CSS, Java, C++, JSON, Markdown, or plain text. The agent team analyzes requirements, plans a single file, writes it, reviews it, and performs bounded static validation. Generated files are owner-scoped downloads; PDF output contains the generated source code. The application does not execute generated programs.

The default project store is `workspace/`. Each account is confined to `workspace/user-<id>/`; a project path entered in the client is relative to that directory. The directory must exist before registration.

## Hugging Face File Generation

Set a Hugging Face user access token and a model that supports [Inference Providers chat completion](https://huggingface.co/docs/inference-providers/en/tasks/chat-completion) in the ignored `.env`:

```dotenv
HF_TOKEN=
HF_INFERENCE_PROVIDER=auto
HF_DEFAULT_MODEL=
HF_REQUIREMENTS_MODEL=
HF_PLANNER_MODEL=
HF_PROGRAMMER_MODEL=
HF_REVIEWER_MODEL=
HF_VALIDATOR_MODEL=
```

`HF_DEFAULT_MODEL` is the fallback model ID for every generation role. Set per-role IDs only when those models are available through the configured provider and support the structured JSON responses required by that role. `HF_INFERENCE_PROVIDER=auto` follows Hugging Face's provider routing. The token and model IDs are server-side configuration, not chat inputs. Restart the backend after changing `.env`.

The separate project-aware task workflow continues to use the optional `MODEL_PROVIDER`, `MODEL_NAME`, `MODEL_API_KEY`, and `MODEL_BASE_URL` settings. Project tasks that need a model also need `MODEL_PROVIDER` and `MODEL_NAME`; the Hugging Face generation settings do not implicitly reconfigure that older task path.

Generation tasks and their status are persisted. Generated artifacts expire after `GENERATED_ARTIFACT_RETENTION_DAYS` (default 7). The worker runs within the FastAPI application process and recovers stale task leases after restart; configure one application deployment before scaling horizontally. Generation validates JSON and Python syntax without running the generated program. Other file types receive model-assisted review but are not executed.

In development, a temporary signing key is generated when `AUTH_SECRET_KEY` is empty, so login tokens stop working after a backend restart. Production requires a stable `AUTH_SECRET_KEY` of at least 32 bytes and a production database URL.

## Safety and Current Limits

- Images are validated and sent to the configured multimodal model; image code is evidence and is not directly copied into files.
- Retrieval currently uses project-filtered BM25-style lexical ranking. Dense embeddings/vector storage are not configured.
- Proposed file changes are stored with a unified diff and source hash. Approval is bound to the proposal hash and current source hash.
- The initial runtime does not execute shell commands or run project tests. The reviewer reports checks to run; it does not claim they passed.
- Project task work currently uses FastAPI background tasks, which are not a durable job queue. File generation uses a database-backed queue worker inside the API process; a separately operated worker, database migrations, production quotas, and remote MCP servers remain follow-up work.
- Face-authentication data remains separate from developer task data and code retrieval.

Run backend tests with `uv run pytest`. The implementation and architecture details are in [docs/implementation](docs/implementation/README.md).
