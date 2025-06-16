"""
MnemoX Memory Module - Modular semantic memory operations.

This module provides a clean, modular architecture for memory operations
while maintaining backward compatibility with the original MemoryService API.
"""

from .service import MemoryService

# Export the main service class for backward compatibility
__all__ = ["MemoryService"]
