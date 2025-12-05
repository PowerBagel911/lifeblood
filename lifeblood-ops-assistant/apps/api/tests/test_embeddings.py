"""Tests for embedding providers."""

import pytest
from app.services.embeddings import (
    EmbeddingsProvider, 
    FakeEmbeddingsProvider, 
    GeminiEmbeddingsProvider,
    get_embeddings_provider
)


class TestFakeEmbeddingsProvider:
    """Test cases for FakeEmbeddingsProvider."""
    
    def test_initialization_default_dimension(self):
        """Test default initialization creates correct dimension."""
        provider = FakeEmbeddingsProvider()
        assert provider.embedding_dim == 384
    
    def test_initialization_custom_dimension(self):
        """Test custom dimension initialization."""
        provider = FakeEmbeddingsProvider(embedding_dim=512)
        assert provider.embedding_dim == 512
    
    def test_embed_query_returns_correct_dimension(self):
        """Test embed_query returns vector of correct dimension."""
        provider = FakeEmbeddingsProvider(embedding_dim=100)
        
        embedding = provider.embed_query("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 100
        assert all(isinstance(val, float) for val in embedding)
    
    def test_embed_query_deterministic(self):
        """Test embed_query produces deterministic results."""
        provider = FakeEmbeddingsProvider()
        
        text = "This is a test query"
        embedding1 = provider.embed_query(text)
        embedding2 = provider.embed_query(text)
        
        assert embedding1 == embedding2
    
    def test_embed_query_different_texts_different_embeddings(self):
        """Test different texts produce different embeddings."""
        provider = FakeEmbeddingsProvider()
        
        embedding1 = provider.embed_query("First text")
        embedding2 = provider.embed_query("Second text")
        
        assert embedding1 != embedding2
    
    def test_embed_query_values_in_range(self):
        """Test embedding values are in expected range [-1, 1]."""
        provider = FakeEmbeddingsProvider()
        
        embedding = provider.embed_query("test")
        
        for value in embedding:
            assert -1.0 <= value <= 1.0
    
    def test_embed_texts_empty_list(self):
        """Test embed_texts with empty list returns empty list."""
        provider = FakeEmbeddingsProvider()
        
        embeddings = provider.embed_texts([])
        
        assert embeddings == []
    
    def test_embed_texts_single_text(self):
        """Test embed_texts with single text."""
        provider = FakeEmbeddingsProvider(embedding_dim=50)
        
        embeddings = provider.embed_texts(["single text"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 50
        assert all(isinstance(val, float) for val in embeddings[0])
    
    def test_embed_texts_multiple_texts(self):
        """Test embed_texts with multiple texts."""
        provider = FakeEmbeddingsProvider()
        
        texts = ["First text", "Second text", "Third text"]
        embeddings = provider.embed_texts(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
        
        # Each embedding should be different
        assert embeddings[0] != embeddings[1]
        assert embeddings[1] != embeddings[2]
        assert embeddings[0] != embeddings[2]
    
    def test_embed_texts_deterministic(self):
        """Test embed_texts produces deterministic results."""
        provider = FakeEmbeddingsProvider()
        
        texts = ["Text one", "Text two"]
        embeddings1 = provider.embed_texts(texts)
        embeddings2 = provider.embed_texts(texts)
        
        assert embeddings1 == embeddings2
    
    def test_embed_texts_consistent_with_embed_query(self):
        """Test embed_texts produces same results as embed_query for same text."""
        provider = FakeEmbeddingsProvider()
        
        text = "consistency test"
        query_embedding = provider.embed_query(text)
        text_embeddings = provider.embed_texts([text])
        
        assert query_embedding == text_embeddings[0]
    
    def test_embed_texts_different_dimensions(self):
        """Test embed_texts works with different dimensions."""
        provider_small = FakeEmbeddingsProvider(embedding_dim=10)
        provider_large = FakeEmbeddingsProvider(embedding_dim=1000)
        
        text = "dimension test"
        
        small_embedding = provider_small.embed_texts([text])[0]
        large_embedding = provider_large.embed_texts([text])[0]
        
        assert len(small_embedding) == 10
        assert len(large_embedding) == 1000
    
    def test_empty_string_embedding(self):
        """Test embedding empty string."""
        provider = FakeEmbeddingsProvider()
        
        empty_embedding = provider.embed_query("")
        
        assert len(empty_embedding) == 384
        assert all(isinstance(val, float) for val in empty_embedding)
        assert all(-1.0 <= val <= 1.0 for val in empty_embedding)
    
    def test_unicode_text_embedding(self):
        """Test embedding text with unicode characters."""
        provider = FakeEmbeddingsProvider()
        
        unicode_text = "Hello 世界 🌍 café naïve"
        embedding = provider.embed_query(unicode_text)
        
        assert len(embedding) == 384
        assert all(isinstance(val, float) for val in embedding)
    
    def test_long_text_embedding(self):
        """Test embedding very long text."""
        provider = FakeEmbeddingsProvider()
        
        long_text = "This is a very long text. " * 1000  # ~27,000 characters
        embedding = provider.embed_query(long_text)
        
        assert len(embedding) == 384
        assert all(isinstance(val, float) for val in embedding)
    
    def test_special_characters_embedding(self):
        """Test embedding text with special characters."""
        provider = FakeEmbeddingsProvider()
        
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        embedding = provider.embed_query(special_text)
        
        assert len(embedding) == 384
        assert all(isinstance(val, float) for val in embedding)


class TestGeminiEmbeddingsProvider:
    """Test cases for GeminiEmbeddingsProvider (compilation only)."""
    
    def test_gemini_provider_class_exists(self):
        """Test that GeminiEmbeddingsProvider class can be imported."""
        assert GeminiEmbeddingsProvider is not None
        assert issubclass(GeminiEmbeddingsProvider, EmbeddingsProvider)
    
    def test_gemini_provider_has_required_methods(self):
        """Test that GeminiEmbeddingsProvider implements required methods."""
        assert hasattr(GeminiEmbeddingsProvider, 'embed_texts')
        assert hasattr(GeminiEmbeddingsProvider, 'embed_query')
        assert callable(getattr(GeminiEmbeddingsProvider, 'embed_texts'))
        assert callable(getattr(GeminiEmbeddingsProvider, 'embed_query'))


class TestEmbeddingsProviderInterface:
    """Test cases for EmbeddingsProvider interface."""
    
    def test_interface_is_abstract(self):
        """Test that EmbeddingsProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmbeddingsProvider()
    
    def test_fake_provider_implements_interface(self):
        """Test that FakeEmbeddingsProvider implements the interface."""
        provider = FakeEmbeddingsProvider()
        assert isinstance(provider, EmbeddingsProvider)
    
    def test_interface_methods_exist(self):
        """Test that interface defines required methods."""
        assert hasattr(EmbeddingsProvider, 'embed_texts')
        assert hasattr(EmbeddingsProvider, 'embed_query')


class TestGetEmbeddingsProvider:
    """Test cases for get_embeddings_provider factory function."""
    
    def test_get_embeddings_provider_function_exists(self):
        """Test that get_embeddings_provider function exists."""
        assert callable(get_embeddings_provider)
    
    def test_function_signature_correct(self):
        """Test that function has correct signature."""
        import inspect
        sig = inspect.signature(get_embeddings_provider)
        assert len(sig.parameters) == 0  # No parameters expected
