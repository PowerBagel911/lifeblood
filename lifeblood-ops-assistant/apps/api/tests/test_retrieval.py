"""Tests for vector store retrieval functionality."""

import tempfile
import shutil
import os
import pytest
import time
from app.services.retrieval import VectorStore, ChromaVectorStore, get_vector_store
from app.services.embeddings import FakeEmbeddingsProvider


class TestChromaVectorStore:
    """Test cases for ChromaVectorStore implementation."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        # Create temporary directory for each test
        self.temp_dir = tempfile.mkdtemp(prefix="test_chroma_")
        self.store = ChromaVectorStore(
            collection_name="test_collection",
            persist_dir=self.temp_dir
        )
        self.embeddings_provider = FakeEmbeddingsProvider(embedding_dim=384)
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        # Close ChromaDB connections first
        if hasattr(self, 'store') and self.store:
            self.store.close()
        
        # Add a small delay to allow Windows to release file handles
        time.sleep(0.1)
        
        # Clean up temporary directory with retry logic for Windows
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # On Windows, sometimes we need to wait a bit longer
                time.sleep(0.5)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    # If still failing, ignore - OS will clean up temp files eventually
                    pass
    
    def test_initialization(self):
        """Test ChromaVectorStore initializes correctly."""
        assert self.store is not None
        assert self.store.collection_name == "test_collection"
        assert self.store.persist_dir == self.temp_dir
        assert os.path.exists(self.temp_dir)
    
    def test_empty_store_count(self):
        """Test empty store has zero count."""
        assert self.store.count() == 0
    
    def test_upsert_single_chunk(self):
        """Test upserting a single chunk."""
        chunk = {
            'doc_id': 'doc1',
            'chunk_id': 'doc1_chunk_0',
            'title': 'Test Document',
            'text': 'This is a test chunk of text.',
            'start': 0,
            'end': 29
        }
        embedding = self.embeddings_provider.embed_query(chunk['text'])
        
        self.store.upsert_chunks([chunk], [embedding])
        
        # Verify chunk was added
        assert self.store.count() == 1
    
    def test_upsert_multiple_chunks(self):
        """Test upserting multiple chunks from different documents."""
        chunks = [
            {
                'doc_id': 'doc1',
                'chunk_id': 'doc1_chunk_0',
                'title': 'First Document',
                'text': 'This is the first chunk from document one.',
                'start': 0,
                'end': 41
            },
            {
                'doc_id': 'doc1',
                'chunk_id': 'doc1_chunk_1',
                'title': 'First Document',
                'text': 'This is the second chunk from document one.',
                'start': 42,
                'end': 85
            },
            {
                'doc_id': 'doc2',
                'chunk_id': 'doc2_chunk_0',
                'title': 'Second Document',
                'text': 'This is a chunk from the second document.',
                'start': 0,
                'end': 41
            }
        ]
        
        # Generate embeddings for all chunks
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embeddings_provider.embed_texts(texts)
        
        self.store.upsert_chunks(chunks, embeddings)
        
        # Verify all chunks were added
        assert self.store.count() == 3
    
    def test_query_returns_results(self):
        """Test querying returns relevant results."""
        # Index some test documents
        chunks = [
            {
                'doc_id': 'medical_doc',
                'chunk_id': 'medical_chunk_0',
                'title': 'Medical Procedures',
                'text': 'Blood donation requires careful screening of donors.',
                'start': 0,
                'end': 51
            },
            {
                'doc_id': 'safety_doc',
                'chunk_id': 'safety_chunk_0',
                'title': 'Safety Guidelines',
                'text': 'Safety protocols must be followed during plasma collection.',
                'start': 0,
                'end': 58
            },
            {
                'doc_id': 'training_doc',
                'chunk_id': 'training_chunk_0',
                'title': 'Training Manual',
                'text': 'Staff training covers equipment operation and maintenance.',
                'start': 0,
                'end': 56
            }
        ]
        
        # Generate embeddings and upsert
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embeddings_provider.embed_texts(texts)
        self.store.upsert_chunks(chunks, embeddings)
        
        # Query with similar text
        query_text = "blood donation screening"
        query_embedding = self.embeddings_provider.embed_query(query_text)
        
        results = self.store.query(query_embedding, top_k=3)
        
        # Verify we get results
        assert len(results) >= 1
        assert len(results) <= 3
        
        # Check result structure
        for result in results:
            assert 'doc_id' in result
            assert 'title' in result
            assert 'chunk_id' in result
            assert 'text' in result
            assert 'score' in result
            assert isinstance(result['score'], float)
            assert 0.0 <= result['score'] <= 1.0
    
    def test_query_top_k_limit(self):
        """Test query respects top_k parameter."""
        # Index 5 chunks
        chunks = []
        for i in range(5):
            chunks.append({
                'doc_id': f'doc{i}',
                'chunk_id': f'doc{i}_chunk_0',
                'title': f'Document {i}',
                'text': f'This is text content for document number {i}.',
                'start': 0,
                'end': 40
            })
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embeddings_provider.embed_texts(texts)
        self.store.upsert_chunks(chunks, embeddings)
        
        # Query with top_k=2
        query_embedding = self.embeddings_provider.embed_query("document text")
        results = self.store.query(query_embedding, top_k=2)
        
        # Should get exactly 2 results
        assert len(results) == 2
    
    def test_query_empty_store(self):
        """Test querying empty store returns no results."""
        query_embedding = self.embeddings_provider.embed_query("test query")
        results = self.store.query(query_embedding, top_k=5)
        
        assert len(results) == 0
    
    def test_upsert_update_existing(self):
        """Test upserting same chunk_id updates existing record."""
        # Insert initial chunk
        chunk = {
            'doc_id': 'doc1',
            'chunk_id': 'doc1_chunk_0',
            'title': 'Original Title',
            'text': 'Original text content.',
            'start': 0,
            'end': 21
        }
        embedding = self.embeddings_provider.embed_query(chunk['text'])
        self.store.upsert_chunks([chunk], [embedding])
        
        assert self.store.count() == 1
        
        # Update same chunk with new content
        updated_chunk = {
            'doc_id': 'doc1',
            'chunk_id': 'doc1_chunk_0',  # Same ID
            'title': 'Updated Title',
            'text': 'Updated text content with more information.',
            'start': 0,
            'end': 43
        }
        updated_embedding = self.embeddings_provider.embed_query(updated_chunk['text'])
        self.store.upsert_chunks([updated_chunk], [updated_embedding])
        
        # Should still have only 1 chunk (updated, not duplicate)
        assert self.store.count() == 1
        
        # Query to verify content was updated
        query_embedding = self.embeddings_provider.embed_query("updated")
        results = self.store.query(query_embedding, top_k=1)
        
        assert len(results) == 1
        assert results[0]['title'] == 'Updated Title'
    
    def test_upsert_validation_errors(self):
        """Test upsert validation with invalid input."""
        # Test mismatched chunks and embeddings count
        chunks = [{'chunk_id': 'test1', 'text': 'test'}]
        embeddings = [[], []]  # Wrong count
        
        with pytest.raises(ValueError, match="Chunks count .* must match embeddings count"):
            self.store.upsert_chunks(chunks, embeddings)
        
        # Test chunk missing chunk_id
        invalid_chunk = [{'doc_id': 'test', 'text': 'test'}]  # No chunk_id
        embedding = [[0.1, 0.2, 0.3]]
        
        with pytest.raises(ValueError, match="Chunk missing required 'chunk_id' field"):
            self.store.upsert_chunks(invalid_chunk, embedding)
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Empty lists should not raise error
        self.store.upsert_chunks([], [])
        assert self.store.count() == 0
        
        # Empty query embedding should return empty results
        results = self.store.query([], top_k=5)
        assert len(results) == 0
    
    def test_reset_collection(self):
        """Test resetting the collection clears all data."""
        # Add some data
        chunk = {
            'doc_id': 'doc1',
            'chunk_id': 'doc1_chunk_0',
            'title': 'Test Doc',
            'text': 'Test content.',
            'start': 0,
            'end': 13
        }
        embedding = self.embeddings_provider.embed_query(chunk['text'])
        self.store.upsert_chunks([chunk], [embedding])
        
        assert self.store.count() == 1
        
        # Reset collection
        self.store.reset()
        
        # Should be empty now
        assert self.store.count() == 0


class TestVectorStoreInterface:
    """Test cases for VectorStore interface."""
    
    def test_interface_is_abstract(self):
        """Test that VectorStore cannot be instantiated directly."""
        with pytest.raises(TypeError):
            VectorStore()
    
    def test_chroma_store_implements_interface(self):
        """Test that ChromaVectorStore implements the interface."""
        temp_dir = tempfile.mkdtemp()
        try:
            store = ChromaVectorStore(persist_dir=temp_dir)
            assert isinstance(store, VectorStore)
            store.close()
        finally:
            # Clean up with retry logic
            time.sleep(0.1)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                time.sleep(0.5)
                try:
                    shutil.rmtree(temp_dir)
                except PermissionError:
                    pass


class TestGetVectorStore:
    """Test cases for get_vector_store factory function."""
    
    def test_get_vector_store_returns_chroma(self):
        """Test factory function returns ChromaVectorStore instance."""
        temp_dir = tempfile.mkdtemp()
        try:
            store = get_vector_store(persist_dir=temp_dir)
            assert isinstance(store, ChromaVectorStore)
            assert isinstance(store, VectorStore)
            store.close()
        finally:
            # Clean up with retry logic
            time.sleep(0.1)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                time.sleep(0.5)
                try:
                    shutil.rmtree(temp_dir)
                except PermissionError:
                    pass


class TestIntegrationScenarios:
    """Integration tests with realistic document scenarios."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="test_integration_")
        self.store = ChromaVectorStore(persist_dir=self.temp_dir)
        self.embeddings_provider = FakeEmbeddingsProvider()
    
    def teardown_method(self):
        """Clean up after integration tests."""
        # Close ChromaDB connections first
        if hasattr(self, 'store') and self.store:
            self.store.close()
        
        # Add a small delay to allow Windows to release file handles
        time.sleep(0.1)
        
        # Clean up temporary directory with retry logic for Windows
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # On Windows, sometimes we need to wait a bit longer
                time.sleep(0.5)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    # If still failing, ignore - OS will clean up temp files eventually
                    pass
    
    def test_medical_documents_scenario(self):
        """Test indexing and querying medical operation documents."""
        # Simulate realistic medical document chunks
        medical_chunks = [
            {
                'doc_id': 'donor_eligibility',
                'chunk_id': 'donor_eligibility_chunk_0',
                'title': 'Donor Eligibility Guidelines',
                'text': 'Blood donors must be between 17-65 years old, weigh at least 110 pounds, and be in good health. Recent travel to certain countries may disqualify donors.',
                'start': 0,
                'end': 156
            },
            {
                'doc_id': 'plasma_handling',
                'chunk_id': 'plasma_handling_chunk_0', 
                'title': 'Plasma Collection Procedures',
                'text': 'Plasma collection requires sterile equipment and trained staff. Temperature must be maintained between 2-6°C during storage and transport.',
                'start': 0,
                'end': 141
            },
            {
                'doc_id': 'emergency_procedures',
                'chunk_id': 'emergency_procedures_chunk_0',
                'title': 'Emergency Response Protocols',
                'text': 'In case of adverse reactions during donation, immediately stop collection, assess donor condition, and contact medical supervisor.',
                'start': 0,
                'end': 134
            }
        ]
        
        # Index documents
        texts = [chunk['text'] for chunk in medical_chunks]
        embeddings = self.embeddings_provider.embed_texts(texts)
        self.store.upsert_chunks(medical_chunks, embeddings)
        
        # Test various medical queries
        queries = [
            "donor age requirements",
            "plasma storage temperature", 
            "emergency response procedure"
        ]
        
        for query_text in queries:
            query_embedding = self.embeddings_provider.embed_query(query_text)
            results = self.store.query(query_embedding, top_k=2)
            
            # Should find relevant results
            assert len(results) >= 1
            
            # Results should have proper structure
            for result in results:
                assert result['doc_id'] in ['donor_eligibility', 'plasma_handling', 'emergency_procedures']
                assert result['title'] is not None
                assert result['text'] is not None
                assert 0.0 <= result['score'] <= 1.0
