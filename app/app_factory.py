"""
FastAPI application factory and router inclusion.
"""
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.retrieve import router as rentals_router  # Fixed import
from app.api.routes.health_check import router as health_router  # Fixed import
from app.scheduler.scheduler import start_scheduler, stop_scheduler  # Fixed import
from app.db.manage_db import init_db, engine
from app.core.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    await init_db()  # Initialize database tables

    yield  # Application runs here

    await engine.dispose()  # Close database connections


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="House Scraper API",
        description="Telegram scraper with LLM parsing and vector search",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Include routers - Fixed
    app.include_router(health_router, prefix="/api")
    app.include_router(rentals_router, prefix="/api")

    return app
