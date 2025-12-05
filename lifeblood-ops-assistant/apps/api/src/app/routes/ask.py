"""Ask endpoint for querying the knowledge base."""

from fastapi import APIRouter, HTTPException, Request

from ..core.schemas import AskRequest, AskResponse

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: Request, ask_request: AskRequest):
    """Ask a question to the knowledge base."""
    # Get trace ID from request state (set by middleware)
    trace_id = getattr(request.state, 'trace_id', 'unknown')
    
    # Placeholder implementation - return 501 with proper schema structure
    raise HTTPException(
        status_code=501,
        detail={
            "message": "Ask endpoint not yet implemented",
            "question": ask_request.question,
            "mode": ask_request.mode,
            "trace_id": trace_id
        }
    )


@router.get("/ask")
async def get_ask_info():
    """Get information about the ask endpoint."""
    # Placeholder implementation  
    raise HTTPException(
        status_code=501,
        detail="Ask info endpoint not yet implemented"
    )
