"""Vector store abstraction and ChromaDB implementation for document retrieval."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any

import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError

from ..core.config import settings

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract interface for vector storage and retrieval."""
    
    @abstractmethod
    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """
        Insert or update chunks with their embeddings.
        
        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors corresponding to chunks
        """
        pass
    
    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar chunks.
        
        Args:
            query_embedding: Query vector to search for
            top_k: Number of top results to return
            
        Returns:
            List of similar chunks with metadata and scores
        """
        pass


class ChromaVectorStore(VectorStore):
    """
    ChromaDB implementation of vector store.
    
    Provides persistent storage with metadata support for document chunks.
    """
    
    def __init__(self, collection_name: str = "lifeblood_docs", persist_dir: str = None):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_dir: Directory for persistent storage (defaults to config setting)
        """
        self.collection_name = collection_name
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        
        # Ensure persist directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection (reset if dimension mismatch)
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing ChromaDB collection '{collection_name}'")
        except NotFoundError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Lifeblood operations document chunks"}
            )
            logger.info(f"Created new ChromaDB collection '{collection_name}'")
        
        logger.info(f"ChromaVectorStore initialized with persist_dir: {self.persist_dir}")
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """
        Insert or update chunks with their embeddings in ChromaDB.
        
        Args:
            chunks: List of chunk dictionaries with doc_id, chunk_id, text, title, etc.
            embeddings: List of embedding vectors corresponding to chunks
        """
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings provided for upsert")
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks count ({len(chunks)}) must match embeddings count ({len(embeddings)})")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for chunk, embedding in zip(chunks, embeddings):
            # Use chunk_id as the unique identifier
            chunk_id = chunk.get('chunk_id')
            if not chunk_id:
                raise ValueError(f"Chunk missing required 'chunk_id' field: {chunk}")
            
            ids.append(chunk_id)
            documents.append(chunk.get('text', ''))
            
            # Store relevant metadata (ChromaDB will automatically filter out None values)
            metadata = {
                'doc_id': chunk.get('doc_id'),
                'title': chunk.get('title'),
                'start': chunk.get('start'),
                'end': chunk.get('end')
            }
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            metadatas.append(metadata)
        
        try:
            # Upsert to ChromaDB (will update if exists, insert if new)
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully upserted {len(chunks)} chunks to ChromaDB")
            
        except Exception as e:
            # Check if it's a dimension mismatch error
            if "dimension" in str(e).lower():
                logger.warning(f"Embedding dimension mismatch detected: {e}")
                logger.info("Resetting collection for new embedding dimension...")
                
                # Delete and recreate collection with new dimension
                self.client.delete_collection(name=self.collection_name)
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Lifeblood operations document chunks"}
                )
                logger.info(f"Recreated collection '{self.collection_name}'")
                
                # Retry the upsert
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                
                logger.info(f"Successfully upserted {len(chunks)} chunks to new ChromaDB collection")
            else:
                # Re-raise if it's not a dimension error
                raise
            
        except Exception as e:
            logger.error(f"Error upserting chunks to ChromaDB: {e}")
            raise
    
    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query ChromaDB for similar chunks.
        
        Args:
            query_embedding: Query vector to search for
            top_k: Number of top results to return
            
        Returns:
            List of similar chunks with metadata and similarity scores
        """
        if not query_embedding:
            logger.warning("Empty query embedding provided")
            return []
        
        # Check if collection has any documents
        try:
            collection_count = self.collection.count()
            logger.debug(f"Collection '{self.collection_name}' has {collection_count} documents")
            if collection_count == 0:
                logger.warning("Collection is empty - no documents to search")
                return []
        except Exception as e:
            logger.warning(f"Could not get collection count: {e}")
        
        try:
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            logger.debug(f"ChromaDB raw results: {results}")
            
            # ChromaDB returns nested lists even for single query
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0] 
            distances = results.get('distances', [[]])[0]
            ids = results.get('ids', [[]])[0]
            
            logger.debug(f"Extracted: {len(documents)} documents, {len(metadatas)} metadatas, {len(distances)} distances, {len(ids)} ids")
            
            # Convert to our expected format
            query_results = []
            for i, (text, metadata, distance, chunk_id) in enumerate(zip(documents, metadatas, distances, ids)):
                # Convert distance to similarity score (ChromaDB uses cosine distance)
                # For cosine distance: similarity = 1 - distance, clamped to [0, 1]
                score = max(0.0, min(1.0, 1.0 - distance))
                
                result = {
                    'doc_id': metadata.get('doc_id', 'unknown') if metadata else 'unknown',
                    'title': metadata.get('title') if metadata else None,
                    'chunk_id': chunk_id,
                    'text': text,  # In ChromaDB, 'documents' contains the actual text
                    'score': score,
                    'start': metadata.get('start') if metadata else None,
                    'end': metadata.get('end') if metadata else None
                }
                query_results.append(result)
            
            logger.debug(f"Query returned {len(query_results)} results")
            return query_results
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            raise
    
    def count(self) -> int:
        """Get the number of chunks in the vector store."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting chunks in ChromaDB: {e}")
            return 0
    
    def reset(self) -> None:
        """Reset the collection (delete all data)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Lifeblood operations document chunks"}
            )
            logger.info(f"Reset ChromaDB collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error resetting ChromaDB collection: {e}")
            raise
    
    def close(self) -> None:
        """Close the ChromaDB client connections."""
        try:
            # ChromaDB doesn't have an explicit close method, but we can reset references
            self.collection = None
            # Force garbage collection to help release file handles
            import gc
            gc.collect()
            logger.debug("ChromaDB connections closed")
        except Exception as e:
            logger.warning(f"Error closing ChromaDB connections: {e}")


def get_vector_store(persist_dir: str = None) -> VectorStore:
    """
    Factory function to get the configured vector store.
    
    Args:
        persist_dir: Optional custom persist directory
        
    Returns:
        Configured vector store instance
    """
    return ChromaVectorStore(persist_dir=persist_dir)
