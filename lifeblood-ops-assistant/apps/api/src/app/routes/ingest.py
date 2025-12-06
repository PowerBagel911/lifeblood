"""Ingest endpoint for adding documents to the knowledge base."""

import logging
from fastapi import APIRouter, HTTPException, Request
from langchain_core.documents import Document

from ..core.schemas import IngestResponse
from ..core.config import settings
from ..utils.file_loaders import load_documents_from_directory
from ..utils.chunking import chunk_documents
from ..services.langchain_factory import build_lc_embeddings, build_lc_vectorstore

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
        
        # Step 3: Build LangChain components
        logger.debug("Building LangChain embeddings and vectorstore")
        lc_embeddings = build_lc_embeddings(settings)
        lc_vectorstore = build_lc_vectorstore(settings, lc_embeddings)
        
        # Step 4: Convert chunks to LangChain Documents
        logger.debug("Converting chunks to LangChain Documents")
        lc_documents = []
        for chunk in chunks:
            # Create metadata dictionary with all available chunk info
            metadata = {
                "doc_id": chunk.get('doc_id', 'unknown'),
                "chunk_id": chunk.get('chunk_id', 'unknown'),
                "title": chunk.get('title', ''),
                "start": chunk.get('start', 0),
                "end": chunk.get('end', 0)
            }
            
            # Create LangChain Document
            lc_doc = Document(
                page_content=chunk['text'],
                metadata=metadata
            )
            lc_documents.append(lc_doc)
        
        logger.debug(f"Converted {len(lc_documents)} chunks to LangChain Documents")
        
        # Step 5: Add documents to LangChain vectorstore
        logger.debug("Adding documents to LangChain Chroma vectorstore")
        lc_vectorstore.add_documents(lc_documents)
        
        logger.info(f"Successfully indexed {len(lc_documents)} documents into LangChain vectorstore")
        
        # Return success response
        return IngestResponse(
            indexed_docs=len(documents),
            indexed_chunks=len(lc_documents),
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
