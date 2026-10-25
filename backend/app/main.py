"""Green Campus Sustainability Auditor — FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging
from backend.app.database.session import engine
from backend.app.database.init_db import init_db
from backend.app.api import router as api_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Green Campus Sustainability Auditor...")
    init_db()

    # Ensure uploads dir exists (use /tmp/uploads on Render, local path elsewhere)
    uploads_dir = Path(settings.UPLOAD_DIR)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Logs dir — /tmp/logs on Render, ./logs locally
    logs_dir = Path("logs")
    try:
        logs_dir.mkdir(exist_ok=True)
    except PermissionError:
        logs_dir = Path("/tmp/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic AI-Powered Green Campus Sustainability Auditor and Action Planner",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS — uses allowed_origins from config (supports localhost + Render URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api")

# Serve uploaded files (read-only static)
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }

