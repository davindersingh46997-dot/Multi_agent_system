# Feature 2: Hugging Face Model Integration

## Goal

Provide one server-side model interface for agent roles using Hugging Face Inference Providers now, while preserving a provider boundary that can later support dedicated Inference Endpoints.

## Current state

- Standalone generation uses `HuggingFaceModelFactory` and `HuggingFaceChatModel` in `brain\core\huggingface_models.py`.
- `HF_TOKEN`, provider selection, default model, per-role overrides, and timeout settings are defined in `brain\core\settings.py`.
- The separate project-task path uses `ModelFactory` in `brain\core\model_factory.py`; it is not automatically configured from the standalone Hugging Face settings.
- File-generation tests mock the provider adapter. No credentialed/live provider call is required for routine tests.

## Implementation steps

1. Define a typed model protocol shared by planner, repository analyst, coder, debugger, and reviewer roles. Keep provider-specific request/response objects inside adapters.
2. Decide whether project-task roles should use the existing generic `ModelFactory` configuration or gain a Hugging Face adapter. Do not silently change the model configuration contract for either workflow.
3. Validate required token/model settings at task start or an explicit health/configuration check. Never accept credentials or model IDs from client requests.
4. Pass bounded timeout, token limits, temperature, and structured-output options through typed settings. Support per-role model overrides with a documented default fallback.
5. Normalize provider failures into explicit categories (configuration, unsupported capability, rate limit, timeout, unavailable model, malformed response, provider outage). Redact tokens and raw provider payloads from user-facing errors and logs.
6. Add a capability registry or deployment validation step for each configured role/model/provider combination: chat completion, JSON/schema behavior where needed, context budget, multimodal input if used, and output limits.
7. Add retry policy only for transient, idempotent provider failures. Bound attempts, use backoff/jitter, honor rate-limit hints, and do not retry invalid requests indefinitely.
8. Add a separately configured smoke test for deployment verification. Do not make tests depend on live credentials or provider availability.
9. Record model/provider version, latency, token usage, task outcome, and estimated cost as redacted operational metadata for later model evaluation.
10. Keep the adapter boundary compatible with a future Hugging Face Inference Endpoint without requiring local weight downloads or GPU deployment.

## Acceptance checks

- Unit tests assert token secrecy, selected role model, timeout, token cap, JSON mode, and normalized provider errors.
- Tests cover missing settings, unsupported structured output, rate limit, timeout, empty response, malformed JSON, and transient retry bounds.
- Model/provider changes run against mocked workflow regression tests and an operator-controlled smoke test.
- The UI and public API never receive or select provider credentials or model identifiers.

