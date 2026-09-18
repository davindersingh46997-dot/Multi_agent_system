from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from agents.base_agent import BaseAgent

class ProgrammerAgent:
    """
    Autonomous coding agent.

    Responbilities:
    - Understand the  programming tasks.
    - Use registered coding tools
    - Inspect and modify project files
    - Return the final response
    """

    def __init__(
            self,
            model : BaseChatModel,
            tools : list[Any],
    ):
       """
       Initialize the programmer agent
       """ 

       super().__init__(
           name = "Programmer"
       )

       self._model = model

       self._tools = tools

       self._system_prompt = self._build_system_prompt()

       self._agent = None

    def _build_system_prompt(self) -> str:
        """
        create the programmer's  system instructions
        """

        return """
You are an autonomous software programmer.

Your goal is to solve programming tasks
inside the assigned project directory.

Responsibilities:

1. Understand the user's task.
2. Inspect the project structure.
3. Read relevant files before modifying them.
4. Plan the required changes.
5. Use the available tools to implement changes.
6. Validate the implementation when possible.
7. Clearly explain the completed work.

Rules:

- Do not invent project files.
- Read existing files before editing.
- Keep changes focused.
- Preserve existing functionality.
- Never access files outside the allowed project.
- Do not expose secrets or API keys.
- Ask for clarification if the task is ambiguous.
"""

    def build(self) -> Any:
        """
        Build and return the langchain agent.
        """

        self._agent = create_agent(
            model = self._model,
            tools = self._tools,
            system_prompt = self._system_prompt,
        )

        return self._agent

    def get_agent(self) -> Any:
        """
        Return the build agent
        """

        if self._agent is None:
            return self.build()

        return self._agent
