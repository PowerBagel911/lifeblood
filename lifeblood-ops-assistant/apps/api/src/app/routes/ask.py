"""Ask endpoint for querying the knowledge base."""

import logging
from fastapi import APIRouter, HTTPException, Request

from ..core.schemas import AskRequest, AskResponse
from ..services.rag_pipeline import RAGPipeline
from ..services.embeddings import get_embeddings_provider
from ..services.retrieval import get_vector_store
from ..services.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: Request, ask_request: AskRequest):
    """Ask a question to the knowledge base."""
    # Get trace ID from request state (set by middleware)
    trace_id = getattr(request.state, 'trace_id', 'unknown')
    
    logger.info(f"Processing question: '{ask_request.question}' [trace_id: {trace_id}]")
    
    try:
        # Step 1: Validate question input
        if not ask_request.question or not ask_request.question.strip():
            logger.warning(f"Empty question received [trace_id: {trace_id}]")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Question cannot be empty or whitespace only",
                    "trace_id": trace_id
                }
            )
        
        # Step 2: Build dependencies from config
        logger.debug(f"Building RAG pipeline dependencies [trace_id: {trace_id}]")
        
        try:
            # Get vector store (Chroma)
            logger.debug(f"Getting vector store [trace_id: {trace_id}]")
            vector_store = get_vector_store(persist_dir=".chroma")
            
            # Get embeddings provider (Gemini or Fake based on config)
            logger.debug(f"Getting embeddings provider [trace_id: {trace_id}]")
            embeddings_provider = get_embeddings_provider()
            
            # Get LLM client (Gemini or Mock based on config)
            logger.debug(f"Getting LLM client [trace_id: {trace_id}]")
            llm_client = get_llm_client()
            
        except Exception as e:
            logger.error(f"Failed to build dependencies: {str(e)} [trace_id: {trace_id}]")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": f"Service configuration error: {str(e)}",
                    "trace_id": trace_id
                }
            )
        
        # Step 3: Initialize RAG pipeline with dependencies
        rag_pipeline = RAGPipeline(
            vector_store=vector_store,
            embeddings_provider=embeddings_provider,
            llm_client=llm_client
        )
        
        # Step 4: Call RAG pipeline
        logger.debug(f"Calling RAG pipeline with mode '{ask_request.mode}' [trace_id: {trace_id}]")
        
        result = rag_pipeline.ask(
            question=ask_request.question.strip(),
            mode=ask_request.mode,
            top_k=ask_request.top_k
        )
        
        # Step 5: Build and return response
        response = AskResponse(
            question=ask_request.question.strip(),
            answer=result["answer"],
            citations=result["citations"],
            mode=ask_request.mode,
            trace_id=trace_id
        )
        
        logger.info(f"Successfully processed question with {len(result['citations'])} citations [trace_id: {trace_id}]")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 validation error)
        raise
    except Exception as e:
        # Catch all other exceptions and return 500 with safe error message
        logger.error(f"Unexpected error processing question: {e} [trace_id: {trace_id}]")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An error occurred while processing your question. Please try again.",
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
