from pathlib import Path

from brain.core.settings import get_settings


def user_workspace_root(owner_id: int, create: bool = False) -> Path:
    projects_root = get_settings().projects_root.resolve()
    workspace_candidate = projects_root / f"user-{owner_id}"
    if workspace_candidate.is_symlink():
        raise PermissionError("User workspace cannot be a symbolic link.")
    workspace_root = workspace_candidate.resolve()
    if not workspace_root.is_relative_to(projects_root):
        raise PermissionError("User workspace escapes PROJECTS_ROOT.")
    if create:
        workspace_root.mkdir(parents=True, exist_ok=True)
    return workspace_root


def resolve_project_path(
    owner_id: int,
    relative_path: str,
    create_root: bool = False,
) -> tuple[Path, str]:
    workspace_root = user_workspace_root(owner_id, create=create_root)
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Project path must be relative to the user's workspace.")
    path = workspace_root
    for part in candidate.parts:
        if part != ".":
            path = path / part
        if path.is_symlink():
            raise PermissionError("Project paths cannot traverse symbolic links.")
    resolved = path.resolve()
    if not resolved.is_relative_to(workspace_root):
        raise ValueError("Project path must remain inside the user's workspace.")
    if not resolved.exists() or not resolved.is_dir():
        raise ValueError("Project directory does not exist.")
    return resolved, resolved.relative_to(workspace_root).as_posix() or "."