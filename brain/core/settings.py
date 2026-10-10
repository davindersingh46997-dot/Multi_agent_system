from functools import lru_cache
from pathlib import Path
import secrets
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./multi_agent.db"
    projects_root: Path = Path("workspace")
    uploads_root: Path = Path(".multi_agent/uploads")
    model_provider: str | None = None
    model_name: str | None = None
    model_api_key: SecretStr | None = None
    model_base_url: str | None = None
    hf_token: SecretStr | None = None
    hf_inference_provider: Literal["auto", "hf-inference"] = "auto"
    hf_default_model: str | None = None
    hf_requirements_model: str | None = None
    hf_planner_model: str | None = None
    hf_programmer_model: str | None = None
    hf_reviewer_model: str | None = None
    hf_validator_model: str | None = None
    hf_inference_timeout_seconds: int = Field(default=90, ge=10, le=300)
    generation_max_revision_rounds: int = Field(default=2, ge=0, le=4)
    max_generation_output_bytes: int = Field(default=1_000_000, ge=1024, le=5_000_000)
    generated_artifact_retention_days: int = Field(default=7, ge=1, le=365)
    generation_task_lease_seconds: int = Field(default=600, ge=60, le=3600)
    generation_worker_poll_seconds: int = Field(default=1, ge=1, le=30)
    auth_secret_key: SecretStr | None = None
    access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)
    max_upload_bytes: int = Field(default=8_000_000, ge=1024, le=50_000_000)
    max_image_pixels: int = Field(default=25_000_000, ge=1_000_000, le=100_000_000)
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    _development_secret: str = ""

    @field_validator("model_provider", "model_name", "model_base_url", mode="before")
    @classmethod
    def blank_text_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("model_api_key", "auth_secret_key", mode="before")
    @classmethod
    def blank_secret_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("hf_token", mode="before")
    @classmethod
    def blank_hf_token_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator(
        "hf_default_model",
        "hf_requirements_model",
        "hf_planner_model",
        "hf_programmer_model",
        "hf_reviewer_model",
        "hf_validator_model",
        mode="before",
    )
    @classmethod
    def blank_model_id_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    def generation_model_for(self, role: str) -> str | None:
        configured_model = {
            "requirements": self.hf_requirements_model,
            "planner": self.hf_planner_model,
            "programmer": self.hf_programmer_model,
            "reviewer": self.hf_reviewer_model,
            "validator": self.hf_validator_model,
        }.get(role)
        return configured_model or self.hf_default_model

    def signing_secret(self) -> str:
        if self.auth_secret_key:
            secret = self.auth_secret_key.get_secret_value()
            if len(secret.encode("utf-8")) < 32:
                raise RuntimeError("AUTH_SECRET_KEY must contain at least 32 bytes.")
            return secret
        if self.app_env == "production":
            raise RuntimeError("AUTH_SECRET_KEY must be configured in production.")
        if not self._development_secret:
            self._development_secret = secrets.token_urlsafe(48)
        return self._development_secret


@lru_cache
def get_settings() -> Settings:
    return Settings()