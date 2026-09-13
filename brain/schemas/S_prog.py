from pydantic import BaseModel

class Programming_State(BaseModel):
    """
    A class representing the state of a programming task.
    """
    code: str
                    