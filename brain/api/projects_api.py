from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from brain.auth.dependencies import get_current_user
from brain.database.session import get_db
from brain.core.workspaces import resolve_project_path
from brain.models.project import Project
from brain.models.user import User
from brain.schemas.projects import ProjectCreate, ProjectResponse


router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProjectResponse:
    try:
        _, normalized_path = resolve_project_path(
            user.id, request.relative_path, create_root=True
        )
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    project = Project(
        owner_id=user.id,
        name=request.name.strip(),
        relative_path=normalized_path,
    )
    db.add(project)
    try:
        db.commit()
        db.refresh(project)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This directory is already registered to your account.",
        ) from exc
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ProjectResponse]:
    projects = db.query(Project).filter(Project.owner_id == user.id).order_by(Project.id).all()
    return [ProjectResponse.model_validate(project) for project in projects]


def get_owned_project(db: Session, project_id: int, user_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.owner_id == user_id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project