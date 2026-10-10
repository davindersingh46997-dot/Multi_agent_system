from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from brain.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def artifact_expiry(retention_days: int = 7) -> datetime:
    return utc_now() + timedelta(days=retention_days)


class FileGeneration(Base):
    __tablename__ = "file_generations"
    __table_args__ = (
        UniqueConstraint("owner_id", "idempotency_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    clarification: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_format: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    current_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    claim_token: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    filename: Mapped[str | None] = mapped_column(String(100), nullable=True)
    clarification_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class GeneratedArtifact(Base):
    __tablename__ = "generated_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(
        ForeignKey("file_generations.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(100))
    media_type: Mapped[str] = mapped_column(String(100))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
