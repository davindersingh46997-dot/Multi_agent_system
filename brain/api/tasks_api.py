from pathlib import Path
from uuid import uuid4
from io import BytesIO
import warnings

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from brain.auth.dependencies import get_current_user
from brain.core.settings import get_settings
from brain.core.workspaces import resolve_project_path
from brain.database.session import SessionLocal, get_db
from brain.models.project import DeveloperTask, Project, TaskAttachment, TaskChange
from brain.models.user import User
from brain.schemas.tasks import ChangeApprovalRequest, TaskChangeResponse, TaskResponse
from brain.services.task_service import execute_task
from brain.tools.workspace_mcp import apply_approved_change


router = APIRouter(prefix="/api/tasks", tags=["Developer tasks"])
IMAGE_TYPES = {
    "image/png": ("png", "PNG", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/jpeg": ("jpg", "JPEG", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/webp": ("webp", "WEBP", lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP"),
}


def _task_response(db: Session, task: DeveloperTask) -> TaskResponse:
    changes = db.query(TaskChange).filter(TaskChange.task_id == task.id).order_by(TaskChange.id).all()
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        prompt=task.prompt,
        status=task.status,
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        changes=[
            TaskChangeResponse(
                id=change.id,
                relative_path=change.relative_path,
                diff=change.diff,
                status=change.status,
                approval_hash=change.proposed_hash,
            )
            for change in changes
        ],
    )


def _owned_task(db: Session, task_id: int, owner_id: int) -> DeveloperTask:
    task = db.query(DeveloperTask).filter(
        DeveloperTask.id == task_id,
        DeveloperTask.owner_id == owner_id,
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    background_tasks: BackgroundTasks,
    project_id: int = Form(...),
    prompt: str = Form(..., min_length=1, max_length=8000),
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TaskResponse:
    prompt = prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Task prompt cannot be blank.")
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    upload_data: tuple[str, str, str, int, bytes] | None = None
    if image is not None:
        media_type = image.content_type or ""
        image_type = IMAGE_TYPES.get(media_type)
        if image_type is None:
            raise HTTPException(status_code=415, detail="Upload a PNG, JPEG, or WebP image.")
        data = await image.read(get_settings().max_upload_bytes + 1)
        if len(data) > get_settings().max_upload_bytes:
            raise HTTPException(status_code=413, detail="Image exceeds the configured upload limit.")
        extension, expected_format, validate_signature = image_type
        if not validate_signature(data):
            raise HTTPException(status_code=415, detail="Image content does not match its media type.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(data)) as decoded_image:
                    if decoded_image.format != expected_format:
                        raise HTTPException(status_code=415, detail="Unsupported image encoding.")
                    if decoded_image.width * decoded_image.height > get_settings().max_image_pixels:
                        raise HTTPException(status_code=413, detail="Image dimensions exceed the configured limit.")
                    decoded_image.verify()
        except HTTPException:
            raise
        except (Image.DecompressionBombError, Image.DecompressionBombWarning, UnidentifiedImageError, OSError, ValueError) as exc:
            raise HTTPException(status_code=415, detail="Image could not be safely decoded.") from exc
        safe_name = Path(image.filename or "image").name[:255]
        storage_name = f"{user.id}/{uuid4().hex}.{extension}"
        upload_data = (storage_name, safe_name, media_type, len(data), data)

    task = DeveloperTask(
        owner_id=user.id,
        project_id=project.id,
        prompt=prompt,
        status="queued",
    )
    db.add(task)
    db.flush()
    if upload_data:
        storage_name, original_name, media_type, byte_count, data = upload_data
        upload_root = get_settings().uploads_root.resolve()
        destination = (upload_root / storage_name).resolve()
        if not destination.is_relative_to(upload_root):
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid attachment location.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        db.add(TaskAttachment(
            task_id=task.id,
            storage_name=storage_name,
            original_name=original_name,
            media_type=media_type,
            byte_count=byte_count,
        ))
    db.commit()
    db.refresh(task)
    response = _task_response(db, task)
    background_tasks.add_task(execute_task, task.id)
    return response


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[TaskResponse]:
    tasks = db.query(DeveloperTask).filter(
        DeveloperTask.owner_id == user.id
    ).order_by(DeveloperTask.created_at.desc()).limit(100).all()
    return [_task_response(db, task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TaskResponse:
    return _task_response(db, _owned_task(db, task_id, user.id))


@router.post("/{task_id}/changes/{change_id}/approval", response_model=TaskResponse)
def decide_change(
    task_id: int,
    change_id: int,
    request: ChangeApprovalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TaskResponse:
    task = _owned_task(db, task_id, user.id)
    change = db.query(TaskChange).filter(
        TaskChange.id == change_id,
        TaskChange.task_id == task.id,
    ).first()
    if change is None:
        raise HTTPException(status_code=404, detail="Change proposal not found.")
    if change.status != "pending" or request.approval_hash != change.proposed_hash:
        raise HTTPException(status_code=409, detail="Approval does not match a pending proposal.")

    if request.approved:
        project = db.get(Project, task.project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found.")
        try:
            root, _ = resolve_project_path(project.owner_id, project.relative_path)
            apply_approved_change(root, change, request.approval_hash)
        except (OSError, PermissionError, RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        change.status = "applied"
    else:
        change.status = "rejected"

    db.flush()
    pending_count = db.query(TaskChange).filter(
        TaskChange.task_id == task.id,
        TaskChange.status == "pending",
    ).count()
    if not pending_count:
        task.status = "completed"
    db.commit()
    db.refresh(task)
    return _task_response(db, task)