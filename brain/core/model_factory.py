from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from brain.core.settings import Settings, get_settings


class ModelConfigurationError(RuntimeError):
    pass

class ModelFactory:
    """
    Responsible for creating the language models instances
    """
    @staticmethod
    def create_model(settings: Settings | None = None) -> BaseChatModel:
        settings = settings or get_settings()
        if not settings.model_provider or not settings.model_name:
            raise ModelConfigurationError(
                "Set MODEL_PROVIDER and MODEL_NAME in .env before running model-backed tasks."
            )

        options: dict[str, object] = {"temperature": 0}
        if settings.model_api_key:
            options["api_key"] = settings.model_api_key.get_secret_value()
        if settings.model_base_url:
            options["base_url"] = settings.model_base_url

        return init_chat_model(
            settings.model_name,
            model_provider=settings.model_provider,
            **options,
        )
