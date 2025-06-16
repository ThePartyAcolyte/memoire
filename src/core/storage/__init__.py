"""
Storage manager for MnemoX Lite - powered by Qdrant + SQLite.

This module provides a unified interface for:
- Qdrant: Vector embeddings and semantic search with superior performance
- SQLite: Structured metadata and relationships
- Automatic synchronization between both systems

Key design principles:
- Embeddings in Qdrant for blazing-fast semantic search
- Metadata in SQLite for structured queries  
- Project-based segregation for multi-tenancy
- Atomic operations across both stores
- Local-first with optional cloud scaling
"""

from .manager import StorageManager

# Export main class
__all__ = ["StorageManager"]