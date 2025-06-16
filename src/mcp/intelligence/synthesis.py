"""
Memory synthesis capabilities for coherent response generation.

Handles synthesis of memory fragments into coherent explanations and responses.
"""

import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MemorySynthesizer:
    """Handles synthesis of memory fragments into coherent responses."""
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        
        # Hot-reloadable configuration
        from src.config import config
        self.config = config
        self.temperature = config.get("processing.temperature", 0.3)
        
        # Subscribe to config changes for hot reload
        config.add_observer(self._on_config_change)
        
        logger.info(f"MemorySynthesizer initialized with temperature: {self.temperature}")
    
    def _on_config_change(self, new_config):
        """Handle configuration changes for hot reload."""
        try:
            old_temp = self.temperature
            self.temperature = new_config.get("processing", {}).get("temperature", 0.3)
            
            if old_temp != self.temperature:
                logger.info(f"Hot reload: Synthesis temperature updated {old_temp:.2f} → {self.temperature:.2f}")
                
        except Exception as e:
            logger.error(f"Error during config hot reload in MemorySynthesizer: {e}")
    
    def synthesize_legacy(self, query: str, fragments) -> Dict[str, Any]:
        """
        Legacy synthesis method for backward compatibility.
        
        Maintains the same interface as the original intelligent_middleware.py
        """
        # Format fragments for analysis
        fragments_text = ""
        for i, fragment in enumerate(fragments, 1):
            fragments_text += f"\nFragment {i}:\n"
            fragments_text += f"Content: {fragment.fragment.content}\n"
            fragments_text += f"Category: {fragment.fragment.category}\n"
            fragments_text += f"Tags: {fragment.fragment.tags}\n"
            fragments_text += f"Similarity: {fragment.similarity:.3f}\n"
        
        # Create synthesis prompt (domain-agnostic)
        prompt = f"""You are a memory synthesis assistant. Your job is to organize and synthesize information, NOT to make decisions or solve problems.

QUERY: {query}

RETRIEVED FRAGMENTS:
{fragments_text}

SYNTHESIZE a coherent response that:
1. Directly addresses the query by organizing relevant information
2. Combines information from fragments into a unified view
3. Identifies relationships, patterns, and potential gaps
4. Maintains neutrality - organize info without making recommendations
5. Uses clear, domain-agnostic language suitable for any project type

RESPOND WITH JSON:
{{
    "synthesized_response": "A coherent explanation that organizes the retrieved information to address the query",
    "confidence": 0.8,
    "information_coverage": "complete|partial|sparse",
    "gaps": ["missing info 1", "missing info 2"],
    "patterns_identified": ["pattern 1", "pattern 2"],
    "fragments_relevance": {{"fragment_1": "high", "fragment_2": "medium", "fragment_3": "low"}}
}}

Focus on synthesis and organization, not problem-solving."""

        try:
            # Use Gemini 2.5 Flash for synthesis
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": self.temperature}  # Use hot-reloadable temperature
            )
            
            synthesis_text = response.text.strip()
            
            # Extract JSON from response
            if synthesis_text.startswith("```json"):
                synthesis_text = synthesis_text[7:-3].strip()
            elif synthesis_text.startswith("```"):
                synthesis_text = synthesis_text[3:-3].strip()
            
            synthesis = json.loads(synthesis_text)
            
            logger.info(f"Memory synthesis completed for query: {query[:50]}...")
            return synthesis
            
        except Exception as e:
            logger.error(f"Memory synthesis failed: {e}")
            # Fallback synthesis
            return {
                "synthesized_response": f"Found {len(fragments)} relevant fragments related to '{query}'. " +
                                    "Manual review recommended due to synthesis processing limitations.",
                "confidence": 0.3,
                "information_coverage": "partial",
                "gaps": ["synthesis processing error"],
                "patterns_identified": [],
                "fragments_relevance": {}
            }
    
    async def synthesize_contextual(self, query: str, fragments: List, 
                                   contexts: List = None) -> Dict[str, Any]:
        """
        Enhanced synthesis with context awareness.
        
        Args:
            query: Search query
            fragments: List of fragment results
            contexts: Optional list of relevant contexts
            
        Returns:
            Synthesis result with context-aware insights
        """
        # Format fragments with context information
        fragments_text = ""
        for i, fragment in enumerate(fragments, 1):
            fragments_text += f"\nFragment {i}:\n"
            fragments_text += f"Content: {fragment.fragment.content}\n"
            fragments_text += f"Category: {fragment.fragment.category}\n"
            
            # Include context information if available
            if hasattr(fragment.fragment, 'context_ids') and fragment.fragment.context_ids:
                fragments_text += f"Contexts: {fragment.fragment.context_ids}\n"
            
            fragments_text += f"Similarity: {fragment.similarity:.3f}\n"
        
        # Include context descriptions if provided
        context_info = ""
        if contexts:
            context_info = "\nRELEVANT CONTEXTS:\n"
            for ctx in contexts:
                context_info += f"- {getattr(ctx, 'name', 'Unknown')}: {getattr(ctx, 'description', 'No description')}\n"
        
        prompt = f"""You are an advanced memory synthesis assistant with context awareness.

QUERY: {query}

RETRIEVED FRAGMENTS:
{fragments_text}
{context_info}

SYNTHESIZE a coherent response that:
1. Directly addresses the query by organizing relevant information
2. Leverages context information to provide deeper insights
3. Identifies relationships between fragments across contexts
4. Highlights patterns and potential knowledge gaps
5. Maintains neutrality while providing comprehensive organization

RESPOND WITH JSON:
{{
    "synthesized_response": "A coherent, context-aware explanation",
    "confidence": 0.8,
    "information_coverage": "complete|partial|sparse",
    "gaps": ["missing info 1", "missing info 2"],
    "patterns_identified": ["pattern 1", "pattern 2"],
    "context_insights": ["insight about context relationships"],
    "fragments_relevance": {{"fragment_1": "high", "fragment_2": "medium"}},
    "recommended_contexts": ["context to explore further"]
}}

Focus on intelligent synthesis that leverages contextual relationships."""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": self.temperature}  # Use hot-reloadable temperature
            )
            
            synthesis_text = response.text.strip()
            synthesis_text = self._extract_json(synthesis_text)
            synthesis = json.loads(synthesis_text)
            
            # Add metadata about synthesis type
            synthesis["synthesis_type"] = "contextual"
            synthesis["contexts_used"] = len(contexts) if contexts else 0
            
            logger.info(f"Contextual synthesis completed for query: {query[:50]}...")
            return synthesis
            
        except Exception as e:
            logger.error(f"Contextual synthesis failed: {e}")
            # Fallback to legacy synthesis
            return self.synthesize_legacy(query, fragments)
    
    async def synthesize_with_curation_context(self, query: str, fragments: List,
                                              curated_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Synthesis that incorporates curation context.
        
        Used when fragments have been curated during recall to provide
        transparency about what was removed and why.
        """
        synthesis = await self.synthesize_contextual(query, fragments)
        
        # Add curation context if provided
        if curated_info:
            synthesis["curation_applied"] = True
            synthesis["fragments_removed"] = curated_info.get("fragments_removed", 0)
            synthesis["curation_reasoning"] = curated_info.get("reasoning", "")
        else:
            synthesis["curation_applied"] = False
        
        return synthesis
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from Gemini response."""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            return text[start:end].strip()
        return text
