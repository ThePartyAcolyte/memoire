"""
Intelligent Middleware - Main orchestrator for cognitive processing.

Coordinates chunking, contextualization, synthesis, and curation.
Maintains the same interface as the original but delegates to specialized modules.
"""

import logging
import os
from typing import Dict, Any, List

from .chunking import SemanticChunker, ContextualChunker
from .contextualization import EmergentContextualizer
from .synthesis import MemorySynthesizer
from .curation import RecallCurator

logger = logging.getLogger(__name__)


class IntelligentMiddleware:
    """
    Main orchestrator for cognitive processing in MnemoX.
    
    Maintains backward compatibility while delegating to specialized modules.
    """
    
    def __init__(self, memory_service):
        self.memory = memory_service
        
        # Get API key from config or env var
        from ...config import config
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        # Initialize Gemini client
        try:
            from google import genai
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            logger.info("Gemini 2.5 Flash client initialized")
        except ImportError:
            raise ImportError("google-genai package required: pip install google-genai")
        
        # Initialize specialized modules
        self.semantic_chunker = SemanticChunker(self.gemini_client)
        self.contextual_chunker = ContextualChunker(self.gemini_client, memory_service)
        self.contextualizer = EmergentContextualizer(memory_service, self.gemini_client)
        self.synthesizer = MemorySynthesizer(self.gemini_client)
        self.curator = RecallCurator(self.gemini_client, memory_service)
        
        logger.info("Intelligence modules initialized")
    
    # ==================== BACKWARD COMPATIBILITY ====================
    
    def analyze_content(self, content: str, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method for content analysis.
        
        Maintained for backward compatibility with existing cognitive_engine.py
        """
        return self.semantic_chunker.analyze_content_legacy(content, project_state)
    
    def synthesize_memory_response(self, query: str, fragments) -> Dict[str, Any]:
        """
        Legacy method for memory synthesis.
        
        Maintained for backward compatibility with existing cognitive_engine.py
        """
        return self.synthesizer.synthesize_legacy(query, fragments)
    
    # ==================== NEW ENHANCED INTERFACE ====================
    
    async def process_remember_enhanced(self, content: str, project_id: str, 
                                      context: str = None) -> Dict[str, Any]:
        """
        Enhanced remember processing with chunking and contextualization.
        
        Args:
            content: Content to remember
            project_id: Project ID
            context: Optional context hint
            
        Returns:
            Processing result with fragments created
        """
        try:
            # Use contextual chunker for intelligent fragmentation
            fragments = await self.contextualizer.process_content(content, project_id)
            
            return {
                "success": True,
                "fragments_created": len(fragments),
                "fragment_ids": [f.id for f in fragments],
                "contexts_used": self._extract_contexts_used(fragments),
                "message": f"Content processed into {len(fragments)} contextualized fragments"
            }
            
        except Exception as e:
            logger.error(f"Enhanced remember processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process content with enhanced intelligence"
            }
    
    async def process_recall_enhanced(self, query: str, project_id: str,
                                    focus: str = None) -> Dict[str, Any]:
        """
        Enhanced recall with context awareness and curation.
        
        Args:
            query: Search query
            project_id: Project ID  
            focus: Optional focus area
            
        Returns:
            Enhanced recall result with curation applied
        """
        try:
            # Use curator for enhanced recall with cleanup
            return await self.curator.curated_recall(query, project_id, focus)
            
        except Exception as e:
            logger.error(f"Enhanced recall processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process recall with enhanced intelligence"
            }
    
    def _extract_contexts_used(self, fragments: List) -> List[str]:
        """Extract unique contexts used across fragments."""
        contexts = set()
        for fragment in fragments:
            if hasattr(fragment, 'context_ids'):
                contexts.update(fragment.context_ids)
        return list(contexts)
    
    # ==================== MODULE ACCESS ====================
    
    def get_chunker(self, type: str = "contextual"):
        """Get chunker instance for direct usage."""
        if type == "semantic":
            return self.semantic_chunker
        elif type == "contextual":
            return self.contextual_chunker
        else:
            raise ValueError(f"Unknown chunker type: {type}")
    
    def get_contextualizer(self):
        """Get contextualizer instance."""
        return self.contextualizer
    
    def get_synthesizer(self):
        """Get synthesizer instance.""" 
        return self.synthesizer
    
    def get_curator(self):
        """Get curator instance."""
        return self.curator
