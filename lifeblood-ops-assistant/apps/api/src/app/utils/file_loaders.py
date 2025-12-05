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
        # Try multiple path resolution strategies
        current_file = Path(__file__)
        
        # Strategy 1: Go up from current file to project root (utils -> app -> src -> api -> apps -> project)
        project_root = current_file.parent.parent.parent.parent.parent
        docs_path = project_root / docs_dir
        
        # Strategy 2: If that doesn't work, try from current working directory
        if not docs_path.exists():
            docs_path = Path.cwd() / docs_dir
        
        # Strategy 3: Try hardcoded path as last resort
        if not docs_path.exists():
            hardcoded_path = Path("E:/Personal Projects/lifeblood/lifeblood-ops-assistant") / docs_dir
            if hardcoded_path.exists():
                docs_path = hardcoded_path
    else:
        docs_path = Path(docs_dir)
    
    documents = []
    
    print(f"Debug - Looking for documents in: {docs_path}")
    print(f"Debug - Path exists: {docs_path.exists()}")
    
    if not docs_path.exists():
        print(f"Directory not found: {docs_path}")
        # Try alternative path resolution in case we're running from different directory
        alternative_path = Path.cwd() / docs_dir
        print(f"Debug - Trying alternative path: {alternative_path}")
        if alternative_path.exists():
            docs_path = alternative_path
            print(f"Debug - Using alternative path: {docs_path}")
        else:
            print(f"Debug - Alternative path also doesn't exist")
            return documents
    
    # Supported file extensions
    supported_extensions = {'.txt', '.md'}
    
    # Load all supported files
    print(f"Debug - Scanning directory for files...")
    all_files = list(docs_path.rglob('*'))
    print(f"Debug - Found {len(all_files)} total files/directories")
    
    supported_files = [f for f in all_files if f.is_file() and f.suffix.lower() in supported_extensions]
    print(f"Debug - Found {len(supported_files)} supported files: {[f.name for f in supported_files]}")
    
    for file_path in supported_files:
        print(f"Debug - Processing file: {file_path}")
        doc = load_document_file(file_path)
        if doc:
            print(f"Debug - Successfully loaded: {doc['doc_id']}")
            documents.append(doc)
        else:
            print(f"Debug - Failed to load: {file_path}")
    
    print(f"Debug - Final document count: {len(documents)}")
    return documents
