"""
Core module for MnemoX Lite semantic memory system.

This module provides the foundational services for:
- Storage management (Qdrant + SQLite)
- Embedding generation (Google Vertex AI, Anthropic)
- Memory operations (fragments, contexts, anchors)
- Semantic search and retrieval

Key components:
- StorageManager: Handles both vector and structured data storage
- EmbeddingService: Generates semantic embeddings from text
- MemoryService: High-level memory operations and search
"""

from .storage import StorageManager
from .embedding import EmbeddingService  
from .memory import MemoryService

__all__ = [
    "StorageManager",
    "EmbeddingService", 
    "MemoryService"
]
