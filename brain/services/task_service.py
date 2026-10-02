import logging
from pathlib import Path

from fastmcp import Client
from langchain_core.tools import StructuredTool

from brain.agents.programmer import ProgrammerAgent
from brain.agents.supervisor import SupervisorAgent
from brain.agents.tester import ReviewerAgent
from brain.core.model_factory import ModelConfigurationError, ModelFactory
from brain.core.settings import get_settings
from brain.core.workspaces import resolve_project_path
from brain.database.session import SessionLocal
from brain.models.project import DeveloperTask, Project, TaskAttachment, TaskChange
from brain.services.retrieval_service import format_evidence, index_project, retrieve
from brain.tools.workspace_mcp import WorkspaceMCP


logger = logging.getLogger(__name__)
def _agent_tools(workspace: WorkspaceMCP) -> list[StructuredTool]:
    async def call_mcp(name: str, arguments: dict[str, object]) -> str:
        async with Client(workspace.server) as client:
            result = await client.call_tool(name, arguments)
        if result.is_error:
            raise RuntimeError(f"Workspace tool {name} failed.")
        if result.structured_content is not None:
            return str(result.structured_content)
        return "\n".join(
            item.text for item in result.content if hasattr(item, "text")
        )

    async def list_workspace(directory_path: str = ".") -> str:
        return await call_mcp("list_workspace", {"directory_path": directory_path})

    async def read_project_file(relative_path: str) -> str:
        return await call_mcp("read_project_file", {"relative_path": relative_path})

    async def search_project(query: str, limit: int = 8) -> str:
        return await call_mcp("search_project", {"query": query, "limit": limit})

    async def propose_file_change(relative_path: str, content: str) -> str:
        return await call_mcp(
            "propose_file_change",
            {"relative_path": relative_path, "content": content},
        )

    return [
        StructuredTool.from_function(
            name="list_workspace",
            description="List safe entries in the assigned project directory.",
            coroutine=list_workspace,
        ),
        StructuredTool.from_function(
            name="read_project_file",
            description="Read a bounded, non-secret UTF-8 project file.",
            coroutine=read_project_file,
        ),
        StructuredTool.from_function(
            name="search_project",
            description="Search indexed source in the assigned project.",
            coroutine=search_project,
        ),
        StructuredTool.from_function(
            name="propose_file_change",
            description="Stage a complete file replacement for user review; never applies it.",
            coroutine=propose_file_change,
        ),
    ]


async def execute_task(task_id: int) -> None:
    settings = get_settings()
    try:
        with SessionLocal() as db:
            task = db.get(DeveloperTask, task_id)
            if task is None:
                return
            project = db.get(Project, task.project_id)
            if project is None:
                task.status = "failed"
                task.error = "The selected project no longer exists."
                db.commit()
                return
            project_id = project.id
            task.status = "indexing"
            task.error = None
            db.commit()
            root, _ = resolve_project_path(project.owner_id, project.relative_path)
            indexed_count = index_project(db, project, root)
            attachments = db.query(TaskAttachment).filter(
                TaskAttachment.task_id == task.id
            ).all()
            attachment_records = [
                (attachment.storage_name, attachment.media_type)
                for attachment in attachments
            ]
            prompt = task.prompt
            db.commit()

        try:
            model = ModelFactory.create_model(settings)
        except ModelConfigurationError as exc:
            with SessionLocal() as db:
                task = db.get(DeveloperTask, task_id)
                if task:
                    task.status = "awaiting_configuration"
                    task.error = str(exc)
                    db.commit()
            return

        workspace = WorkspaceMCP(root, project_id, task_id, SessionLocal)
        programmer = ProgrammerAgent(model, _agent_tools(workspace))
        supervisor = SupervisorAgent(
            model=model,
            programmer=programmer,
            reviewer=ReviewerAgent("Reviewer", model),
        )
        image_inputs: list[tuple[str, bytes]] = []
        upload_root = settings.uploads_root.resolve()
        for storage_name, media_type in attachment_records:
            image_path = (upload_root / storage_name).resolve()
            if not image_path.is_relative_to(upload_root) or not image_path.is_file():
                raise PermissionError("Task image attachment is unavailable.")
            image_inputs.append((media_type, image_path.read_bytes()))

        with SessionLocal() as db:
            task = db.get(DeveloperTask, task_id)
            if task:
                task.status = "analyzing"
                db.commit()
        def load_diffs() -> str:
            with SessionLocal() as db:
                changes = db.query(TaskChange).filter(
                    TaskChange.task_id == task_id,
                    TaskChange.status == "pending",
                ).order_by(TaskChange.id).all()
                return "\n\n".join(change.diff for change in changes)

        def retrieve_evidence(query: str) -> str:
            with SessionLocal() as db:
                matches = retrieve(db, project_id, query)
                return (
                    f"{indexed_count} project chunks were indexed.\n"
                    f"{format_evidence(matches)}"
                )

        result_text = await supervisor.run(
            task=prompt,
            retrieve_evidence=retrieve_evidence,
            images=image_inputs,
            load_diffs=load_diffs,
        )

        with SessionLocal() as db:
            task = db.get(DeveloperTask, task_id)
            if task is None:
                return
            pending_changes = db.query(TaskChange).filter(
                TaskChange.task_id == task_id,
                TaskChange.status == "pending",
            ).count()
            task.result = result_text
            task.status = "awaiting_approval" if pending_changes else "completed"
            task.error = None
            db.commit()
    except Exception:
        logger.exception("Developer task %s failed", task_id)
        with SessionLocal() as db:
            task = db.get(DeveloperTask, task_id)
            if task:
                task.status = "failed"
                task.error = "Task execution failed. Check the server log for its task ID."
                db.commit()