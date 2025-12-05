"""Ingest endpoint for adding documents to the knowledge base."""

from fastapi import APIRouter, HTTPException, Request

from ..core.schemas import IngestResponse

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: Request):
    """Ingest a document into the knowledge base."""
    # Get trace ID from request state (set by middleware)
    trace_id = getattr(request.state, 'trace_id', 'unknown')
    
    # Placeholder implementation - return 501 with proper schema structure
    raise HTTPException(
        status_code=501,
        detail={
            "message": "Ingest endpoint not yet implemented",
            "trace_id": trace_id
        }
    )


@router.get("/ingest")
async def get_ingest_info():
    """Get information about the ingest endpoint."""
    # Placeholder implementation
    raise HTTPException(
        status_code=501,
        detail="Ingest info endpoint not yet implemented"
    )
