from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    relative_path: str = Field(min_length=1, max_length=1024)


class ProjectResponse(BaseModel):
    id: int
    name: str
    relative_path: str
    created_at: datetime

    model_config = {"from_attributes": True}