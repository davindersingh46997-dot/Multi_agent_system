from pydantic import BaseModel

class Test_State(BaseModel):
    """
    A class representing the state of a test task.
    """
    test_code: str
     
    verifie: bool