import asyncio

from brain.agents.file_generation import (
    FileGenerationOrchestrator,
    GenerationClarificationRequired,
    GenerationValidationError,
)
from brain.core.huggingface_models import (
    HuggingFaceConfigurationError,
    HuggingFaceModelFactory,
)
from brain.core.settings import Settings
from brain.schemas.generated_files import OutputFormat


class FakeModel:
    def __init__(self, response):
        self.response = response

    async def complete(self, messages, *, max_tokens, json_mode=False):
        assert max_tokens > 0
        assert messages and isinstance(messages[0]["content"], str)
        assert isinstance(json_mode, bool)
        return self.response


class FakeModelFactory:
    def __init__(self, responses):
        self.responses = {role: list(values) for role, values in responses.items()}
        self.calls = []

    def create(self, role, settings=None):
        assert settings is not None
        self.calls.append(role)
        return FakeModel(self.responses[role].pop(0))


class FakeInferenceClient:
    def __init__(self, content):
        self.content = content
        self.closed = False

    async def chat_completion(self, **kwargs):
        assert kwargs["max_tokens"] > 0
        assert kwargs["temperature"] == 0
        return type(
            "Completion",
            (),
            {"choices": [type(
                "Choice",
                (),
                {"message": type("Message", (), {"content": self.content})()},
            )()]},
        )()

    async def close(self):
        self.closed = True


async def _check_stage(stage):
    assert stage in {"requirements", "planner", "programmer", "reviewer", "validator"}


def _valid_responses(program_code="print('hello')\n"):
    return {
        "requirements": ['{"summary":"Write a greeting program.","needs_clarification":false}'],
        "planner": ['{"purpose":"Greet the user","language":"Python","filename":"hello.py","acceptance_criteria":["Print a greeting"]}'],
        "programmer": [program_code],
        "reviewer": ['{"approved":true,"feedback":""}'],
        "validator": ['{"valid":true,"issues":[]}'],
    }


def test_agent_sequence_returns_reviewer_approved_static_file():
    factory = FakeModelFactory(_valid_responses())
    stages = []

    async def record_stage(stage):
        stages.append(stage)

    orchestrator = FileGenerationOrchestrator(
        settings=Settings(_env_file=None),
        model_factory=factory,
    )
    content, filename = asyncio.run(
        orchestrator.generate(
            "Write a greeting program.",
            None,
            OutputFormat.PYTHON,
            record_stage,
        )
    )

    assert content == "print('hello')"
    assert filename == "hello.py"
    assert factory.calls == ["requirements", "planner", "programmer", "reviewer", "validator"]
    assert stages == factory.calls


def test_requirements_agent_can_request_clarification():
    responses = _valid_responses()
    responses["requirements"] = [
        '{"summary":"Need a language","needs_clarification":true,"clarification_question":"Which programming language should I use?"}'
    ]
    orchestrator = FileGenerationOrchestrator(
        settings=Settings(_env_file=None),
        model_factory=FakeModelFactory(responses),
    )

    try:
        asyncio.run(
            orchestrator.generate(
                "Create a program.",
                None,
                OutputFormat.PDF,
                _check_stage,
            )
        )
    except GenerationClarificationRequired as exc:
        assert "Which programming language" in exc.question
    else:
        raise AssertionError("Missing language should request clarification for PDF output.")


def test_invalid_python_is_rejected_without_execution():
    factory = FakeModelFactory(_valid_responses("def broken(:\n"))
    orchestrator = FileGenerationOrchestrator(
        settings=Settings(_env_file=None),
        model_factory=factory,
    )

    try:
        asyncio.run(
            orchestrator.generate(
                "Write a greeting program.",
                None,
                OutputFormat.PYTHON,
                _check_stage,
            )
        )
    except GenerationValidationError as exc:
        assert "did not pass validation" in str(exc)
    else:
        raise AssertionError("Invalid Python syntax must not be accepted.")


def test_review_revisions_are_bounded():
    responses = _valid_responses()
    responses["programmer"] = ["print('hello')", "print('hello')"]
    responses["reviewer"] = [
        '{"approved":false,"feedback":"Add a greeting."}',
        '{"approved":false,"feedback":"Still incomplete."}',
    ]
    factory = FakeModelFactory(responses)
    orchestrator = FileGenerationOrchestrator(
        settings=Settings(_env_file=None, generation_max_revision_rounds=1),
        model_factory=factory,
    )

    try:
        asyncio.run(
            orchestrator.generate(
                "Write a greeting program.",
                None,
                OutputFormat.PYTHON,
                _check_stage,
            )
        )
    except GenerationValidationError as exc:
        assert "revision limit" in str(exc)
    else:
        raise AssertionError("Review iterations must stop at the configured limit.")
    assert factory.calls.count("programmer") == 2
    assert factory.calls.count("reviewer") == 2


def test_huggingface_adapter_uses_model_and_closes_client(monkeypatch):
    import brain.core.huggingface_models as huggingface_models

    client = FakeInferenceClient("  generated output  ")

    def make_client(**kwargs):
        assert kwargs["model"] == "org/model"
        assert kwargs["token"] == "test-token"
        assert kwargs["provider"] == "auto"
        return client

    monkeypatch.setattr(huggingface_models, "AsyncInferenceClient", make_client)
    model = HuggingFaceModelFactory.create(
        "programmer",
        Settings(
            _env_file=None,
            hf_token="test-token",
            hf_default_model="org/model",
        ),
    )
    content = asyncio.run(model.complete([{"role": "user", "content": "write"}], max_tokens=100))
    assert content == "generated output"
    assert client.closed


def test_huggingface_factory_requires_server_token():
    try:
        HuggingFaceModelFactory.create(
            "programmer",
            Settings(_env_file=None, hf_default_model="org/model"),
        )
    except HuggingFaceConfigurationError as exc:
        assert "HF_TOKEN" in str(exc)
    else:
        raise AssertionError("Missing Hugging Face token must fail clearly.")
