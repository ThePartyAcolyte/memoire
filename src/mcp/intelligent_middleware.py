"""
Intelligent Middleware for MnemoX Lite - UPDATED to use intelligence modules.

This file maintains backward compatibility while delegating to the new intelligence layer.
"""

import logging
from typing import Dict, Any

# Import the new intelligence layer
from .intelligence import IntelligentMiddleware as NewIntelligentMiddleware

logger = logging.getLogger(__name__)


class IntelligentMiddleware:
    """
    Backward compatibility wrapper for the new intelligence layer.
    
    Maintains the same interface as before while using the new modular implementation.
    """
    
    def __init__(self, memory_service):
        self.memory = memory_service
        
        # Initialize the new intelligence layer
        self.intelligence = NewIntelligentMiddleware(memory_service)
        
        logger.info("IntelligentMiddleware initialized with new intelligence layer")
    
    def analyze_content(self, content: str, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method for content analysis - maintained for backward compatibility.
        
        This is called by cognitive_engine.py in the remember() method.
        """
        return self.intelligence.analyze_content(content, project_state)
    
    def synthesize_memory_response(self, query: str, fragments) -> Dict[str, Any]:
        """
        Legacy method for memory synthesis - maintained for backward compatibility.
        
        This is called by cognitive_engine.py in the recall() method.
        """
        return self.intelligence.synthesize_memory_response(query, fragments)
    
    # ==================== NEW ENHANCED METHODS ====================
    
    async def process_remember_enhanced(self, content: str, project_id: str, 
                                      context: str = None) -> Dict[str, Any]:
        """
        Enhanced remember processing with chunking and contextualization.
        
        This is the new recommended method for processing remember requests.
        """
        return await self.intelligence.process_remember_enhanced(content, project_id, context)
    
    async def process_recall_enhanced(self, query: str, project_id: str,
                                    focus: str = None) -> Dict[str, Any]:
        """
        Enhanced recall with context awareness and curation.
        
        This is the new recommended method for processing recall requests.
        """
        return await self.intelligence.process_recall_enhanced(query, project_id, focus)
    
    # ==================== ACCESS TO INTELLIGENCE MODULES ====================
    
    def get_intelligence(self):
        """Get access to the full intelligence layer."""
        return self.intelligence
    
    def get_chunker(self, type: str = "contextual"):
        """Get chunker for direct usage."""
        return self.intelligence.get_chunker(type)
    
    def get_contextualizer(self):
        """Get contextualizer for direct usage."""
        return self.intelligence.get_contextualizer()
    
    def get_synthesizer(self):
        """Get synthesizer for direct usage."""
        return self.intelligence.get_synthesizer()
    
    def get_curator(self):
        """Get curator for direct usage."""
        return self.intelligence.get_curator()


# Export for backward compatibility
__all__ = ["IntelligentMiddleware"]
