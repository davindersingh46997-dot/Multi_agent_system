from pydantic import BaseModel

class Supervise_State(BaseModel):
    """
    A class representing the state of a supervise task.
    """
    supervise_code: str

    valid : bool