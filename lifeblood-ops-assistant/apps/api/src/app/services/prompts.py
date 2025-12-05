"""Prompt building service for RAG (Retrieval-Augmented Generation) responses."""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


# Core grounding rules that apply to all responses
CORE_RULES = """
CRITICAL INSTRUCTIONS:
- Answer ONLY using the provided sources below
- If the sources don't contain the answer to the question, clearly say "I don't know" or "The provided sources don't contain information about this topic"
- Do not use external knowledge or make assumptions beyond what's explicitly stated in the sources
- Always cite your sources using the format [1], [2], etc. when referencing information from the sources
- If multiple sources support the same point, cite all relevant sources like [1,2]
"""

# Mode-specific response templates
MODE_TEMPLATES = {
    "general": """
Provide a concise, direct answer to the question based on the sources. Use clear, professional language and cite your sources appropriately.
""",
    
    "checklist": """
Provide your answer as a clear, step-by-step checklist or numbered list. Break down the information into actionable steps or organized points. Each step should be cited with the appropriate sources.

Format your response as:
1. [Step/Point 1] [citation]
2. [Step/Point 2] [citation]
3. [Continue as needed...]
""",
    
    "plain_english": """
Provide a simplified explanation that would be easy for anyone to understand. Use simple language, avoid technical jargon, and explain concepts clearly. Break down complex information into digestible parts.
"""
}


def format_sources(chunks: List[Dict[str, Any]]) -> str:
    """
    Format document chunks as numbered sources.
    
    Args:
        chunks: List of chunk dictionaries with text and metadata
        
    Returns:
        Formatted sources string
    """
    if not chunks:
        return "No sources provided."
    
    sources_text = "SOURCES:\n"
    
    for i, chunk in enumerate(chunks, 1):
        # Get chunk text
        text = chunk.get('text', '').strip()
        if not text:
            continue
        
        # Add source header with metadata if available
        source_header = f"Source [{i}]"
        if chunk.get('title'):
            source_header += f" - {chunk['title']}"
        if chunk.get('doc_id'):
            source_header += f" (Document: {chunk['doc_id']})"
        
        sources_text += f"\n{source_header}:\n{text}\n"
    
    return sources_text


def get_mode_instructions(mode: str) -> str:
    """
    Get response format instructions for the specified mode.
    
    Args:
        mode: Response mode ("general", "checklist", or "plain_english")
        
    Returns:
        Mode-specific instruction text
    """
    mode = mode.lower().strip()
    
    if mode in MODE_TEMPLATES:
        return MODE_TEMPLATES[mode]
    else:
        logger.warning(f"Unknown mode '{mode}', using 'general' mode")
        return MODE_TEMPLATES["general"]


def build_citation_instructions() -> str:
    """
    Build instructions for proper source citation.
    
    Returns:
        Citation instruction text
    """
    return """
CITATION REQUIREMENTS:
- When referencing information from sources, immediately cite the source number in square brackets [1], [2], etc.
- If information comes from multiple sources, cite all relevant sources [1,2,3]
- Place citations right after the relevant statement, not at the end of paragraphs
- Every factual claim must have a citation unless it's a direct restatement of the question

EXAMPLE:
"Blood donors must be between 17-65 years old [1] and weigh at least 110 pounds [1,2]. The screening process includes a health questionnaire [3]."
"""


def build_prompt(question: str, chunks: List[Dict[str, Any]], mode: str = "general") -> str:
    """
    Build a complete RAG prompt with question, sources, and instructions.
    
    Args:
        question: The user's question to answer
        chunks: List of retrieved document chunks with text and metadata
        mode: Response mode - "general", "checklist", or "plain_english"
        
    Returns:
        Complete formatted prompt for the LLM
    """
    if not question.strip():
        raise ValueError("Question cannot be empty")
    
    # Log prompt building
    logger.debug(f"Building prompt for mode '{mode}' with {len(chunks)} source chunks")
    
    # Build prompt sections
    sections = [
        "You are a knowledgeable assistant answering questions about medical operations and procedures.",
        "",
        CORE_RULES.strip(),
        "",
        build_citation_instructions().strip(),
        "",
        get_mode_instructions(mode).strip(),
        "",
        format_sources(chunks),
        "",
        f"QUESTION: {question.strip()}",
        "",
        "ANSWER:"
    ]
    
    # Join sections with proper spacing
    prompt = "\n".join(sections)
    
    logger.debug(f"Generated prompt with {len(prompt)} characters")
    
    return prompt


def build_prompt_no_sources(question: str, mode: str = "general") -> str:
    """
    Build a prompt when no relevant sources are found.
    
    Args:
        question: The user's question
        mode: Response mode (for consistency, though response will be standard)
        
    Returns:
        Prompt indicating no sources available
    """
    logger.debug(f"Building no-sources prompt for mode '{mode}'")
    
    sections = [
        "You are a knowledgeable assistant answering questions about medical operations and procedures.",
        "",
        CORE_RULES.strip(),
        "",
        "SOURCES:",
        "No relevant sources found for this question.",
        "",
        f"QUESTION: {question.strip()}",
        "",
        "ANSWER:",
        "I don't have access to relevant sources to answer your question about this topic. Please try rephrasing your question or ask about a different aspect of medical operations."
    ]
    
    return "\n".join(sections)


def validate_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and filter chunks to ensure they have required fields.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        List of valid chunks with required fields
    """
    valid_chunks = []
    
    for i, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            logger.warning(f"Chunk {i} is not a dictionary, skipping")
            continue
        
        if not chunk.get('text', '').strip():
            logger.warning(f"Chunk {i} has empty text, skipping")
            continue
        
        valid_chunks.append(chunk)
    
    logger.debug(f"Validated {len(valid_chunks)} out of {len(chunks)} chunks")
    return valid_chunks


# Convenience function for common usage patterns
def build_rag_prompt(question: str, chunks: List[Dict[str, Any]], mode: str = "general") -> str:
    """
    Build a RAG prompt with validation and fallback handling.
    
    Args:
        question: User question
        chunks: Retrieved chunks
        mode: Response mode
        
    Returns:
        Complete prompt, either with sources or no-sources message
    """
    # Validate inputs
    if not question or not question.strip():
        raise ValueError("Question is required")
    
    # Validate and filter chunks
    valid_chunks = validate_chunks(chunks) if chunks else []
    
    # Build appropriate prompt
    if valid_chunks:
        return build_prompt(question, valid_chunks, mode)
    else:
        return build_prompt_no_sources(question, mode)
