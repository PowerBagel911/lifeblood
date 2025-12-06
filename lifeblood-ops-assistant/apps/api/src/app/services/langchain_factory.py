"""LangChain component factory using existing configuration."""

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from ..core.config import Settings

logger = logging.getLogger(__name__)


def build_lc_embeddings(config: Settings) -> GoogleGenerativeAIEmbeddings:
    """
    Build LangChain GoogleGenerativeAIEmbeddings using configuration.
    
    Args:
        config: Application settings with Gemini configuration
        
    Returns:
        Configured GoogleGenerativeAIEmbeddings instance
    """
    # Ensure the model name has the "models/" prefix for LangChain
    model_name = config.GEMINI_EMBED_MODEL
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
    
    logger.info(f"Building LangChain embeddings with model: {model_name}")
    
    # Use the API key from config (compatibility bridge should have set GOOGLE_API_KEY)
    api_key = config.GOOGLE_API_KEY or config.GEMINI_API_KEY
    if not api_key:
        raise ValueError(
            "Google API key required for LangChain embeddings. "
            "Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
        )
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=api_key
        )
        
        logger.debug("Successfully created LangChain GoogleGenerativeAIEmbeddings")
        return embeddings
        
    except Exception as e:
        logger.error(f"Failed to create LangChain embeddings: {e}")
        raise ValueError(f"LangChain embeddings initialization failed: {e}")


def build_lc_llm(config: Settings) -> ChatGoogleGenerativeAI:
    """
    Build LangChain ChatGoogleGenerativeAI using configuration.
    
    Args:
        config: Application settings with Gemini configuration
        
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    model_name = config.GEMINI_MODEL
    logger.info(f"Building LangChain LLM with model: {model_name}")
    
    # Use the API key from config (compatibility bridge should have set GOOGLE_API_KEY)
    api_key = config.GOOGLE_API_KEY or config.GEMINI_API_KEY
    if not api_key:
        raise ValueError(
            "Google API key required for LangChain LLM. "
            "Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
        )
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,  # Low temperature for more consistent medical responses
            convert_system_message_to_human=True  # Handle system messages properly
        )
        
        logger.debug("Successfully created LangChain ChatGoogleGenerativeAI")
        return llm
        
    except Exception as e:
        logger.error(f"Failed to create LangChain LLM: {e}")
        raise ValueError(f"LangChain LLM initialization failed: {e}")


def build_lc_vectorstore(config: Settings, embeddings: GoogleGenerativeAIEmbeddings) -> Chroma:
    """
    Build LangChain Chroma vector store using configuration and embeddings.
    
    Args:
        config: Application settings with ChromaDB configuration
        embeddings: GoogleGenerativeAIEmbeddings instance for the vector store
        
    Returns:
        Configured Chroma vector store instance
    """
    collection_name = "lifeblood_docs"
    persist_directory = config.CHROMA_PERSIST_DIR
    
    logger.info(f"Building LangChain Chroma vectorstore: collection='{collection_name}', persist_dir='{persist_directory}'")
    
    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        logger.debug("Successfully created LangChain Chroma vectorstore")
        return vectorstore
        
    except Exception as e:
        logger.error(f"Failed to create LangChain vectorstore: {e}")
        raise ValueError(f"LangChain vectorstore initialization failed: {e}")


def build_lc_components(config: Settings) -> dict[str, Any]:
    """
    Build all LangChain components together for convenience.
    
    Args:
        config: Application settings
        
    Returns:
        Dictionary with 'embeddings', 'llm', and 'vectorstore' keys
    """
    logger.info("Building complete LangChain component suite")
    
    try:
        # Build embeddings first (needed for vectorstore)
        embeddings = build_lc_embeddings(config)
        
        # Build LLM
        llm = build_lc_llm(config)
        
        # Build vectorstore with embeddings
        vectorstore = build_lc_vectorstore(config, embeddings)
        
        components = {
            'embeddings': embeddings,
            'llm': llm,
            'vectorstore': vectorstore
        }
        
        logger.info("Successfully built all LangChain components")
        return components
        
    except Exception as e:
        logger.error(f"Failed to build LangChain components: {e}")
        raise
