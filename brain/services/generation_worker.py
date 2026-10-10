import asyncio
import logging
import time

from sqlalchemy import delete, update
from sqlalchemy.orm import sessionmaker

from brain.core.settings import get_settings
from brain.database.session import SessionLocal
from brain.models.generation import FileGeneration, GeneratedArtifact, utc_now
from brain.services.generation_service import (
    claim_generation,
    execute_generation,
    recover_stale_generations,
)


logger = logging.getLogger(__name__)
SessionFactory = sessionmaker


def _heartbeat(task_id: int, claim_token: str, session_factory: SessionFactory) -> bool:
    with session_factory() as db:
        result = db.execute(
            update(FileGeneration)
            .where(
                FileGeneration.id == task_id,
                FileGeneration.claim_token == claim_token,
            )
            .values(updated_at=utc_now())
        )
        db.commit()
        return result.rowcount == 1


async def _keep_lease(task_id: int, claim_token: str) -> None:
    session_factory = SessionLocal
    interval = max(5, get_settings().generation_task_lease_seconds // 3)
    while True:
        await asyncio.sleep(interval)
        try:
            heartbeat_ok = _heartbeat(task_id, claim_token, session_factory)
        except Exception:
            logger.exception("Unable to renew generation task lease for task %s", task_id)
            return
        if not heartbeat_ok:
            return


def _delete_expired_artifacts(session_factory: SessionFactory) -> None:
    with session_factory() as db:
        now = utc_now()
        expired_ids = [
            generation_id
            for (generation_id,) in db.query(GeneratedArtifact.generation_id).filter(
                GeneratedArtifact.expires_at < now
            ).all()
        ]
        if expired_ids:
            db.query(FileGeneration).filter(
                FileGeneration.id.in_(expired_ids),
                FileGeneration.status == "completed",
            ).update(
                {"status": "expired", "updated_at": now},
                synchronize_session=False,
            )
        db.execute(
            delete(GeneratedArtifact).where(
                GeneratedArtifact.expires_at < now
            )
        )
        db.commit()


async def run_generation_worker() -> None:
    settings = get_settings()
    last_cleanup = time.monotonic()
    last_recovery = last_cleanup - 60
    while True:
        if time.monotonic() - last_recovery >= 60:
            last_recovery = time.monotonic()
            try:
                recover_stale_generations()
            except Exception:
                logger.exception("Unable to recover stale file generation tasks")
        try:
            claimed = claim_generation()
        except Exception:
            logger.exception("Unable to claim a file generation task")
            await asyncio.sleep(settings.generation_worker_poll_seconds)
            continue
        if claimed is None:
            await asyncio.sleep(settings.generation_worker_poll_seconds)
            if time.monotonic() - last_cleanup >= 60:
                try:
                    _delete_expired_artifacts(SessionLocal)
                except Exception:
                    logger.exception("Unable to clean up expired generated artifacts")
                last_cleanup = time.monotonic()
            continue

        task_id, claim_token = claimed
        heartbeat = asyncio.create_task(_keep_lease(task_id, claim_token))
        try:
            await execute_generation(task_id, claim_token)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Generation worker failed on task %s", task_id)
        finally:
            heartbeat.cancel()
            try:
                await heartbeat
            except asyncio.CancelledError:
                pass
            if time.monotonic() - last_cleanup >= 60:
                try:
                    _delete_expired_artifacts(SessionLocal)
                except Exception:
                    logger.exception("Unable to clean up expired generated artifacts")
                last_cleanup = time.monotonic()
