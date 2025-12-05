"""Document chunking utilities with overlap support."""

from typing import Dict, List


def chunk_document(
    document: Dict[str, str], 
    chunk_size_chars: int = 2000,
    overlap_chars: int = 200
) -> List[Dict[str, str]]:
    """
    Chunk a single document into overlapping chunks.
    
    Args:
        document: Document dict with 'doc_id', 'title', and 'text'
        chunk_size_chars: Maximum size of each chunk in characters
        overlap_chars: Number of characters to overlap between chunks
        
    Returns:
        List of chunk dicts with 'doc_id', 'chunk_id', 'start', 'end', 'text', 'title'
    """
    text = document['text']
    doc_id = document['doc_id']
    title = document['title']
    
    if not text.strip():
        return []
    
    chunks = []
    text_length = len(text)
    
    # If document is smaller than chunk size, return as single chunk
    if text_length <= chunk_size_chars:
        chunks.append({
            'doc_id': doc_id,
            'chunk_id': f"{doc_id}_chunk_0",
            'start': 0,
            'end': text_length,
            'text': text,
            'title': title
        })
        return chunks
    
    # Calculate step size (chunk size - overlap)
    step_size = chunk_size_chars - overlap_chars
    
    if step_size <= 0:
        raise ValueError("overlap_chars must be smaller than chunk_size_chars")
    
    chunk_index = 0
    start = 0
    
    while start < text_length:
        # Calculate end position for this chunk
        end = min(start + chunk_size_chars, text_length)
        
        # Extract chunk text
        chunk_text = text[start:end].strip()
        
        # Skip empty chunks
        if chunk_text:
            chunks.append({
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_chunk_{chunk_index}",
                'start': start,
                'end': end,
                'text': chunk_text,
                'title': title
            })
            chunk_index += 1
        
        # Move to next chunk start position
        start += step_size
        
        # If we've reached the end, break
        if end >= text_length:
            break
    
    return chunks


def chunk_documents(
    documents: List[Dict[str, str]],
    chunk_size_chars: int = 2000,
    overlap_chars: int = 200
) -> List[Dict[str, str]]:
    """
    Chunk multiple documents into overlapping chunks.
    
    Args:
        documents: List of document dicts with 'doc_id', 'title', and 'text'
        chunk_size_chars: Maximum size of each chunk in characters
        overlap_chars: Number of characters to overlap between chunks
        
    Returns:
        List of all chunks from all documents
    """
    all_chunks = []
    
    for document in documents:
        doc_chunks = chunk_document(
            document=document,
            chunk_size_chars=chunk_size_chars,
            overlap_chars=overlap_chars
        )
        all_chunks.extend(doc_chunks)
    
    return all_chunks


def get_chunk_overlap(chunk1: Dict[str, str], chunk2: Dict[str, str]) -> int:
    """
    Calculate the number of overlapping characters between two chunks from the same document.
    
    Args:
        chunk1: First chunk dict
        chunk2: Second chunk dict
        
    Returns:
        Number of overlapping characters, or 0 if chunks are from different documents
        or don't overlap
    """
    # Only check overlap for chunks from same document
    if chunk1['doc_id'] != chunk2['doc_id']:
        return 0
    
    # Determine which chunk comes first
    if chunk1['start'] <= chunk2['start']:
        first_chunk, second_chunk = chunk1, chunk2
    else:
        first_chunk, second_chunk = chunk2, chunk1
    
    # Calculate overlap
    first_end = first_chunk['end']
    second_start = second_chunk['start']
    
    if first_end > second_start:
        return first_end - second_start
    else:
        return 0
