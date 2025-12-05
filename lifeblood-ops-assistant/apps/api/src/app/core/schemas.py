"""Pydantic models for API request/response schemas."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request schema for asking questions."""
    
    question: str = Field(..., description="The question to ask")
    mode: Literal["general", "checklist", "plain_english"] = Field(
        default="general",
        description="The response mode for the question"
    )


class Citation(BaseModel):
    """Citation information for sources."""
    
    doc_id: str = Field(..., description="Document identifier")
    title: Optional[str] = Field(None, description="Document title")
    chunk_id: Optional[str] = Field(None, description="Chunk identifier within the document")
    snippet: str = Field(..., description="Relevant text snippet from the source")
    score: float = Field(..., description="Relevance score for this citation", ge=0.0, le=1.0)


class AskResponse(BaseModel):
    """Response schema for question answers."""
    
    answer: str = Field(..., description="The generated answer to the question")
    citations: List[Citation] = Field(
        default_factory=list, 
        description="List of source citations supporting the answer"
    )
    trace_id: str = Field(..., description="Request trace identifier")


class IngestResponse(BaseModel):
    """Response schema for document ingestion."""
    
    indexed_docs: int = Field(..., description="Number of documents indexed", ge=0)
    indexed_chunks: int = Field(..., description="Number of chunks indexed", ge=0)
    trace_id: str = Field(..., description="Request trace identifier")
