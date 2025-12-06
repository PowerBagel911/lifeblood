"""RAG (Retrieval-Augmented Generation) pipeline implementation."""

import logging
from typing import Dict, List, Any, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .prompts import build_rag_prompt
from ..core.config import Settings

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG pipeline that orchestrates document retrieval, prompt building, 
    and LLM generation using LangChain components.
    """
    
    def __init__(
        self,
        vectorstore: Chroma,
        embeddings: GoogleGenerativeAIEmbeddings,
        llm: ChatGoogleGenerativeAI
    ):
        """
        Initialize RAG pipeline with LangChain components.
        
        Args:
            vectorstore: LangChain Chroma vector store
            embeddings: LangChain Google GenerativeAI embeddings
            llm: LangChain Google GenerativeAI chat model
        """
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.llm = llm
        
        logger.info("RAG pipeline initialized with LangChain components")
    
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
            
            # Step 1: Retrieve documents with scores using LangChain
            logger.debug(f"Retrieving top {top_k} documents with relevance scores")
            try:
                # Try similarity_search_with_relevance_scores first (preferred)
                if hasattr(self.vectorstore, 'similarity_search_with_relevance_scores'):
                    retrieved_docs_with_scores = self.vectorstore.similarity_search_with_relevance_scores(
                        question.strip(), k=top_k
                    )
                    logger.debug(f"Retrieved {len(retrieved_docs_with_scores)} documents with relevance scores")
                else:
                    # Fallback to similarity_search_with_score
                    retrieved_docs_with_scores = self.vectorstore.similarity_search_with_score(
                        question.strip(), k=top_k
                    )
                    logger.debug(f"Retrieved {len(retrieved_docs_with_scores)} documents with scores (fallback method)")
                
            except Exception as e:
                logger.error(f"Error retrieving documents: {e}")
                # Check if it's because no data is indexed yet
                if "does not exist" in str(e).lower() or "not found" in str(e).lower() or "empty" in str(e).lower():
                    logger.info("No data indexed yet, returning fallback")
                    return {
                        "answer": "I don't have enough information in the docs to answer that. Please make sure documents have been ingested using the /ingest endpoint first.",
                        "citations": []
                    }
                return {
                    "answer": "I encountered an error searching for relevant information. Please try again.",
                    "citations": []
                }
            
            # Step 2: Convert LangChain Documents to citations
            logger.debug(f"Converting {len(retrieved_docs_with_scores)} LangChain documents to citations")
            citations = self._convert_langchain_docs_to_citations(retrieved_docs_with_scores)
            
            # Step 3: Filter meaningful results
            meaningful_citations = self._filter_meaningful_citations(citations)
            
            if not meaningful_citations:
                logger.info("No meaningful citations found, returning fallback")
                return {
                    "answer": "I don't have enough information in the docs to answer that.",
                    "citations": []
                }
            
            # Step 4: Convert citations to chunks format for existing prompt builder
            logger.debug(f"Building prompt with {len(meaningful_citations)} citations")
            chunks_for_prompt = self._citations_to_chunks(meaningful_citations)
            
            try:
                prompt = build_rag_prompt(question.strip(), chunks_for_prompt, mode)
                logger.debug(f"Built prompt length: {len(prompt)} characters")
            except Exception as e:
                logger.error(f"Error building prompt: {e}")
                return {
                    "answer": "I encountered an error preparing the response. Please try again.",
                    "citations": []
                }
            
            # Step 5: Generate answer using LangChain LLM
            logger.debug("Generating LLM response with LangChain")
            try:
                response = self.llm.invoke(prompt)
                
                # Extract text from LangChain response
                if hasattr(response, 'text') and response.text:
                    llm_response = response.text
                elif hasattr(response, 'content') and response.content:
                    llm_response = response.content
                else:
                    llm_response = str(response)
                    
                logger.debug("Successfully generated response with LangChain LLM")
                
            except Exception as e:
                logger.error(f"Error generating LLM response: {e}")
                return {
                    "answer": "I encountered an error generating the response. Please try again.",
                    "citations": []
                }
            
            # Step 6: Return final result
            result = {
                "answer": llm_response.strip() if llm_response else "I was unable to generate a response.",
                "citations": meaningful_citations
            }
            
            logger.info(f"RAG pipeline completed successfully with {len(meaningful_citations)} citations")
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in RAG pipeline: {e}")
            return {
                "answer": "I encountered an unexpected error. Please try again.",
                "citations": []
            }
    
    def _convert_langchain_docs_to_citations(self, docs_with_scores: List[Tuple[Document, float]]) -> List[Dict[str, Any]]:
        """
        Convert LangChain Documents with scores to Citation format.
        
        Args:
            docs_with_scores: List of tuples (Document, score) from LangChain similarity search
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        for doc, score in docs_with_scores:
            citation = {
                "doc_id": doc.metadata.get('doc_id', 'unknown'),
                "title": doc.metadata.get('title'),
                "chunk_id": doc.metadata.get('chunk_id'),
                "snippet": self._create_snippet(doc.page_content),
                "score": score
            }
            citations.append(citation)
        
        logger.debug(f"Converted {len(citations)} LangChain documents to citations")
        return citations

    def _filter_meaningful_citations(self, citations: List[Dict[str, Any]], min_score: float = 0.01) -> List[Dict[str, Any]]:
        """
        Filter citations to only include meaningful results.
        
        Args:
            citations: List of citations with scores
            min_score: Minimum relevance score threshold
            
        Returns:
            List of citations that meet meaningfulness criteria
        """
        if not citations:
            return []
        
        meaningful_citations = []
        
        for citation in citations:
            # Check if citation has required fields
            if not isinstance(citation, dict):
                continue
                
            snippet = citation.get('snippet', '').strip()
            if not snippet:
                continue
            
            # Check relevance score
            score = citation.get('score', 0.0)
            if score < min_score:
                logger.debug(f"Filtering out citation with low score: {score} (min: {min_score})")
                continue
            
            # Check snippet length (too short snippets are usually not helpful)
            if len(snippet) < 20:
                logger.debug("Filtering out citation with very short snippet")
                continue
            
            meaningful_citations.append(citation)
        
        logger.debug(f"Filtered {len(meaningful_citations)} meaningful citations from {len(citations)} total")
        return meaningful_citations

    def _citations_to_chunks(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert citations back to chunks format for prompt building.
        
        Args:
            citations: List of citation dictionaries
            
        Returns:
            List of chunk dictionaries compatible with build_rag_prompt
        """
        chunks = []
        
        for citation in citations:
            chunk = {
                'doc_id': citation.get('doc_id', 'unknown'),
                'chunk_id': citation.get('chunk_id'),
                'title': citation.get('title'),
                'text': citation.get('snippet', ''),
                'start': citation.get('start'),
                'end': citation.get('end'),
                'score': citation.get('score', 0.0)
            }
            chunks.append(chunk)
        
        return chunks

    # Note: _filter_meaningful_chunks and _build_citations methods removed 
    # as they're replaced by _filter_meaningful_citations and _convert_langchain_docs_to_citations
    
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
        Get status information about the LangChain pipeline components.
        
        Returns:
            Dictionary with component status information
        """
        status = {
            "vectorstore": {
                "type": type(self.vectorstore).__name__,
                "available": self.vectorstore is not None,
                "collection_name": getattr(self.vectorstore, '_collection_name', 'unknown')
            },
            "embeddings": {
                "type": type(self.embeddings).__name__,
                "available": self.embeddings is not None,
                "model": getattr(self.embeddings, 'model', 'unknown')
            },
            "llm": {
                "type": type(self.llm).__name__,
                "available": self.llm is not None,
                "model": getattr(self.llm, 'model_name', 'unknown')
            }
        }
        
        # Try to get document count from vectorstore if available
        try:
            if hasattr(self.vectorstore, '_collection') and self.vectorstore._collection:
                collection = self.vectorstore._collection
                if hasattr(collection, 'count'):
                    status["vectorstore"]["document_count"] = collection.count()
        except Exception as e:
            logger.debug(f"Could not get document count: {e}")
        
        return status
