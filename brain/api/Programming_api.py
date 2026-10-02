from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field

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
    raise HTTPException(
        status_code=410,
        detail="Use the authenticated /api/tasks workflow instead.",
    )