from datetime import timedelta
import logging

from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

from brain.agents.file_generation import (
    FileGenerationOrchestrator,
    GenerationClarificationRequired,
    GenerationValidationError,
)
from brain.core.huggingface_models import (
    HuggingFaceConfigurationError,
    HuggingFaceProviderError,
)
from brain.core.settings import get_settings
from brain.database.session import SessionLocal
from brain.models.generation import (
    FileGeneration,
    GeneratedArtifact,
    artifact_expiry,
    utc_now,
)
from brain.schemas.generated_files import OutputFormat
from brain.services.generated_artifacts import make_artifact, safe_filename


logger = logging.getLogger(__name__)
SessionFactory = sessionmaker


class GenerationCancelledError(RuntimeError):
    pass


class GenerationLeaseLostError(RuntimeError):
    pass


def recover_stale_generations(session_factory: SessionFactory = SessionLocal) -> None:
    settings = get_settings()
    cutoff = utc_now() - timedelta(seconds=settings.generation_task_lease_seconds)
    active_statuses = ["analyzing", "planning", "generating", "reviewing", "validating"]
    with session_factory() as db:
        db.execute(
            update(FileGeneration)
            .where(
                FileGeneration.status.in_(active_statuses),
                FileGeneration.updated_at < cutoff,
                FileGeneration.cancel_requested.is_(True),
            )
            .values(status="cancelled", current_stage=None, claim_token=None)
        )
        db.execute(
            update(FileGeneration)
            .where(
                FileGeneration.status.in_(active_statuses),
                FileGeneration.updated_at < cutoff,
                FileGeneration.cancel_requested.is_(False),
            )
            .values(status="queued", current_stage=None, claim_token=None)
        )
        db.commit()


def claim_generation(session_factory: SessionFactory = SessionLocal) -> tuple[int, str] | None:
    with session_factory() as db:
        task_id = db.query(FileGeneration.id).filter(
            FileGeneration.status == "queued"
        ).order_by(FileGeneration.created_at, FileGeneration.id).limit(1).scalar()
        if task_id is None:
            return None
        from uuid import uuid4

        token = uuid4().hex
        result = db.execute(
            update(FileGeneration)
            .where(
                FileGeneration.id == task_id,
                FileGeneration.status == "queued",
            )
            .values(
                status="analyzing",
                current_stage="requirements",
                claim_token=token,
                updated_at=utc_now(),
            )
        )
        db.commit()
        if result.rowcount != 1:
            return None
        return task_id, token


def _set_failure(
    task_id: int,
    claim_token: str,
    error: str,
    session_factory: SessionFactory,
) -> None:
    with session_factory() as db:
        task = db.query(FileGeneration).filter(
            FileGeneration.id == task_id,
            FileGeneration.claim_token == claim_token,
        ).first()
        if task is None:
            return
        task.status = "cancelled" if task.cancel_requested else "failed"
        task.error = None if task.cancel_requested else error
        task.current_stage = None
        task.claim_token = None
        task.updated_at = utc_now()
        db.commit()


async def execute_generation(
    task_id: int,
    claim_token: str,
    session_factory: SessionFactory = SessionLocal,
    orchestrator: FileGenerationOrchestrator | None = None,
) -> None:
    settings = get_settings()
    with session_factory() as db:
        task = db.get(FileGeneration, task_id)
        if task is None or task.claim_token != claim_token:
            return
        prompt = task.prompt
        clarification = task.clarification
        output_format = OutputFormat(task.output_format)

    try:
        generator = orchestrator or FileGenerationOrchestrator(settings)

        async def update_stage(stage: str) -> None:
            status_by_stage = {
                "requirements": "analyzing",
                "planner": "planning",
                "programmer": "generating",
                "reviewer": "reviewing",
                "validator": "validating",
            }
            with session_factory() as db:
                task = db.get(FileGeneration, task_id)
                if task is None or task.claim_token != claim_token:
                    raise GenerationLeaseLostError("Generation task lease is no longer active.")
                if task.cancel_requested:
                    raise GenerationCancelledError("Generation was cancelled.")
                task.current_stage = stage
                task.status = status_by_stage[stage]
                task.updated_at = utc_now()
                db.commit()

        content, filename_suggestion = await generator.generate(
            prompt,
            clarification,
            output_format,
            update_stage,
        )
        source_bytes = content.encode("utf-8")
        if len(source_bytes) > settings.max_generation_output_bytes:
            raise GenerationValidationError("Generated content exceeds the configured output limit.")
        artifact_content, media_type = make_artifact(content, output_format)
        if len(artifact_content) > settings.max_generation_output_bytes:
            raise GenerationValidationError("Generated artifact exceeds the configured output limit.")
        filename = safe_filename(filename_suggestion, task_id, output_format)

        with session_factory() as db:
            task = db.get(FileGeneration, task_id)
            if task is None or task.claim_token != claim_token:
                raise GenerationLeaseLostError("Generation task lease is no longer active.")
            if task.cancel_requested:
                task.status = "cancelled"
                task.current_stage = None
                task.claim_token = None
                task.updated_at = utc_now()
                db.commit()
                return
            db.add(GeneratedArtifact(
                generation_id=task_id,
                owner_id=task.owner_id,
                filename=filename,
                media_type=media_type,
                content=artifact_content,
                expires_at=artifact_expiry(settings.generated_artifact_retention_days),
            ))
            task.filename = filename
            task.status = "completed"
            task.current_stage = None
            task.claim_token = None
            task.error = None
            task.clarification_question = None
            task.updated_at = utc_now()
            db.commit()
    except GenerationClarificationRequired as exc:
        with session_factory() as db:
            task = db.query(FileGeneration).filter(
                FileGeneration.id == task_id,
                FileGeneration.claim_token == claim_token,
            ).first()
            if task is None:
                return
            task.status = "cancelled" if task.cancel_requested else "needs_clarification"
            task.current_stage = None
            task.clarification_question = (
                None if task.cancel_requested else exc.question
            )
            task.claim_token = None
            task.updated_at = utc_now()
            db.commit()
    except GenerationCancelledError:
        with session_factory() as db:
            db.execute(
                update(FileGeneration)
                .where(
                    FileGeneration.id == task_id,
                    FileGeneration.claim_token == claim_token,
                )
                .values(
                    status="cancelled",
                    current_stage=None,
                    claim_token=None,
                    updated_at=utc_now(),
                )
            )
            db.commit()
    except GenerationLeaseLostError:
        logger.info("Generation task %s lost its worker lease", task_id)
    except HuggingFaceConfigurationError as exc:
        _set_failure(task_id, claim_token, str(exc), session_factory)
    except HuggingFaceProviderError:
        _set_failure(
            task_id,
            claim_token,
            "Hugging Face inference failed. Check model availability and provider configuration.",
            session_factory,
        )
    except GenerationValidationError as exc:
        _set_failure(task_id, claim_token, str(exc), session_factory)
    except Exception as exc:
        logger.error(
            "File generation task %s failed unexpectedly (%s)",
            task_id,
            type(exc).__name__,
        )
        _set_failure(
            task_id,
            claim_token,
            "File generation failed unexpectedly. Please retry the task.",
            session_factory,
        )
