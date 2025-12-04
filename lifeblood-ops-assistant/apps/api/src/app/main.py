"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.config import settings
from .core.logging import setup_logging, setup_middleware
from .routes import ask, ingest

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting lifeblood-ops-assistant API")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Embed Provider: {settings.EMBED_PROVIDER}")
    
    # Validate API key configuration
    try:
        settings.validate_gemini_api_keys()
        logger.info("API key validation passed")
    except ValueError as e:
        logger.error(f"Startup validation failed: {e}")
        raise e
    
    yield
    
    # Shutdown
    logger.info("Shutting down lifeblood-ops-assistant API")


# Create FastAPI application
app = FastAPI(
    title="Lifeblood Ops Assistant API",
    description="AI-powered operations assistant API",
    version="0.1.0",
    lifespan=lifespan
)

# Set up middleware
setup_middleware(app)

# Include routers
app.include_router(ask.router, tags=["ask"])
app.include_router(ingest.router, tags=["ingest"])


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Lifeblood Ops Assistant API",
        "version": "0.1.0",
        "status": "running"
    }
