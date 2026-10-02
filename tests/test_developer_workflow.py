import asyncio
import hashlib
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastmcp import Client
from langchain_core.messages import AIMessage
from PIL import Image
from pydantic import SecretStr
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from brain.api.auth_api import router as auth_router
from brain.api.projects_api import router as projects_router
from brain.api.tasks_api import router as tasks_router
from brain.agents.supervisor import SupervisorAgent
from brain.core.settings import get_settings
from brain.database.session import Base, get_db
from brain.models.project import DeveloperTask, Project, TaskChange
from brain.models.user import User
from brain.services.retrieval_service import index_project, retrieve
from brain.tools.workspace_mcp import WorkspaceMCP, apply_approved_change
from brain.tools.file_tools import FileCreaterTool, FileReaderTool, FileWriterTool


def _png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (2, 2), color="white").save(buffer, format="PNG")
    return buffer.getvalue()


def test_auth_project_and_image_task_without_model(tmp_path, monkeypatch):
    settings = get_settings()
    original_values = {
        "projects_root": settings.projects_root,
        "uploads_root": settings.uploads_root,
        "auth_secret_key": settings.auth_secret_key,
        "model_provider": settings.model_provider,
        "model_name": settings.model_name,
        "model_api_key": settings.model_api_key,
    }
    projects_root = tmp_path / "projects"
    projects_root.mkdir()
    user_root = projects_root / "user-1"
    user_root.mkdir()
    (user_root / "sample.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    settings.projects_root = projects_root
    settings.uploads_root = tmp_path / "uploads"
    settings.auth_secret_key = SecretStr("test-only-signing-secret-at-least-32-bytes")
    settings.model_provider = None
    settings.model_name = None
    settings.model_api_key = None

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with test_session() as db:
            yield db

    app = FastAPI()
    app.include_router(auth_router, prefix="/api")
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.dependency_overrides[get_db] = override_get_db

    import brain.services.task_service as task_service

    monkeypatch.setattr(task_service, "SessionLocal", test_session)
    try:
        with TestClient(app) as client:
            registered = client.post(
                "/api/auth/register",
                json={"email": "dev@example.com", "password": "long-password"},
            )
            assert registered.status_code == 201

            login = client.post(
                "/api/auth/login",
                json={"username": "dev@example.com", "password": "long-password"},
            )
            assert login.status_code == 200
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

            project = client.post(
                "/api/projects",
                headers=headers,
                json={"name": "fixture", "relative_path": "."},
            )
            assert project.status_code == 201
            project_id = project.json()["id"]

            unsafe_project = client.post(
                "/api/projects",
                headers=headers,
                json={"name": "escape", "relative_path": "../"},
            )
            assert unsafe_project.status_code == 400

            client.post(
                "/api/auth/register",
                json={"email": "other@example.com", "password": "another-password"},
            )
            other_login = client.post(
                "/api/auth/login",
                json={"email": "other@example.com", "password": "another-password"},
            )
            other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}
            other_projects = client.get("/api/projects", headers=other_headers)
            assert other_projects.status_code == 200
            assert other_projects.json() == []
            cross_user_path = client.post(
                "/api/projects",
                headers=other_headers,
                json={"name": "escape", "relative_path": "../user-1"},
            )
            assert cross_user_path.status_code == 400

            task = client.post(
                "/api/tasks",
                headers=headers,
                data={"project_id": project_id, "prompt": "Read the code in this image"},
                files={"image": ("sample.png", _png_bytes(), "image/png")},
            )
            assert task.status_code == 202
            task_id = task.json()["id"]
            status_response = client.get(f"/api/tasks/{task_id}", headers=headers)
            assert status_response.status_code == 200
            assert status_response.json()["status"] == "awaiting_configuration"
            assert "MODEL_PROVIDER and MODEL_NAME" in status_response.json()["error"]
            assert (settings.uploads_root / "1").is_dir()

            settings.model_provider = "test-provider"
            settings.model_name = "test-model"

            class FakeSupervisor:
                def __init__(self, **kwargs):
                    pass

                async def run(self, task, retrieve_evidence, images, load_diffs):
                    evidence = retrieve_evidence(f"{task} answer function")
                    assert "sample.py" in evidence
                    assert images[0][0] == "image/png"
                    assert images[0][1].startswith(b"\x89PNG\r\n\x1a\n")
                    return "Image and project evidence reviewed."

            monkeypatch.setattr(
                task_service.ModelFactory,
                "create_model",
                staticmethod(lambda configured_settings: object()),
            )
            monkeypatch.setattr(task_service, "SupervisorAgent", FakeSupervisor)
            configured_task = client.post(
                "/api/tasks",
                headers=headers,
                data={"project_id": project_id, "prompt": "Analyze this code screenshot"},
                files={"image": ("again.png", _png_bytes(), "image/png")},
            )
            assert configured_task.status_code == 202
            configured_id = configured_task.json()["id"]
            completed_task = client.get(f"/api/tasks/{configured_id}", headers=headers)
            assert completed_task.json()["status"] == "completed"
            assert completed_task.json()["result"] == "Image and project evidence reviewed."
    finally:
        engine.dispose()
        for name, value in original_values.items():
            setattr(settings, name, value)


