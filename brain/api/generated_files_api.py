import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from brain.auth.dependencies import get_current_user
from brain.database.session import get_db
from brain.models.generation import FileGeneration, GeneratedArtifact, utc_now
from brain.models.user import User
from brain.schemas.generated_files import (
    FileClarificationRequest,
    FileGenerationRequest,
    FileGenerationResponse,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["Generated files"])
TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
ACTIVE_STATUSES = {"analyzing", "planning", "generating", "reviewing", "validating"}


def _task_response(task: FileGeneration) -> FileGenerationResponse:
    return FileGenerationResponse(
        id=task.id,
        prompt=task.prompt,
        output_format=task.output_format,
        status=task.status,
        current_stage=task.current_stage,
        filename=task.filename,
        clarification_question=task.clarification_question,
        error=task.error,
        download_url=(
            f"/api/files/{task.id}/download"
            if task.status == "completed"
            else None
        ),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _owned_task(db: Session, generation_id: int, owner_id: int) -> FileGeneration:
    task = db.query(FileGeneration).filter(
        FileGeneration.id == generation_id,
        FileGeneration.owner_id == owner_id,
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="File generation not found.")
    return task


@router.post(
    "/generate",
    response_model=FileGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_file(
    request: FileGenerationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", max_length=64),
) -> FileGenerationResponse:
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Requirements cannot be blank.")

    if idempotency_key:
        existing = db.query(FileGeneration).filter(
            FileGeneration.owner_id == user.id,
            FileGeneration.idempotency_key == idempotency_key,
        ).first()
        if existing:
            return _task_response(existing)

    task = FileGeneration(
        owner_id=user.id,
        prompt=prompt,
        output_format=request.output_format.value,
        status="queued",
        idempotency_key=idempotency_key,
    )
    db.add(task)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if idempotency_key:
            existing = db.query(FileGeneration).filter(
                FileGeneration.owner_id == user.id,
                FileGeneration.idempotency_key == idempotency_key,
            ).first()
            if existing:
                return _task_response(existing)
        logger.error("Unable to enqueue file generation due to a database constraint.")
        raise HTTPException(status_code=500, detail="Unable to enqueue file generation.") from exc
    db.refresh(task)
    return _task_response(task)


@router.get("", response_model=list[FileGenerationResponse])
def list_generations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[FileGenerationResponse]:
    tasks = db.query(FileGeneration).filter(
        FileGeneration.owner_id == user.id
    ).order_by(FileGeneration.created_at.desc()).limit(50).all()
    return [_task_response(task) for task in tasks]


@router.get("/{generation_id}", response_model=FileGenerationResponse)
def get_generation(
    generation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileGenerationResponse:
    return _task_response(_owned_task(db, generation_id, user.id))


@router.post(
    "/{generation_id}/clarification",
    response_model=FileGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def clarify_generation(
    generation_id: int,
    request: FileClarificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileGenerationResponse:
    task = _owned_task(db, generation_id, user.id)
    if task.status != "needs_clarification":
        raise HTTPException(status_code=409, detail="This generation is not waiting for clarification.")
    answer = request.answer.strip()
    if not answer:
        raise HTTPException(status_code=422, detail="A clarification answer cannot be blank.")
    task.clarification = (
        f"{task.clarification}\n{answer}" if task.clarification else answer
    )
    task.status = "queued"
    task.current_stage = None
    task.clarification_question = None
    task.error = None
    task.updated_at = utc_now()
    db.commit()
    db.refresh(task)
    return _task_response(task)


@router.post("/{generation_id}/retry", response_model=FileGenerationResponse)
def retry_generation(
    generation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileGenerationResponse:
    task = _owned_task(db, generation_id, user.id)
    if task.status != "failed":
        raise HTTPException(status_code=409, detail="Only failed generations can be retried.")
    task.status = "queued"
    task.current_stage = None
    task.claim_token = None
    task.cancel_requested = False
    task.error = None
    task.clarification_question = None
    task.updated_at = utc_now()
    db.commit()
    db.refresh(task)
    return _task_response(task)


@router.delete("/{generation_id}", response_model=FileGenerationResponse)
def cancel_generation(
    generation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileGenerationResponse:
    task = _owned_task(db, generation_id, user.id)
    if task.status == "queued" or task.status == "needs_clarification":
        task.status = "cancelled"
        task.current_stage = None
        task.claim_token = None
    elif task.status in ACTIVE_STATUSES:
        task.cancel_requested = True
    elif task.status not in TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail="This generation cannot be cancelled.")
    task.updated_at = utc_now()
    db.commit()
    db.refresh(task)
    return _task_response(task)


@router.get("/{generation_id}/download")
def download_generation(
    generation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    task = _owned_task(db, generation_id, user.id)
    if task.status == "expired":
        raise HTTPException(status_code=410, detail="The generated file has expired.")
    if task.status != "completed":
        raise HTTPException(status_code=409, detail="The generated file is not ready.")
    artifact = db.query(GeneratedArtifact).filter(
        GeneratedArtifact.generation_id == generation_id,
        GeneratedArtifact.owner_id == user.id,
        GeneratedArtifact.expires_at > utc_now(),
    ).first()
    if artifact is None:
        raise HTTPException(status_code=410, detail="The generated file has expired.")
    return Response(
        content=artifact.content,
        media_type=artifact.media_type,
        headers={"Content-Disposition": f'attachment; filename="{artifact.filename}"'},
    )
