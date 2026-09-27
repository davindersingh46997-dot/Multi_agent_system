from fastapi import FastAPI,APIRouter,Depends
from pydantic import BaseModel,Field
from brain.services.programmer_service import ProgrammerService
from brain.agents.programmer import ProgrammerAgent

from fastapi import HTTPException

class ProgrammerRequest(BaseModel):
    task : str = Field(
        ...,
        min_length = 1,
        description= "Programming task to execute o"
    )


class ProgrammerResponse(BaseModel):
    success : bool
    message : str    


router = APIRouter(
    prefix = "/programmer",
    tags = ["Programmer"]
)


@router.post(
    "/execute",
    response_model = ProgrammerResponse,
)
def get_programming_service(
    request : ProgrammerRequest
):
    """
    Execute a programming task using the programmer response
    """
    
    try:
        service = ProgrammerService(Programmer_agent=ProgrammerAgent)
        
        result = service.execute(request.task)

        return ProgrammerResponse(
            success = result.success,
            message = result.message,
        )
    
    except ValueError as exc:
        raise HTTPException(
            status_code = 400,
            detail = str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code = 500,
            detail = str(exc)
        )