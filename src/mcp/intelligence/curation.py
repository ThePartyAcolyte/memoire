"""
Recall curation for memory cleanup and conflict resolution.

Implements curation during recall to remove redundancies and resolve conflicts.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from ...models import SearchResult, SearchOptions

logger = logging.getLogger(__name__)


class RecallCurator:
    """Handles curation during recall to maintain memory coherence."""
    
    def __init__(self, gemini_client, memory_service):
        self.gemini_client = gemini_client
        self.memory_service = memory_service
    
    async def curated_recall(self, query: str, project_id: str, 
                           focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced recall with automatic curation.
        
        Args:
            query: Search query
            project_id: Project ID
            focus: Optional focus area
            
        Returns:
            Recall result with curation applied
        """
        logger.info(f"Curated recall for query: {query[:50]}...")
        
        # 1. Perform initial search
        search_results = await self._perform_initial_search(query, project_id)
        
        if not search_results:
            return {
                "success": True,
                "response": f"No encontré información relacionada con '{query}'. ¿Te gustaría que recuerde algo sobre este tema?",
                "confidence": 0.0,
                "coverage": "none",
                "fragments_found": 0,
                "curation_applied": False
            }
        
        # 2. Apply curation if multiple results
        curated_results, curation_info = await self._curate_search_results(query, search_results)
        
        # 3. Synthesize response with curation context
        from .synthesis import MemorySynthesizer
        synthesizer = MemorySynthesizer(self.gemini_client)
        
        synthesis = await synthesizer.synthesize_with_curation_context(
            query, curated_results, curation_info
        )
        
        # 4. Format final response
        return {
            "success": True,
            "response": synthesis.get("synthesized_response", "Unable to synthesize response"),
            "confidence": synthesis.get("confidence", 0.5),
            "coverage": synthesis.get("information_coverage", "partial"),
            "fragments_found": len(search_results),
            "fragments_after_curation": len(curated_results),
            "curation_applied": curation_info is not None,
            "curation_reasoning": curation_info.get("reasoning", "") if curation_info else "",
            "insights": {
                "patterns": synthesis.get("patterns_identified", []),
                "knowledge_gaps": synthesis.get("gaps", []),
                "context_insights": synthesis.get("context_insights", [])
            }
        }
    
    async def _perform_initial_search(self, query: str, project_id: str) -> List[SearchResult]:
        """Perform initial semantic search with configurable threshold."""
        
        # Use configured curation search threshold
        from ...config import config
        search_threshold = config.get("intelligence.curation_search_threshold", 0.4)
        max_results = config.get("search.max_results", 50)
        
        search_options = SearchOptions(
            project_id=project_id,
            max_results=max_results,
            similarity_threshold=search_threshold
        )
        
        # Use memory service directly instead of importing (avoids circular imports)
        return await self.memory_service.search_memory(query, search_options)
    
    async def _curate_search_results(self, query: str, 
                                   results: List[SearchResult]) -> tuple[List[SearchResult], Optional[Dict[str, Any]]]:
        """
        Apply curation to search results to remove conflicts and redundancies.
        
        Returns:
            Tuple of (curated_results, curation_info)
        """
        if len(results) <= 1:
            # No curation needed for single result
            return results, None
        
        # Format results for Gemini analysis
        results_text = ""
        for i, result in enumerate(results):
            results_text += f"\n[ID: {result.fragment.id}] [Created: {result.fragment.created_at}] [Similarity: {result.similarity:.3f}]\n"
            results_text += f"Content: {result.fragment.content}\n"
            
            # Include context information if available
            if result.fragment.context_ids:
                results_text += f"Contexts: {result.fragment.context_ids}\n"
            
            # Include custom fields for additional context
            if result.fragment.custom_fields:
                key_concepts = result.fragment.custom_fields.get("key_concepts", [])
                if key_concepts:
                    results_text += f"Key concepts: {key_concepts}\n"
        
        prompt = f"""
        QUERY: {query}
        
        FRAGMENTOS ENCONTRADOS:
        {results_text}
        
        TAREA: Curar memoria eliminando redundancias y conflictos
        
        REGLAS ESTRICTAS:
        1. Si hay información CONTRADICTORIA: mantener solo la más reciente
        2. Si hay información REDUNDANTE: marcar duplicados para eliminación  
        3. Si hay información COMPLEMENTARIA: mantener todo
        4. En caso de DUDA: mantener todo (ser conservador)
        
        CRITERIOS:
        - Fragmentos muy similares (>90% overlap semántico) → eliminar el más antiguo
        - Fragmentos que se contradicen directamente → mantener el más reciente
        - Fragmentos que aportan perspectivas diferentes → mantener ambos
        
        RESPONDE JSON:
        {{
            "fragments_to_keep": ["id1", "id2", "id3"],
            "fragments_to_delete": ["id4", "id5"],
            "reasoning": "explicación detallada de por qué se eliminaron ciertos fragmentos",
            "conflicts_detected": true|false,
            "redundancies_detected": true|false
        }}
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": 0.2}  # Low temperature for consistent decisions
            )
            
            curation_text = response.text.strip()
            curation_text = self._extract_json(curation_text)
            curation_result = json.loads(curation_text)
            
            # Apply curation decisions
            keep_ids = set(curation_result.get("fragments_to_keep", []))
            delete_ids = set(curation_result.get("fragments_to_delete", []))
            
            # Filter results
            curated_results = [r for r in results if r.fragment.id in keep_ids]
            
            # Actually delete the marked fragments
            if delete_ids:
                await self._delete_fragments_silently(list(delete_ids))
                
                curation_info = {
                    "fragments_removed": len(delete_ids),
                    "reasoning": curation_result.get("reasoning", ""),
                    "conflicts_detected": curation_result.get("conflicts_detected", False),
                    "redundancies_detected": curation_result.get("redundancies_detected", False)
                }
                
                logger.info(f"Curation removed {len(delete_ids)} fragments: {curation_result.get('reasoning', '')}")
                return curated_results, curation_info
            else:
                # No curation needed
                return results, None
                
        except Exception as e:
            logger.error(f"Curation failed: {e}")
            # Return original results if curation fails
            return results, None
    
    async def _delete_fragments_silently(self, fragment_ids: List[str]):
        """Delete fragments silently during curation."""
        
        deleted_count = 0
        
        try:
            # Actually delete fragments using real implementation
            for fragment_id in fragment_ids:
                success = self.memory_service.delete_fragment(fragment_id)
                if success:
                    deleted_count += 1
                else:
                    logger.warning(f"Failed to delete fragment: {fragment_id}")
            
            logger.info(f"Successfully deleted {deleted_count}/{len(fragment_ids)} fragments during curation")
            
        except Exception as e:
            logger.error(f"Failed to delete fragments during curation: {e}")
            logger.info(f"Managed to delete {deleted_count} fragments before error")
    
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
