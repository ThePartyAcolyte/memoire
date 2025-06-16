"""
Embedding module for MnemoX Lite.

This module provides semantic embedding capabilities using external APIs.
Organized into logical units for maintainability.
"""

from .service import EmbeddingService
from .cache import EmbeddingCache  
from .providers import GeminiProvider

__all__ = [
    "EmbeddingService",
    "EmbeddingCache", 
    "GeminiProvider"
]
