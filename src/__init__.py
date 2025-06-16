"""
MnemoX Lite - Semantic Memory System for LLMs

A lightweight, local-first semantic memory system that implements core MnemoX concepts:
- Cognitive Fragments: Basic units of information with semantic embeddings
- Cognitive Contexts: Thematic organization of related fragments
- Cognitive Anchors: Important reference points for navigation
- Flexible project schemas: Completely customizable metadata structures

Features:
- Qdrant-powered vector search for superior performance
- SQLite for structured metadata and relationships
- Local deployment with optional cloud scaling
- MCP protocol integration for LLM access
- Python-native with excellent developer experience
"""

__version__ = "0.1.0"
__author__ = "MnemoX Team"
__description__ = "Semantic memory service for LLMs - testground for MnemoX concepts"

# Import main components for easy access
from .core import StorageManager, EmbeddingService, MemoryService
from .models import Project, MemoryFragment, MemoryContext, CognitiveAnchor, SearchOptions, SearchResult

__all__ = [
    "StorageManager",
    "EmbeddingService", 
    "MemoryService",
    "Project",
    "MemoryFragment", 
    "MemoryContext",
    "CognitiveAnchor",
    "SearchOptions",
    "SearchResult"
]
