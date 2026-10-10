from typing import Literal

from huggingface_hub import AsyncInferenceClient

from brain.core.settings import Settings, get_settings


ModelRole = Literal[
    "requirements",
    "planner",
    "programmer",
    "reviewer",
    "validator",
]


class HuggingFaceConfigurationError(RuntimeError):
    pass


class HuggingFaceProviderError(RuntimeError):
    pass


class HuggingFaceChatModel:
    def __init__(self, model_id: str, client: AsyncInferenceClient) -> None:
        self.model_id = model_id
        self.client = client

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int,
        json_mode: bool = False,
    ) -> str:
        response_format = {"type": "json_object"} if json_mode else None
        try:
            result = await self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0,
                response_format=response_format,
            )
        except Exception as exc:
            raise HuggingFaceProviderError(
                f"Hugging Face inference failed for configured model {self.model_id}."
            ) from exc
        finally:
            await self.client.close()

        if not result.choices:
            raise HuggingFaceProviderError("Hugging Face returned no completion choices.")
        content = result.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise HuggingFaceProviderError("Hugging Face returned an empty completion.")
        return content.strip()


class HuggingFaceModelFactory:
    @staticmethod
    def create(
        role: ModelRole,
        settings: Settings | None = None,
    ) -> HuggingFaceChatModel:
        settings = settings or get_settings()
        if settings.hf_token is None:
            raise HuggingFaceConfigurationError(
                "Set HF_TOKEN in .env to enable Hugging Face file generation."
            )
        model_id = settings.generation_model_for(role)
        if model_id is None:
            raise HuggingFaceConfigurationError(
                "Set HF_DEFAULT_MODEL or a model ID for each generation agent."
            )
        client = AsyncInferenceClient(
            model=model_id,
            provider=settings.hf_inference_provider,
            token=settings.hf_token.get_secret_value(),
            timeout=settings.hf_inference_timeout_seconds,
        )
        return HuggingFaceChatModel(model_id, client)
