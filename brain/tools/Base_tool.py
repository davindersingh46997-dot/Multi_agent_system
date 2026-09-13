from abc import ABC,abstractmethod

from typing import TypedDict,Any

class BaseTool(ABC):
    """
    abstract base class for tools
    """

    def __init__(self, name: str, description: str):
        self._name = name
        self._description : str

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Every child tool must implement this method.
        """
        pass
