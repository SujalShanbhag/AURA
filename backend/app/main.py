from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.container import (
    initialize_ai,
    shutdown_ai,
    get_ai_container,
)

from app.api.routes import router

from app.core.database import (
    database_health_check,
    close_database,
)

logger = logging.getLogger("aura.main")


# ============================================================
# Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Startup
    try:
        await initialize_ai()
        logger.info("AURA AI initialized.")
    except Exception:
        logger.exception("AI initialization failed.")
        raise

    yield

    # Shutdown
    try:
        await shutdown_ai()
        logger.info("AI shutdown completed.")
    except Exception:
        logger.exception("AI shutdown failed.")

    try:
        await close_database()
        logger.info("Database closed.")
    except Exception:
        logger.exception("Database shutdown failed.")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="AURA API",
    version="1.0.0",
    description="Next Generation AI Companion Backend",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API Routes
# ============================================================

# app.api.routes already includes all v1 routers.
app.include_router(router)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "app": "AURA",
        "status": "running",
        "version": "1.0.0",
    }


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health", tags=["System"])
async def health():
    database_status = False
    ai_status = False

    try:
        database_status = await database_health_check()
    except Exception:
        logger.exception("Database health check failed.")

    try:
        container = get_ai_container()
        ai_status = await container.orchestrator.health_check()
    except Exception:
        logger.exception("AI health check failed.")

    return {
        "status": "healthy" if database_status and ai_status else "degraded",
        "services": {
            "database": database_status,
            "ai": ai_status,
        },
    }