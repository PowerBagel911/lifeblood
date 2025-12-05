"""Ingest endpoint for adding documents to the knowledge base."""

import logging
from fastapi import APIRouter, HTTPException, Request

from ..core.schemas import IngestResponse
from ..utils.file_loaders import load_documents_from_directory
from ..utils.chunking import chunk_documents
from ..services.embeddings import get_embeddings_provider
from ..services.retrieval import get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: Request):
    """
    Ingest documents from data/docs into the knowledge base.
    
    Local prototype only; add auth in real environment.
    """
    # Get trace ID from request state (set by middleware)
    trace_id = getattr(request.state, 'trace_id', 'unknown')
    
    logger.info(f"Starting document ingestion [trace_id: {trace_id}]")
    
    try:
        # Step 1: Load documents from data/docs
        logger.debug("Loading documents from data/docs directory")
        documents = load_documents_from_directory("data/docs")
        
        if not documents:
            logger.warning("No documents found in data/docs directory")
            return IngestResponse(
                indexed_docs=0,
                indexed_chunks=0,
                trace_id=trace_id
            )
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Step 2: Chunk the documents
        logger.debug("Chunking documents")
        chunks = chunk_documents(documents, chunk_size_chars=2000, overlap_chars=200)
        
        if not chunks:
            logger.warning("No chunks generated from documents")
            return IngestResponse(
                indexed_docs=len(documents),
                indexed_chunks=0,
                trace_id=trace_id
            )
        
        logger.info(f"Generated {len(chunks)} chunks from {len(documents)} documents")
        
        # Step 3: Generate embeddings (use configured provider)
        logger.debug("Generating embeddings for chunks")
        embeddings_provider = get_embeddings_provider()
        
        # Extract text from chunks for embedding
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = embeddings_provider.embed_texts(chunk_texts)
        
        if len(embeddings) != len(chunks):
            raise ValueError(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
        
        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        
        # Step 4: Upsert into vector store
        logger.debug("Upserting chunks into vector store")
        vector_store = get_vector_store()
        vector_store.upsert_chunks(chunks, embeddings)
        
        # Verify indexing by counting
        final_count = vector_store.count() if hasattr(vector_store, 'count') else len(chunks)
        logger.info(f"Successfully indexed {len(chunks)} chunks into vector store (total: {final_count})")
        
        # Return success response
        return IngestResponse(
            indexed_docs=len(documents),
            indexed_chunks=len(chunks),
            trace_id=trace_id
        )
        
    except Exception as e:
        logger.error(f"Error during document ingestion: {e} [trace_id: {trace_id}]")
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Document ingestion failed: {str(e)}",
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