def test_retrieval_skips_secrets_and_matches_code_identifiers(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "billing.py").write_text(
        "def calculate_total(items):\n    return sum(items)\n", encoding="utf-8"
    )
    (root / ".env").write_text("MODEL_API_KEY=do-not-index", encoding="utf-8")

    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    try:
        with factory() as db:
            user = User(email="rag@example.test", password_hash="unused")
            db.add(user)
            db.flush()
            project = Project(owner_id=user.id, name="test", relative_path=".")
            db.add(project)
            db.flush()
            index_project(db, project, root)
            results = retrieve(db, project.id, "calculate total")
            assert results and results[0]["path"] == "billing.py"
            assert all(".env" not in result["path"] for result in results)
    finally:
        engine.dispose()


def test_fastmcp_stages_change_without_writing_source(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    source = root / "sample.py"
    source.write_text("before\n", encoding="utf-8")
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    try:
        with factory() as db:
            user = User(email="mcp@example.test", password_hash="unused")
            db.add(user)
            db.flush()
            project = Project(owner_id=user.id, name="test", relative_path=".")
            db.add(project)
            db.flush()
            task = DeveloperTask(owner_id=user.id, project_id=project.id, prompt="change")
            db.add(task)
            db.flush()
            project_id, task_id = project.id, task.id
            db.commit()

        workspace = WorkspaceMCP(root, project_id, task_id, factory)

        async def stage_change():
            async with Client(workspace.server) as client:
                result = await client.call_tool(
                    "propose_file_change",
                    {"relative_path": "sample.py", "content": "after\n"},
                )
                assert not result.is_error

        asyncio.run(stage_change())
        assert source.read_text(encoding="utf-8") == "before\n"
        with factory() as db:
            change = db.query(TaskChange).one()
            assert change.status == "pending"
            assert change.original_hash == hashlib.sha256(b"before\n").hexdigest()
            assert "-before" in change.diff
            assert "after" in change.diff
    finally:
        engine.dispose()


def test_approved_change_checks_source_and_proposal_hash(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("before\n", encoding="utf-8")
    proposed = "after\n"
    change = TaskChange(
        relative_path="sample.py",
        original_hash=hashlib.sha256(b"before\n").hexdigest(),
        proposed_hash=hashlib.sha256(proposed.encode()).hexdigest(),
        proposed_content=proposed,
        diff="diff",
        status="pending",
    )
    apply_approved_change(tmp_path, change, change.proposed_hash)
    assert source.read_text(encoding="utf-8") == proposed

    with TemporaryDirectory() as other_directory:
        other_root = Path(other_directory)
        (other_root / "sample.py").write_text("concurrent edit\n", encoding="utf-8")
        try:
            apply_approved_change(other_root, change, change.proposed_hash)
        except RuntimeError as exc:
            assert "changed after the proposal" in str(exc)
        else:
            raise AssertionError("Stale source must not be overwritten")


def test_supervisor_uses_image_analysis_as_retrieval_query():
    class FakeModel:
        async def ainvoke(self, messages):
            return AIMessage(content="Visible function answer_value has a return statement.")

    class FakeProgrammer:
        async def run(self, task, context):
            assert "canonical.py" in context["evidence"]
            return "Staged a reviewed proposal."

    class FakeReviewer:
        async def run(self, task, context):
            return "No issues found in the provided diff."

    retrieval_queries = []

    def retrieve_evidence(query):
        retrieval_queries.append(query)
        return "Evidence: canonical.py:1-2\ndef answer_value(): return 42"

    supervisor = SupervisorAgent(
        model=FakeModel(),
        programmer=FakeProgrammer(),
        reviewer=FakeReviewer(),
    )
    result = asyncio.run(supervisor.run(
        task="Explain the screenshot",
        retrieve_evidence=retrieve_evidence,
        images=[("image/png", b"test image data")],
        load_diffs=lambda: "",
    ))
    assert retrieval_queries
    assert "answer_value" in retrieval_queries[0]
    assert "canonical.py" in result


def test_legacy_file_tools_cannot_bypass_approval(tmp_path):
    (tmp_path / "sample.py").write_text("before\n", encoding="utf-8")
    reader = FileReaderTool(str(tmp_path))
    writer = FileWriterTool(str(tmp_path))
    creator = FileCreaterTool(str(tmp_path))

    assert reader.execute("sample.py") == "before\n"
    with pytest.raises(PermissionError, match="Direct writes are disabled"):
        writer.execute("sample.py", "after\n")
    with pytest.raises(PermissionError, match="Direct file creation is disabled"):
        creator.execute("new.py")
    with pytest.raises(PermissionError):
        reader.execute("../outside.py")