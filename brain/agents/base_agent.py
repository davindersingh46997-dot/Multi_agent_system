from abc import ABC,abstractmethod

from typing import TypedDict

class BaseAgent(TypedDict):
    """
    abstract base class for all agents
    """

    def __init__(self,name : str):

        self._name = name 

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def build(self) -> Any:
        """
        build and return the agent
        """
        pass
            