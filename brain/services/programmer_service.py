from pydantic import BaseModel
from typing import Any

from brain.agents.programmer import ProgrammerAgent

class ProgrammerService:
    """
    The application which is responsible for the handling the programming tasks using the programming agent .
    """

    def __init__(
            self,
            Programmer_agent : ProgrammerAgent
    ):

        self._programmer_agent = ProgrammerAgent

        self._agent = self._programmer_agent.get_agent()

    def execute(self,task : str) -> Any:
        """"
        Execute a programming task.
        """

        if not task and not task.strip():
            raise ValueError("Programming task cannot be empty. ")

        response = self._agent.invoke(
            {
                "messsages": [
                    {
                        "role" : "user",
                         "content" : task
                    }
                ]
            }
        )

        return response