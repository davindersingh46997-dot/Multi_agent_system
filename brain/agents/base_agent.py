from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel


class BaseAgent(ABC):
    def __init__(self, name: str, model: BaseChatModel) -> None:
        self.name = name
        self.model = model

    @abstractmethod
    async def run(self, task: str, context: dict[str, Any]) -> str:
        raise NotImplementedError


def response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            str(block.get("text", "")) for block in content if isinstance(block, dict)
        )
    return str(content)
            