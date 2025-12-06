"""Ask endpoint for querying the knowledge base."""

import logging
from fastapi import APIRouter, HTTPException, Request

from ..core.schemas import AskRequest, AskResponse
from ..core.config import settings
from ..services.rag_pipeline import RAGPipeline
from ..services.langchain_factory import build_lc_embeddings, build_lc_vectorstore, build_lc_llm

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
        
        # Step 2: Build LangChain components from config
        logger.debug(f"Building LangChain RAG pipeline components [trace_id: {trace_id}]")
        
        try:
            # Build LangChain embeddings
            logger.debug(f"Building LangChain embeddings [trace_id: {trace_id}]")
            lc_embeddings = build_lc_embeddings(settings)
            
            # Build LangChain vector store
            logger.debug(f"Building LangChain vector store [trace_id: {trace_id}]")
            lc_vectorstore = build_lc_vectorstore(settings, lc_embeddings)
            
            # Build LangChain LLM
            logger.debug(f"Building LangChain LLM [trace_id: {trace_id}]")
            lc_llm = build_lc_llm(settings)
            
        except Exception as e:
            logger.error(f"Failed to build LangChain components: {str(e)} [trace_id: {trace_id}]")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": f"LangChain configuration error: {str(e)}",
                    "trace_id": trace_id
                }
            )
        
        # Step 3: Initialize RAG pipeline with LangChain components
        rag_pipeline = RAGPipeline(
            vectorstore=lc_vectorstore,
            embeddings=lc_embeddings,
            llm=lc_llm
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
