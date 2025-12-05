"""LLM client implementations for text generation."""

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List

from google import genai

from ..core.config import settings

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract interface for language model clients."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text based on the given prompt.
        
        Args:
            prompt: Input text prompt for generation
            
        Returns:
            Generated text response
        """
        pass


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing and offline operation.
    
    Generates deterministic responses based on prompt content.
    Safe for offline use and produces consistent results.
    """
    
    def __init__(self, response_templates: List[str] = None):
        """
        Initialize mock LLM client.
        
        Args:
            response_templates: List of response templates to cycle through
        """
        if response_templates is None:
            self.response_templates = [
                "This is a mock response to your query about: {topic}",
                "Based on the provided information about {topic}, here's what I can tell you:",
                "Regarding {topic}, the key points are as follows:",
                "To address your question about {topic}, consider the following:",
                "Here's a comprehensive answer about {topic}:"
            ]
        else:
            self.response_templates = response_templates
        
        logger.info(f"Initialized MockLLMClient with {len(self.response_templates)} response templates")
    
    def _extract_topic(self, prompt: str) -> str:
        """
        Extract a topic from the prompt for more realistic responses.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Extracted topic or generic fallback
        """
        import re
        
        # Simple topic extraction - take first few meaningful words
        words = prompt.strip().split()[:5]
        if words:
            # Filter out common question words and clean punctuation
            topic_words = []
            for word in words:
                # Remove punctuation and convert to lowercase for filtering
                clean_word = re.sub(r'[^\w]', '', word.lower())
                if clean_word and clean_word not in {'what', 'how', 'why', 'when', 'where', 'who', 'is', 'are', 'the', 'a', 'an', 'do', 'does', 'can', 'will', 'should'}:
                    # Keep original word for output (with punctuation if needed)
                    topic_words.append(word.strip('.,!?;:'))
            
            if topic_words:
                return ' '.join(topic_words[:3])  # Take first 3 meaningful words
        
        return "the requested topic"
    
    def generate(self, prompt: str) -> str:
        """
        Generate a mock response based on the prompt.
        
        Args:
            prompt: Input text prompt
            
        Returns:
            Deterministic mock response
        """
        if not prompt.strip():
            return "Please provide a specific question or prompt for me to respond to."
        
        logger.debug("Generating mock response for prompt")
        
        # Use prompt hash to deterministically select a template
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        template_index = int(prompt_hash, 16) % len(self.response_templates)
        
        # Extract topic for more contextual response
        topic = self._extract_topic(prompt)
        
        # Generate response from template
        template = self.response_templates[template_index]
        response = template.format(topic=topic)
        
        # Add some deterministic "details" based on prompt content
        prompt_length = len(prompt)
        if prompt_length > 100:
            response += " This is a detailed response given the comprehensive nature of your query."
        elif "?" in prompt:
            response += " I hope this answers your question effectively."
        
        return response


class GeminiLLMClient(LLMClient):
    """
    Gemini LLM client using Google GenAI SDK.
    
    Requires valid GEMINI_API_KEY or GOOGLE_API_KEY in environment.
    """
    
    def __init__(self):
        """Initialize Gemini LLM client."""
        # Use the API key from settings
        api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY or GOOGLE_API_KEY."
            )
        
        # Configure the client
        genai.configure(api_key=api_key)
        self.client = genai.Client()
        self.model_name = settings.GEMINI_MODEL
        
        logger.info(f"Initialized GeminiLLMClient with model {self.model_name}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: Input text prompt for generation
            
        Returns:
            Generated text from Gemini API
        """
        if not prompt.strip():
            return "Please provide a prompt for text generation."
        
        logger.debug("Generating text with Gemini API")
        
        try:
            # Call Gemini generation API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                logger.debug("Successfully generated text with Gemini")
                return response.text
            
            # Fallback: join candidate parts if direct text access fails
            if hasattr(response, 'candidates') and response.candidates:
                parts = []
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    parts.append(part.text)
                
                if parts:
                    result = ''.join(parts)
                    logger.debug("Successfully extracted text from candidate parts")
                    return result
            
            # If no text could be extracted
            logger.warning("No text content found in Gemini response")
            return "I apologize, but I couldn't generate a response to your prompt."
            
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            raise


def get_llm_client() -> LLMClient:
    """
    Factory function to get the configured LLM client.
    
    Returns:
        Configured LLM client based on settings
    """
    provider_name = settings.LLM_PROVIDER.lower()
    
    if provider_name == "gemini":
        return GeminiLLMClient()
    elif provider_name == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
