"""Structured logging with trace ID middleware."""

import logging
import uuid
from typing import Callable
from contextvars import ContextVar

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


# Context variable to store trace ID for the current request
trace_id_context: ContextVar[str] = ContextVar("trace_id", default="")


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and attach trace IDs to requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Generate trace ID and attach to request context and response headers."""
        # Generate a new trace ID for this request
        trace_id = str(uuid.uuid4())
        
        # Set trace ID in context for logging
        trace_id_context.set(trace_id)
        
        # Add trace ID to request state for access in route handlers
        request.state.trace_id = trace_id
        
        # Process the request
        response = await call_next(request)
        
        # Add trace ID to response headers
        response.headers["X-Trace-Id"] = trace_id
        
        return response


class TraceIDFormatter(logging.Formatter):
    """Custom formatter that includes trace ID in log messages."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with trace ID if available."""
        # Get trace ID from context
        trace_id = trace_id_context.get("")
        
        # Add trace_id to the record
        record.trace_id = trace_id if trace_id else "no-trace"
        
        return super().format(record)


def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Create formatter with trace ID
    formatter = TraceIDFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Configure uvicorn loggers to use our formatter
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(logger_name)
        for handler in uvicorn_logger.handlers:
            handler.setFormatter(formatter)


def get_trace_id() -> str:
    """Get the current request's trace ID."""
    return trace_id_context.get("")


def setup_middleware(app: FastAPI) -> None:
    """Add trace ID middleware to the FastAPI app."""
    app.add_middleware(TraceIDMiddleware)
