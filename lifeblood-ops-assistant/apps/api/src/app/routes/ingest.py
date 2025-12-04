"""Ingest endpoint for adding documents to the knowledge base."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/ingest")
async def ingest_document():
    """Ingest a document into the knowledge base."""
    # Placeholder implementation
    raise HTTPException(
        status_code=501,
        detail="Ingest endpoint not yet implemented"
    )


@router.get("/ingest")
async def get_ingest_info():
    """Get information about the ingest endpoint."""
    # Placeholder implementation
    raise HTTPException(
        status_code=501,
        detail="Ingest info endpoint not yet implemented"
    )
