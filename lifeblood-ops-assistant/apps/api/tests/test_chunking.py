"""Tests for document chunking utilities."""

import pytest
from app.utils.chunking import chunk_document, chunk_documents, get_chunk_overlap


class TestChunkDocument:
    """Test cases for chunk_document function."""
    
    def test_empty_document(self):
        """Test chunking empty document returns no chunks."""
        document = {'doc_id': 'test', 'title': 'Test', 'text': ''}
        chunks = chunk_document(document)
        assert chunks == []
    
    def test_whitespace_only_document(self):
        """Test chunking whitespace-only document returns no chunks."""
        document = {'doc_id': 'test', 'title': 'Test', 'text': '   \n\t  '}
        chunks = chunk_document(document)
        assert chunks == []
    
    def test_small_document(self):
        """Test chunking document smaller than chunk size."""
        text = "This is a small document."
        document = {'doc_id': 'small', 'title': 'Small Doc', 'text': text}
        chunks = chunk_document(document, chunk_size_chars=100, overlap_chars=20)
        
        assert len(chunks) == 1
        assert chunks[0]['doc_id'] == 'small'
        assert chunks[0]['chunk_id'] == 'small_chunk_0'
        assert chunks[0]['start'] == 0
        assert chunks[0]['end'] == len(text)
        assert chunks[0]['text'] == text
        assert chunks[0]['title'] == 'Small Doc'
    
    def test_exact_chunk_size_document(self):
        """Test document exactly equal to chunk size."""
        text = 'A' * 100
        document = {'doc_id': 'exact', 'title': 'Exact', 'text': text}
        chunks = chunk_document(document, chunk_size_chars=100, overlap_chars=20)
        
        assert len(chunks) == 1
        assert chunks[0]['text'] == text
        assert chunks[0]['start'] == 0
        assert chunks[0]['end'] == 100
    
    def test_large_document_chunking(self):
        """Test chunking large document creates multiple chunks with overlap."""
        # Create a 500-character text
        text = 'A' * 500
        document = {'doc_id': 'large', 'title': 'Large Doc', 'text': text}
        chunks = chunk_document(document, chunk_size_chars=200, overlap_chars=50)
        
        # Should create 3 chunks: [0:200], [150:350], [300:500]
        assert len(chunks) >= 2
        
        # Check all chunks are properly formatted
        for i, chunk in enumerate(chunks):
            assert chunk['doc_id'] == 'large'
            assert chunk['chunk_id'] == f'large_chunk_{i}'
            assert chunk['title'] == 'Large Doc'
            assert len(chunk['text']) > 0  # No empty chunks
            assert chunk['start'] >= 0
            assert chunk['end'] <= len(text)
            assert chunk['start'] < chunk['end']
    
    def test_overlap_exists(self):
        """Test that consecutive chunks have proper overlap."""
        text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' * 20  # 520 characters
        document = {'doc_id': 'overlap_test', 'title': 'Overlap Test', 'text': text}
        chunks = chunk_document(document, chunk_size_chars=100, overlap_chars=30)
        
        assert len(chunks) > 1
        
        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Current chunk should end after next chunk starts (overlap)
            assert current_chunk['end'] > next_chunk['start']
            
            # Calculate expected overlap
            overlap = get_chunk_overlap(current_chunk, next_chunk)
            assert overlap > 0
            assert overlap <= 30  # Should not exceed specified overlap
    
    def test_no_empty_chunks(self):
        """Test that no empty chunks are created."""
        text = "Word " * 1000  # 5000 characters with spaces
        document = {'doc_id': 'no_empty', 'title': 'No Empty', 'text': text}
        chunks = chunk_document(document, chunk_size_chars=200, overlap_chars=50)
        
        for chunk in chunks:
            assert len(chunk['text'].strip()) > 0
            assert chunk['text'].strip()  # Ensure not just whitespace
    
    def test_invalid_overlap_size(self):
        """Test error when overlap is greater than or equal to chunk size."""
        document = {'doc_id': 'test', 'title': 'Test', 'text': 'A' * 1000}
        
        # Overlap equal to chunk size
        with pytest.raises(ValueError):
            chunk_document(document, chunk_size_chars=100, overlap_chars=100)
        
        # Overlap greater than chunk size
        with pytest.raises(ValueError):
            chunk_document(document, chunk_size_chars=100, overlap_chars=150)
    
    def test_different_chunk_sizes(self):
        """Test chunking with different chunk sizes."""
        text = 'X' * 1000
        document = {'doc_id': 'size_test', 'title': 'Size Test', 'text': text}
        
        # Small chunks
        small_chunks = chunk_document(document, chunk_size_chars=100, overlap_chars=20)
        # Large chunks  
        large_chunks = chunk_document(document, chunk_size_chars=500, overlap_chars=50)
        
        assert len(small_chunks) > len(large_chunks)
        
        # All chunks should respect their size limits
        for chunk in small_chunks:
            assert len(chunk['text']) <= 100
        
        for chunk in large_chunks:
            assert len(chunk['text']) <= 500


