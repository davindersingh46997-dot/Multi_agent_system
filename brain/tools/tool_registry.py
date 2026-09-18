from typing import Any

class ToolRegistry:
    """
    Registry responsible for the managing 
    tools available to agents.
    """

    def __init__(self):
        """
        Initiate an empty tool registry.
        """

        self._tools : dict[str,Any] = {}

    def register(self,tool : Any) -> None:
        """
        Registers a tool in the register directory.
        """

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered ."
            )

        self._tools[tool.name] = tool

    def get_tool(self, name : str) -> Any:

        """
        Retrieve a tool by its name .
        """

        if name not in self._tools:
            raise KeyError(
                f"Tool '{name}' is not registered "
            )

        return self._tools[name]

    def get_tools(self) -> list[Any]:

        """
        Return all registered tools.
        """

        return list(self._tools.values())

    def Remove(self,name : str) -> None:
        """
        Erases the given tool from the registry.
        """

        if name not in self._tools:
            raise KeyError(
                f"Tool {name} is not registered ."
            )

        del self._tools[name]

    def has_tool(self,name : str) -> bool:
        """
        checks whether the given tool in the registry or not.
        """ 

        return name in self._tools

    def __len__(self) -> int:
        """
        Returns the number of registered tools
        """

        return len(self._tools)   