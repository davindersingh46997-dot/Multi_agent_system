from fastapi import APIRouter,HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth",tags=["Authentication"])

class LoginRequest(BaseModel):
    username : str
    password : str


@router.post("/login")
def login(request : LoginRequest):

    if(username == "Davinder" and )