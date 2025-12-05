"""Embedding providers for text vectorization."""

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List

try:
    import google.generativeai as genai
except ImportError:
    try:
        from google import genai
    except ImportError:
        genai = None

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsProvider(ABC):
    """Abstract interface for text embedding providers."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts into vectors.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors, one for each input text
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text into a vector.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector for the input text
        """
        pass


class FakeEmbeddingsProvider(EmbeddingsProvider):
    """
    Fake embeddings provider for testing and offline operation.
    
    Generates deterministic embeddings based on text content hash.
    Safe for offline use and produces consistent results.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize fake embeddings provider.
        
        Args:
            embedding_dim: Dimension of embedding vectors to generate
        """
        self.embedding_dim = embedding_dim
        logger.info(f"Initialized FakeEmbeddingsProvider with dimension {embedding_dim}")
    
    def _text_to_embedding(self, text: str) -> List[float]:
        """
        Convert text to deterministic embedding vector.
        
        Args:
            text: Input text string
            
        Returns:
            Deterministic embedding vector
        """
        # Create deterministic hash from text
        text_hash = hashlib.sha256(text.encode('utf-8')).digest()
        
        # Generate embedding values from hash
        embedding = []
        for i in range(self.embedding_dim):
            # Use byte at position (i % len(hash)) to generate float
            byte_val = text_hash[i % len(text_hash)]
            # Normalize to [-1, 1] range
            normalized_val = (byte_val / 255.0) * 2.0 - 1.0
            embedding.append(normalized_val)
        
        return embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts into vectors."""
        if not texts:
            return []
        
        logger.debug(f"Embedding {len(texts)} texts with FakeEmbeddingsProvider")
        embeddings = [self._text_to_embedding(text) for text in texts]
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text into a vector."""
        logger.debug(f"Embedding query text with FakeEmbeddingsProvider")
        return self._text_to_embedding(text)


class GeminiEmbeddingsProvider(EmbeddingsProvider):
    """
    Gemini embeddings provider using Google GenAI SDK.
    
    Requires valid GEMINI_API_KEY or GOOGLE_API_KEY in environment.
    """
    
    def __init__(self):
        """Initialize Gemini embeddings provider."""
        # Use the API key from settings
        api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY or GOOGLE_API_KEY."
            )
        
        # Configure the client
        genai.configure(api_key=api_key)
        self.client = genai.Client()
        self.model_name = settings.GEMINI_EMBED_MODEL
        
        logger.info(f"Initialized GeminiEmbeddingsProvider with model {self.model_name}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts using Gemini API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors from Gemini API
        """
        if not texts:
            return []
        
        logger.debug(f"Embedding {len(texts)} texts with Gemini API")
        
        try:
            # Call Gemini embedding API
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=texts
            )
            
            # Extract embedding vectors
            embeddings = [emb.values for emb in result.embeddings]
            
            logger.debug(f"Successfully embedded {len(embeddings)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error embedding texts with Gemini: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text using Gemini API.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector from Gemini API
        """
        logger.debug("Embedding query text with Gemini API")
        
        try:
            # Call Gemini embedding API for single text
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=[text]
            )
            
            # Extract first (and only) embedding vector
            if result.embeddings:
                embedding = result.embeddings[0].values
                logger.debug("Successfully embedded query text")
                return embedding
            else:
                raise ValueError("No embedding returned from Gemini API")
                
        except Exception as e:
            logger.error(f"Error embedding query with Gemini: {e}")
            raise


def get_embeddings_provider() -> EmbeddingsProvider:
    """
    Factory function to get the configured embeddings provider.
    
    Returns:
        Configured embeddings provider based on settings
    """
    provider_name = settings.EMBED_PROVIDER.lower()
    
    if provider_name == "gemini":
        return GeminiEmbeddingsProvider()
    elif provider_name == "fake":
        return FakeEmbeddingsProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {provider_name}")
