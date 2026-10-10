from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    PDF = "pdf"
    PYTHON = "py"
    JAVASCRIPT = "js"
    TYPESCRIPT = "ts"
    HTML = "html"
    CSS = "css"
    JAVA = "java"
    CPP = "cpp"
    JSON = "json"
    MARKDOWN = "md"
    TEXT = "txt"


class FileGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    output_format: OutputFormat


class FileClarificationRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=4000)


class FileGenerationResponse(BaseModel):
    id: int
    prompt: str
    output_format: OutputFormat
    status: str
    current_stage: str | None
    filename: str | None
    clarification_question: str | None
    error: str | None
    download_url: str | None
    created_at: datetime
    updated_at: datetime

