"""Ask endpoint for querying the knowledge base."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/ask")
async def ask_question():
    """Ask a question to the knowledge base."""
    # Placeholder implementation
    raise HTTPException(
        status_code=501,
        detail="Ask endpoint not yet implemented"
    )


@router.get("/ask")
async def get_ask_info():
    """Get information about the ask endpoint."""
    # Placeholder implementation  
    raise HTTPException(
        status_code=501,
        detail="Ask info endpoint not yet implemented"
    )
