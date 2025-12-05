"""File loading utilities for processing documents."""

import os
from pathlib import Path
from typing import Dict, List, Optional


def extract_title_from_content(text: str, fallback_title: str) -> str:
    """Extract title from document content, fallback to provided title."""
    lines = text.strip().split('\n')
    if not lines:
        return fallback_title
    
    first_line = lines[0].strip()
    
    # Check if first line is a markdown header
    if first_line.startswith('# '):
        return first_line[2:].strip()
    
    # Check if first line looks like a title (no lowercase words, reasonable length)
    if len(first_line) < 100 and first_line and not first_line.islower():
        return first_line
    
    return fallback_title


def load_document_file(file_path: Path) -> Optional[Dict[str, str]]:
    """Load a single document file and extract metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        if not text:
            return None
            
        # Generate doc_id from filename (without extension)
        doc_id = file_path.stem
        
        # Generate fallback title from filename
        fallback_title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
        
        # Extract title from content
        title = extract_title_from_content(text, fallback_title)
        
        return {
            'doc_id': doc_id,
            'title': title,
            'text': text
        }
        
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None


def load_documents_from_directory(docs_dir: str = "data/docs") -> List[Dict[str, str]]:
    """Load all .txt and .md files from the specified directory."""
    # Convert relative path to absolute path from project root
    if not os.path.isabs(docs_dir):
        # Assume we're running from apps/api/src, so go up to project root
        project_root = Path(__file__).parent.parent.parent.parent.parent
        docs_path = project_root / docs_dir
    else:
        docs_path = Path(docs_dir)
    
    documents = []
    
    if not docs_path.exists():
        print(f"Directory not found: {docs_path}")
        return documents
    
    # Supported file extensions
    supported_extensions = {'.txt', '.md'}
    
    # Load all supported files
    for file_path in docs_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            doc = load_document_file(file_path)
            if doc:
                documents.append(doc)
    
    return documents
