import difflib
import hashlib
from pathlib import Path
import tempfile

from fastmcp import FastMCP
from sqlalchemy.orm import sessionmaker

from brain.models.project import DeveloperTask, TaskChange
from brain.services.retrieval_service import retrieve


BLOCKED_NAMES = {".env", "credentials", "secrets.json", "id_rsa", "id_ed25519"}
BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".db"}
MAX_READ_BYTES = 256_000


class WorkspaceMCP:
    def __init__(
        self,
        project_root: Path,
        project_id: int,
        task_id: int,
        session_factory: sessionmaker,
    ) -> None:
        self.project_root = project_root.resolve()
        self.project_id = project_id
        self.task_id = task_id
        self.session_factory = session_factory
        self.server = FastMCP(name="multi-agent-workspace")
        self.server.tool(name="list_workspace")(self.list_workspace)
        self.server.tool(name="read_project_file")(self.read_project_file)
        self.server.tool(name="search_project")(self.search_project)
        self.server.tool(name="propose_file_change")(self.propose_file_change)

    def _safe_path(self, relative_path: str) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise PermissionError("Absolute paths and traversal are not permitted.")
        path = self.project_root
        for part in candidate.parts:
            if part != ".":
                path = path / part
            if path.is_symlink():
                raise PermissionError("Symbolic links are not available to agent tools.")
        path = path.resolve()
        if not path.is_relative_to(self.project_root):
            raise PermissionError("Path escapes the authorized project.")
        if _is_sensitive(path):
            raise PermissionError("Sensitive files are not available to agent tools.")
        return path

    def list_workspace(self, directory_path: str = ".") -> list[str]:
        path = self._safe_path(directory_path)
        if not path.is_dir():
            raise NotADirectoryError(directory_path)
        entries = []
        for entry in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
            if entry.name in {".git", ".venv", "node_modules", "__pycache__"}:
                continue
            if entry.name.lower().startswith(".env"):
                continue
            entries.append(f"[DIR] {entry.name}" if entry.is_dir() else f"[FILE] {entry.name}")
        return entries

    def read_project_file(self, relative_path: str) -> str:
        path = self._safe_path(relative_path)
        if not path.is_file():
            raise FileNotFoundError(relative_path)
        if path.stat().st_size > MAX_READ_BYTES:
            raise ValueError("File exceeds the maximum readable size.")
        return path.read_text(encoding="utf-8")

    def search_project(self, query: str, limit: int = 8) -> list[dict[str, object]]:
        with self.session_factory() as db:
            results = retrieve(db, self.project_id, query, min(max(limit, 1), 12))
        return results

    def propose_file_change(self, relative_path: str, content: str) -> dict[str, object]:
        path = self._safe_path(relative_path)
        if path.exists() and not path.is_file():
            raise IsADirectoryError(relative_path)
        if len(content.encode("utf-8")) > MAX_READ_BYTES:
            raise ValueError("Proposed file exceeds the maximum size.")

        original = path.read_text(encoding="utf-8") if path.exists() else ""
        original_hash = hashlib.sha256(original.encode("utf-8")).hexdigest() if path.exists() else None
        proposed_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        diff = "".join(difflib.unified_diff(
            original.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"a/{relative_path}" if path.exists() else "/dev/null",
            tofile=f"b/{relative_path}",
        ))

        with self.session_factory() as db:
            task = db.get(DeveloperTask, self.task_id)
            if task is None or task.project_id != self.project_id:
                raise PermissionError("Task is not authorized for this project.")
            db.query(TaskChange).filter(
                TaskChange.task_id == self.task_id,
                TaskChange.relative_path == relative_path,
                TaskChange.status == "pending",
            ).delete()
            change = TaskChange(
                task_id=self.task_id,
                relative_path=relative_path,
                original_hash=original_hash,
                proposed_hash=proposed_hash,
                proposed_content=content,
                diff=diff,
                status="pending",
            )
            db.add(change)
            db.commit()
            db.refresh(change)
            return {
                "change_id": change.id,
                "path": relative_path,
                "diff": diff,
                "approval_required": True,
                "approval_hash": proposed_hash,
            }


def apply_approved_change(
    project_root: Path,
    change: TaskChange,
    approved_hash: str,
) -> None:
    if change.status != "pending" or approved_hash != change.proposed_hash:
        raise ValueError("Approval does not match the pending change.")

    root = project_root.resolve()
    candidate = Path(change.relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise PermissionError("Absolute paths and traversal are not permitted.")
    target = root
    for part in candidate.parts:
        target = target / part if part != "." else target
        if target.is_symlink():
            raise PermissionError("Symbolic links cannot be modified.")
    target = target.resolve()
    if not target.is_relative_to(root):
        raise PermissionError("Path escapes the authorized project.")
    if _is_sensitive(target):
        raise PermissionError("Sensitive files cannot be modified.")

    current = target.read_text(encoding="utf-8") if target.exists() else None
    current_hash = hashlib.sha256(current.encode("utf-8")).hexdigest() if current is not None else None
    if current_hash != change.original_hash:
        raise RuntimeError("The file changed after the proposal; create a new proposal.")
    if hashlib.sha256(change.proposed_content.encode("utf-8")).hexdigest() != change.proposed_hash:
        raise RuntimeError("The stored proposal failed integrity verification.")

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=target.parent, delete=False
    ) as temporary_file:
        temporary_file.write(change.proposed_content)
        temporary_path = Path(temporary_file.name)
    try:
        temporary_path.replace(target)
    finally:
        temporary_path.unlink(missing_ok=True)


def _is_sensitive(path: Path) -> bool:
    name = path.name.lower()
    return (
        name in BLOCKED_NAMES
        or name.startswith(".env")
        or path.suffix.lower() in BLOCKED_SUFFIXES
    )