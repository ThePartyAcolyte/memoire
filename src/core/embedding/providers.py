"""
Provider implementations for different embedding APIs.

Each provider handles API-specific authentication and request formatting.
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name used by this provider."""
        pass


class GeminiProvider(EmbeddingProvider):
    """Google Gemini API provider for embeddings."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """Initialize Gemini provider.
        
        Args:
            api_key: Google AI API key (uses GOOGLE_API_KEY env var if not provided)
            model: Model to use for embeddings
        """
        # Get config values if not provided
        from ...config import config
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if model is None:
            config_model = config.get("embedding.model", "text-embedding-004")
            # Ensure model has 'models/' prefix for Google API
            model = config_model if config_model.startswith("models/") else f"models/{config_model}"
        self.model = model
        
        # Get dimension from config based on model
        self._dimension = config.get("embedding.dimension", 768)
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        # Import and initialize client
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"GeminiProvider initialized with model: {model}")
        except ImportError:
            raise ImportError(
                "google-genai package not installed. Please run: pip install google-genai"
            )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            RuntimeError: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            # Call Gemini API
            response = self.client.models.embed_content(
                model=self.model,
                contents=text
            )
            
            # Extract embedding from response
            embedding = response.embeddings[0].values
            
            logger.debug(f"Generated embedding for text: {text[:50]}... (dim: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}")
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.model


class AnthropicProvider(EmbeddingProvider):
    """Anthropic Claude provider for embeddings (placeholder - not yet available)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        logger.warning("AnthropicProvider is a placeholder - embeddings API not yet available")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Anthropic API (not yet available)."""
        raise NotImplementedError("Anthropic embeddings API not yet available")
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return 1024  # Placeholder
    
    def get_model_name(self) -> str:
        """Get model name."""
        return "claude-embedding-v1"  # Placeholder
