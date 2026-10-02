from fastapi import FastAPI
from brain.api.projects_api import router as projects_router
from brain.api.tasks_api import router as tasks_router
from brain.api.auth_api import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from brain.core.settings import get_settings
from brain.database.session import engine, Base
from brain.models.project import DeveloperTask, Project, ProjectChunk, TaskAttachment, TaskChange
from brain.models.user import User

settings = get_settings()
if settings.app_env == "production":
    settings.signing_secret()
    if settings.database_url.startswith("sqlite"):
        raise RuntimeError("Production requires a configured server database URL.")
settings.projects_root.mkdir(parents=True, exist_ok=True)
settings.uploads_root.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Multi-Agent Software Developer",
    description="Project-scoped coding assistant with retrieval and reviewed changes.",
    version="1.0.0",
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