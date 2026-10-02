from datetime import datetime

from pydantic import BaseModel


class TaskChangeResponse(BaseModel):
    id: int
    relative_path: str
    diff: str
    status: str
    approval_hash: str


class TaskResponse(BaseModel):
    id: int
    project_id: int
    prompt: str
    status: str
    result: str | None
    error: str | None
    created_at: datetime
    changes: list[TaskChangeResponse]


class ChangeApprovalRequest(BaseModel):
    approved: bool
    approval_hash: str