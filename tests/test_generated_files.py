import asyncio
from datetime import timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from brain.api.generated_files_api import router as generated_files_router
from brain.auth.dependencies import get_current_user
from brain.core.settings import Settings, get_settings
from brain.database.session import Base, get_db
from brain.models.generation import (
    FileGeneration,
    GeneratedArtifact,
    utc_now,
)
from brain.models.user import User
from brain.schemas.generated_files import OutputFormat
from brain.services.generation_service import claim_generation, execute_generation
from brain.services.generation_service import recover_stale_generations
from brain.services.generation_worker import _delete_expired_artifacts


class FakeOrchestrator:
    async def generate(self, _prompt, _clarification, _output_format, on_stage):
        await on_stage("requirements")
        await on_stage("planner")
        await on_stage("programmer")
        await on_stage("reviewer")
        await on_stage("validator")
        return "print('hello')\n", "hello.untrusted.py"


def test_generation_queue_download_and_owner_isolation(monkeypatch):
    settings = get_settings()
    original_settings = settings.generated_artifact_retention_days
    settings.generated_artifact_retention_days = 7
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

    def current_user():
        return user_one

    with test_session() as db:
        user_one = User(email="first@example.test", password_hash="unused")
        user_two = User(email="second@example.test", password_hash="unused")
        db.add_all([user_one, user_two])
        db.commit()
        db.refresh(user_one)
        db.refresh(user_two)

    app = FastAPI()
    app.include_router(generated_files_router)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = current_user
    monkeypatch.setattr(
        "brain.services.generation_service.get_settings",
        lambda: settings,
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/files/generate",
                headers={"Idempotency-Key": "request-1"},
                json={"prompt": "Build a greeting program.", "output_format": "py"},
            )
            assert response.status_code == 202
            queued = response.json()
            assert queued["status"] == "queued"
            assert queued["download_url"] is None

            repeated = client.post(
                "/api/files/generate",
                headers={"Idempotency-Key": "request-1"},
                json={"prompt": "Build a greeting program.", "output_format": "py"},
            )
            assert repeated.json()["id"] == queued["id"]

            claim = claim_generation(test_session)
            assert claim is not None
            asyncio.run(execute_generation(
                claim[0],
                claim[1],
                session_factory=test_session,
                orchestrator=FakeOrchestrator(),
            ))

            complete = client.get(f"/api/files/{queued['id']}")
            assert complete.status_code == 200
            assert complete.json()["status"] == "completed"
            assert complete.json()["filename"] == "hello_untrusted.py"

            download = client.get(f"/api/files/{queued['id']}/download")
            assert download.status_code == 200
            assert download.content == b"print('hello')\n"
            assert download.headers["content-type"].startswith("text/x-python")
            assert 'filename="hello_untrusted.py"' in download.headers["content-disposition"]

            pdf_response = client.post(
                "/api/files/generate",
                headers={"Idempotency-Key": "request-pdf"},
                json={"prompt": "Build a greeting program.", "output_format": "pdf"},
            )
            assert pdf_response.status_code == 202
            pdf_claim = claim_generation(test_session)
            assert pdf_claim is not None
            asyncio.run(execute_generation(
                pdf_claim[0],
                pdf_claim[1],
                session_factory=test_session,
                orchestrator=FakeOrchestrator(),
            ))
            pdf_download = client.get(f"/api/files/{pdf_claim[0]}/download")
            assert pdf_download.status_code == 200
            assert pdf_download.content.startswith(b"%PDF")
            assert pdf_download.headers["content-type"] == "application/pdf"

            clarification_task = client.post(
                "/api/files/generate",
                json={"prompt": "Create a program.", "output_format": "py"},
            ).json()
            with test_session() as db:
                pending = db.get(FileGeneration, clarification_task["id"])
                assert pending is not None
                pending.status = "needs_clarification"
                pending.clarification_question = "Which language should I use?"
                db.commit()
            clarification = client.post(
                f"/api/files/{clarification_task['id']}/clarification",
                json={"answer": "Python"},
            )
            assert clarification.status_code == 202
            assert clarification.json()["status"] == "queued"
            assert clarification.json()["clarification_question"] is None

            cancellable = client.post(
                "/api/files/generate",
                json={"prompt": "Create another program.", "output_format": "py"},
            ).json()
            cancelled = client.delete(f"/api/files/{cancellable['id']}")
            assert cancelled.status_code == 200
            assert cancelled.json()["status"] == "cancelled"

            def switch_user_two():
                return user_two

            app.dependency_overrides[get_current_user] = switch_user_two
            unauthorized = client.get(f"/api/files/{queued['id']}/download")
            assert unauthorized.status_code == 404

            invalid_format = client.post(
                "/api/files/generate",
                json={"prompt": "Make a file.", "output_format": "exe"},
            )
            assert invalid_format.status_code == 422
    finally:
        engine.dispose()
        settings.generated_artifact_retention_days = original_settings


def test_generates_pdf_artifact():
    from brain.services.generated_artifacts import make_artifact

    content, media_type = make_artifact("print('hello')", OutputFormat.PDF)
    assert content.startswith(b"%PDF")
    assert media_type == "application/pdf"


def test_huggingface_settings_requirements_and_role_overrides():
    settings = Settings(
        _env_file=None,
        hf_token="test-token",
        hf_default_model="org/default-model",
        hf_programmer_model="org/code-model",
    )
    assert settings.generation_model_for("requirements") == "org/default-model"
    assert settings.generation_model_for("programmer") == "org/code-model"


def test_stale_task_recovery_and_expired_artifact_cleanup(monkeypatch):
    settings = Settings(_env_file=None, generation_task_lease_seconds=60)
    monkeypatch.setattr(
        "brain.services.generation_service.get_settings",
        lambda: settings,
    )
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with test_session() as db:
        user = User(email="lease@example.test", password_hash="unused")
        db.add(user)
        db.flush()
        stale = FileGeneration(
            owner_id=user.id,
            prompt="stale",
            output_format="py",
            status="generating",
            current_stage="programmer",
            claim_token="expired-lease",
            updated_at=utc_now() - timedelta(seconds=120),
        )
        expired = FileGeneration(
            owner_id=user.id,
            prompt="expired",
            output_format="py",
            status="completed",
        )
        db.add_all([stale, expired])
        db.flush()
        db.add(GeneratedArtifact(
            generation_id=expired.id,
            owner_id=user.id,
            filename="old.py",
            media_type="text/x-python",
            content=b"print('old')",
            expires_at=utc_now() - timedelta(seconds=1),
        ))
        db.commit()
        stale_id = stale.id
        expired_id = expired.id

    recover_stale_generations(test_session)
    _delete_expired_artifacts(test_session)

    with test_session() as db:
        stale = db.get(FileGeneration, stale_id)
        expired = db.get(FileGeneration, expired_id)
        assert stale is not None and stale.status == "queued"
        assert stale.claim_token is None
        assert expired is not None and expired.status == "expired"
        assert db.query(GeneratedArtifact).filter(
            GeneratedArtifact.generation_id == expired_id
        ).count() == 0
    engine.dispose()
