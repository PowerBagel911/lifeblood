"""RAG (Retrieval-Augmented Generation) pipeline implementation."""

import logging
from typing import Dict, List, Any

from .embeddings import EmbeddingsProvider
from .retrieval import VectorStore
from .llm_client import LLMClient
from .prompts import build_rag_prompt

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG pipeline that orchestrates query embedding, document retrieval, 
    prompt building, and LLM generation.
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        embeddings_provider: EmbeddingsProvider,
        llm_client: LLMClient
    ):
        """
        Initialize RAG pipeline with injected dependencies.
        
        Args:
            vector_store: Vector store for document retrieval
            embeddings_provider: Provider for text embeddings
            llm_client: LLM client for text generation
        """
        self.vector_store = vector_store
        self.embeddings_provider = embeddings_provider
        self.llm_client = llm_client
        
        logger.info("RAG pipeline initialized with injected dependencies")
    
    def ask(self, question: str, mode: str = "general", top_k: int = 5) -> Dict[str, Any]:
        """
        Process a question through the full RAG pipeline.
        
        Args:
            question: User question to answer
            mode: Response mode ("general", "checklist", "plain_english")
            top_k: Number of top chunks to retrieve
            
        Returns:
            Dictionary with 'answer' and 'citations' keys
        """
        try:
            logger.info(f"Processing RAG query: '{question}' (mode={mode}, top_k={top_k})")
            
            # Validate input
            if not question or not question.strip():
                return {
                    "answer": "Please provide a specific question for me to answer.",
                    "citations": []
                }
            
            # Step 1: Embed the query
            logger.debug("Embedding query")
            try:
                query_embedding = self.embeddings_provider.embed_query(question.strip())
            except Exception as e:
                logger.error(f"Error embedding query: {e}")
                return {
                    "answer": "I encountered an error processing your question. Please try again.",
                    "citations": []
                }
            
            # Step 2: Retrieve relevant chunks
            logger.debug(f"Retrieving top {top_k} chunks")
            try:
                retrieved_chunks = self.vector_store.query(query_embedding, top_k=top_k)
            except Exception as e:
                logger.error(f"Error retrieving chunks: {e}")
                return {
                    "answer": "I encountered an error searching for relevant information. Please try again.",
                    "citations": []
                }
            
            # Step 3: Check if we have meaningful results
            meaningful_chunks = self._filter_meaningful_chunks(retrieved_chunks)
            
            if not meaningful_chunks:
                logger.info("No meaningful chunks retrieved, returning fallback")
                return {
                    "answer": "I don't have enough information in the docs to answer that.",
                    "citations": []
                }
            
            # Step 4: Build prompt with retrieved chunks
            logger.debug(f"Building prompt with {len(meaningful_chunks)} chunks")
            try:
                prompt = build_rag_prompt(question.strip(), meaningful_chunks, mode)
            except Exception as e:
                logger.error(f"Error building prompt: {e}")
                return {
                    "answer": "I encountered an error preparing the response. Please try again.",
                    "citations": []
                }
            
            # Step 5: Generate answer using LLM
            logger.debug("Generating LLM response")
            try:
                llm_response = self.llm_client.generate(prompt)
            except Exception as e:
                logger.error(f"Error generating LLM response: {e}")
                return {
                    "answer": "I encountered an error generating the response. Please try again.",
                    "citations": []
                }
            
            # Step 6: Build citations from meaningful chunks
            citations = self._build_citations(meaningful_chunks)
            
            result = {
                "answer": llm_response.strip() if llm_response else "I was unable to generate a response.",
                "citations": citations
            }
            
            logger.info(f"RAG pipeline completed successfully with {len(citations)} citations")
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in RAG pipeline: {e}")
            return {
                "answer": "I encountered an unexpected error. Please try again.",
                "citations": []
            }
    
    def _filter_meaningful_chunks(self, chunks: List[Dict[str, Any]], min_score: float = 0.01) -> List[Dict[str, Any]]:
        """
        Filter chunks to only include meaningful results.
        
        Args:
            chunks: Retrieved chunks with scores
            min_score: Minimum similarity score threshold
            
        Returns:
            List of chunks that meet meaningfulness criteria
        """
        if not chunks:
            return []
        
        meaningful_chunks = []
        
        for chunk in chunks:
            # Check if chunk has required fields
            if not isinstance(chunk, dict):
                continue
                
            text = chunk.get('text', '').strip()
            if not text:
                continue
            
            # Check similarity score
            score = chunk.get('score', 0.0)
            if score < min_score:
                logger.debug(f"Filtering out chunk with low score: {score} (min: {min_score})")
                continue
            
            # Check text length (too short texts are usually not helpful)
            if len(text) < 20:
                logger.debug("Filtering out chunk with very short text")
                continue
            
            meaningful_chunks.append(chunk)
        
        logger.debug(f"Filtered {len(meaningful_chunks)} meaningful chunks from {len(chunks)} total")
        return meaningful_chunks
    
    def _build_citations(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build citation objects from retrieved chunks.
        
        Args:
            chunks: List of meaningful chunks
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        for chunk in chunks:
            citation = {
                "doc_id": chunk.get('doc_id', 'unknown'),
                "title": chunk.get('title'),
                "chunk_id": chunk.get('chunk_id'),
                "snippet": self._create_snippet(chunk.get('text', '')),
                "score": chunk.get('score', 0.0)
            }
            citations.append(citation)
        
        return citations
    
    def _create_snippet(self, text: str, max_length: int = 200) -> str:
        """
        Create a concise snippet from chunk text.
        
        Args:
            text: Full chunk text
            max_length: Maximum snippet length
            
        Returns:
            Truncated snippet with ellipsis if needed
        """
        text = text.strip()
        if len(text) <= max_length:
            return text
        
        # Try to cut at a sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        # If we find a period, cut there
        if last_period > max_length * 0.7:  # Don't cut too early
            return text[:last_period + 1]
        
        # Otherwise cut at last word boundary
        if last_space > max_length * 0.7:
            return text[:last_space] + "..."
        
        # Fallback: hard cut with ellipsis
        return text[:max_length - 3] + "..."
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get status information about the pipeline components.
        
        Returns:
            Dictionary with component status information
        """
        status = {
            "vector_store": {
                "type": type(self.vector_store).__name__,
                "available": self.vector_store is not None
            },
            "embeddings_provider": {
                "type": type(self.embeddings_provider).__name__,
                "available": self.embeddings_provider is not None
            },
            "llm_client": {
                "type": type(self.llm_client).__name__,
                "available": self.llm_client is not None
            }
        }
        
        # Try to get vector store count if available
        try:
            if hasattr(self.vector_store, 'count'):
                status["vector_store"]["document_count"] = self.vector_store.count()
        except Exception:
            pass
        
        return status