class TestChunkDocuments:
    """Test cases for chunk_documents function."""
    
    def test_empty_document_list(self):
        """Test chunking empty document list."""
        chunks = chunk_documents([])
        assert chunks == []
    
    def test_multiple_documents(self):
        """Test chunking multiple documents."""
        docs = [
            {'doc_id': 'doc1', 'title': 'Doc 1', 'text': 'A' * 500},
            {'doc_id': 'doc2', 'title': 'Doc 2', 'text': 'B' * 300},
            {'doc_id': 'doc3', 'title': 'Doc 3', 'text': 'C' * 50}
        ]
        
        chunks = chunk_documents(docs, chunk_size_chars=200, overlap_chars=50)
        
        # Should have chunks from all documents
        doc_ids = {chunk['doc_id'] for chunk in chunks}
        assert doc_ids == {'doc1', 'doc2', 'doc3'}
        
        # Check each document has proper chunks
        doc1_chunks = [c for c in chunks if c['doc_id'] == 'doc1']
        doc2_chunks = [c for c in chunks if c['doc_id'] == 'doc2']
        doc3_chunks = [c for c in chunks if c['doc_id'] == 'doc3']
        
        assert len(doc1_chunks) > 1  # 500 chars should create multiple chunks
        assert len(doc2_chunks) >= 1  # 300 chars should create at least 1 chunk
        assert len(doc3_chunks) == 1  # 50 chars should create 1 chunk
    
    def test_mixed_document_sizes(self):
        """Test chunking documents of various sizes."""
        docs = [
            {'doc_id': 'tiny', 'title': 'Tiny', 'text': 'Hi'},
            {'doc_id': 'empty', 'title': 'Empty', 'text': ''},
            {'doc_id': 'huge', 'title': 'Huge', 'text': 'Z' * 2000}
        ]
        
        chunks = chunk_documents(docs, chunk_size_chars=100, overlap_chars=20)
        
        # Empty document should produce no chunks
        empty_chunks = [c for c in chunks if c['doc_id'] == 'empty']
        assert len(empty_chunks) == 0
        
        # Tiny document should produce 1 chunk
        tiny_chunks = [c for c in chunks if c['doc_id'] == 'tiny']
        assert len(tiny_chunks) == 1
        
        # Huge document should produce multiple chunks
        huge_chunks = [c for c in chunks if c['doc_id'] == 'huge']
        assert len(huge_chunks) > 1


class TestGetChunkOverlap:
    """Test cases for get_chunk_overlap function."""
    
    def test_overlapping_chunks(self):
        """Test calculating overlap between overlapping chunks."""
        chunk1 = {
            'doc_id': 'test',
            'chunk_id': 'test_chunk_0',
            'start': 0,
            'end': 100,
            'text': 'A' * 100,
            'title': 'Test'
        }
        chunk2 = {
            'doc_id': 'test',
            'chunk_id': 'test_chunk_1', 
            'start': 80,
            'end': 180,
            'text': 'A' * 100,
            'title': 'Test'
        }
        
        overlap = get_chunk_overlap(chunk1, chunk2)
        assert overlap == 20  # 100 - 80 = 20
        
        # Test reverse order
        overlap_reverse = get_chunk_overlap(chunk2, chunk1)
        assert overlap_reverse == 20
    
    def test_non_overlapping_chunks(self):
        """Test chunks that don't overlap."""
        chunk1 = {
            'doc_id': 'test',
            'start': 0,
            'end': 100,
            'text': 'A' * 100,
            'title': 'Test'
        }
        chunk2 = {
            'doc_id': 'test',
            'start': 200,
            'end': 300,
            'text': 'B' * 100,
            'title': 'Test'
        }
        
        overlap = get_chunk_overlap(chunk1, chunk2)
        assert overlap == 0
    
    def test_different_documents(self):
        """Test chunks from different documents."""
        chunk1 = {
            'doc_id': 'doc1',
            'start': 0,
            'end': 100,
            'text': 'A' * 100,
            'title': 'Doc 1'
        }
        chunk2 = {
            'doc_id': 'doc2',
            'start': 50,
            'end': 150,
            'text': 'B' * 100,
            'title': 'Doc 2'
        }
        
        overlap = get_chunk_overlap(chunk1, chunk2)
        assert overlap == 0
    
    def test_adjacent_chunks(self):
        """Test chunks that are adjacent but don't overlap."""
        chunk1 = {
            'doc_id': 'test',
            'start': 0,
            'end': 100,
            'text': 'A' * 100,
            'title': 'Test'
        }
        chunk2 = {
            'doc_id': 'test', 
            'start': 100,
            'end': 200,
            'text': 'B' * 100,
            'title': 'Test'
        }
        
        overlap = get_chunk_overlap(chunk1, chunk2)
        assert overlap == 0
