"""Configuration management using Pydantic settings."""

from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    APP_ENV: str = Field(default="development", description="Application environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # LLM Provider settings
    LLM_PROVIDER: str = Field(default="gemini", description="LLM provider")
    EMBED_PROVIDER: str = Field(default="gemini", description="Embedding provider")
    
    # Gemini settings
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    GEMINI_EMBED_MODEL: str = Field(default="gemini-embedding-001", description="Gemini embedding model name")
    
    # API Keys (sensitive - won't be printed)
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Gemini API key")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google API key")
    
    # Vector store settings
    CHROMA_PERSIST_DIR: str = Field(default=".chroma", description="ChromaDB persistence directory")
    
    class Config:
        env_file = "../../../.env"  # Path from src/ to repo root
        case_sensitive = True
        # Hide sensitive fields from representation
        repr_exclude = {"GEMINI_API_KEY", "GOOGLE_API_KEY"}
    
    def model_dump(self, **kwargs) -> dict:
        """Override to exclude sensitive fields from serialization."""
        data = super().model_dump(**kwargs)
        # Remove sensitive keys from output
        sensitive_keys = {"GEMINI_API_KEY", "GOOGLE_API_KEY"}
        return {k: v for k, v in data.items() if k not in sensitive_keys}
    
    def validate_gemini_api_keys(self) -> None:
        """Validate that required API keys are available for Gemini providers."""
        gemini_required = (
            self.LLM_PROVIDER == "gemini" or 
            self.EMBED_PROVIDER == "gemini"
        )
        
        if gemini_required:
            if not self.GEMINI_API_KEY and not self.GOOGLE_API_KEY:
                raise ValueError(
                    "Gemini API configuration error: When using Gemini as LLM_PROVIDER or EMBED_PROVIDER, "
                    "you must set either GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
                )
            
            if self.GEMINI_API_KEY and self.GOOGLE_API_KEY:
                raise ValueError(
                    "Gemini API configuration error: Set either GEMINI_API_KEY or GOOGLE_API_KEY, not both."
                )


# Global settings instance
settings = Settings()
