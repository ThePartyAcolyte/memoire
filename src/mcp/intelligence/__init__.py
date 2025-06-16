"""
Intelligence layer for MnemoX Lite.

This module contains the cognitive processing components that handle:
- Content analysis and chunking
- Emergent contextualization 
- Memory synthesis and curation
- Semantic organization
"""

from .middleware import IntelligentMiddleware
from .chunking import SemanticChunker, ContextualChunker
from .contextualization import EmergentContextualizer
from .synthesis import MemorySynthesizer
from .curation import RecallCurator

__all__ = [
    "IntelligentMiddleware",
    "SemanticChunker", 
    "ContextualChunker",
    "EmergentContextualizer",
    "MemorySynthesizer",
    "RecallCurator"
]
