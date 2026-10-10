import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from brain.api.generated_files_api import router as generated_files_router
from brain.api.projects_api import router as projects_router
from brain.api.tasks_api import router as tasks_router
from brain.api.auth_api import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from brain.core.settings import get_settings
from brain.database.session import engine, Base
from brain.models.project import DeveloperTask, Project, ProjectChunk, TaskAttachment, TaskChange
from brain.models.generation import FileGeneration, GeneratedArtifact
from brain.models.user import User
from brain.services.generation_worker import run_generation_worker

settings = get_settings()
if settings.app_env == "production":
    settings.signing_secret()
    if settings.database_url.startswith("sqlite"):
        raise RuntimeError("Production requires a configured server database URL.")
settings.projects_root.mkdir(parents=True, exist_ok=True)
settings.uploads_root.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker = asyncio.create_task(run_generation_worker())
    try:
        yield
    finally:
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Multi-Agent Software Developer",
    description="Authenticated multi-agent file generation and project-aware coding assistance.",
    version="1.0.0",
    lifespan=lifespan,
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api")
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(generated_files_router)