from agents.programmer import ProgrammerAgent

class ProgrammerService:

    """
    Application service responsible for 
    executing programmer tasks.
    """

    def __init__(
            self,
            programmer : ProgrammerAgent
    ):

        self.programmer = programmer

        self._agent = programmer.get_agent()

    def execute_agent(
            self,
            task : str,
    ) -> str:

        response = self._agent.invoke(
            {
                "messages" : [
                    {
                        "role" : "user",
                        "content" : task,
                    }
                ]
            }
        ) 

        return response["messages"][-1].content