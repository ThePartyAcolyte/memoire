"""
Emergent contextualization for intelligent memory organization.

Handles context resolution, creation, and fragment multi-context assignment.
"""

import logging
from typing import List, Dict, Any, Optional
from ...models import MemoryFragment, MemoryContext
from .chunking import ContextualChunker

logger = logging.getLogger(__name__)


class EmergentContextualizer:
    """
    Manages emergent contextualization based on content patterns.
    
    Coordinates chunking and context resolution to create multi-context fragments.
    """
    
    def __init__(self, memory_service, gemini_client):
        self.memory_service = memory_service
        self.gemini_client = gemini_client
        self.chunker = ContextualChunker(gemini_client, memory_service)
        self.context_resolver = ContextResolver(memory_service, gemini_client)
    
    async def process_content(self, content: str, project_id: str) -> List[MemoryFragment]:
        """
        Process content with emergent contextualization.
        
        Args:
            content: Content to process
            project_id: Project ID
            
        Returns:
            List of created MemoryFragment objects with context assignments
        """
        logger.info(f"Processing content with emergent contextualization for project {project_id}")
        
        # 1. Perform context-aware chunking
        chunks = await self.chunker.chunk_with_context_awareness(content, project_id)
        
        if not chunks:
            logger.warning("No chunks produced from content")
            return []
        
        # 2. Create fragments for each chunk with context resolution
        fragments = []
        for chunk_data in chunks:
            fragment = await self._create_contextualized_fragment(chunk_data, project_id)
            if fragment:
                fragments.append(fragment)
        
        logger.info(f"Created {len(fragments)} contextualized fragments")
        return fragments
    
    async def _create_contextualized_fragment(self, chunk_data: Dict[str, Any], 
                                            project_id: str) -> MemoryFragment:
        """Create a fragment with resolved contexts."""
        
        try:
            # Resolve context names to IDs
            context_names = chunk_data.get("suggested_contexts", ["general"])
            context_ids = await self.context_resolver.resolve_contexts(
                context_names, project_id, chunk_data
            )
            
            # Prepare custom fields with rich metadata
            custom_fields = {
                "semantic_summary": chunk_data.get("semantic_summary", ""),
                "key_concepts": chunk_data.get("key_concepts", []),
                "context_reasoning": chunk_data.get("context_reasoning", ""),
                "context_confidence": chunk_data.get("context_confidence", 0.5),
                "chunk_type": "emergent_contextual",
                "word_count": chunk_data.get("word_count", 0)
            }
            
            # Store fragment through memory service
            fragment_id = await self.memory_service.store_fragment(
                project_id=project_id,
                content=chunk_data["content"],
                category="contextualized",
                source="emergent_chunking",
                context_ids=context_ids,
                custom_fields=custom_fields
            )
            
            # Create fragment object for return
            fragment = MemoryFragment(
                id=fragment_id,
                project_id=project_id,
                content=chunk_data["content"],
                category="contextualized",
                context_ids=context_ids,
                custom_fields=custom_fields,
                source="emergent_chunking"
            )
            
            logger.debug(f"Created fragment {fragment_id} in contexts: {context_names}")
            return fragment
            
        except Exception as e:
            logger.error(f"Failed to create contextualized fragment: {e}")
            return None


class ContextResolver:
    """Resolves context names to IDs and manages context creation."""
    
    def __init__(self, memory_service, gemini_client):
        self.memory_service = memory_service
        self.gemini_client = gemini_client
        self._context_cache = {}  # Cache contexts by project
    
    async def resolve_contexts(self, context_names: List[str], project_id: str, 
                              chunk_data: Dict[str, Any]) -> List[str]:
        """
        Resolve context names to context IDs, creating new ones if needed.
        
        Args:
            context_names: List of context names from chunking
            project_id: Project ID
            chunk_data: Chunk information for context creation
            
        Returns:
            List of context IDs
        """
        existing_contexts = await self._get_cached_contexts(project_id)
        context_ids = []
        
        for context_name in context_names:
            context_id = await self._resolve_single_context(
                context_name, project_id, existing_contexts, chunk_data
            )
            context_ids.append(context_id)
        
        return context_ids
    
    async def _resolve_single_context(self, context_name: str, project_id: str,
                                     existing_contexts: List[MemoryContext],
                                     chunk_data: Dict[str, Any]) -> str:
        """Resolve a single context name to ID."""
        
        # Try to find existing context with fuzzy matching
        for ctx in existing_contexts:
            if self._contexts_match(context_name, ctx.name):
                logger.debug(f"Matched existing context: {context_name} -> {ctx.name}")
                return ctx.id
        
        # Create new context
        context_id = await self._create_new_context(context_name, project_id, chunk_data)
        
        # Update cache
        new_context = MemoryContext(
            id=context_id,
            project_id=project_id,
            name=context_name,
            description=""  # Will be set during creation
        )
        existing_contexts.append(new_context)
        
        return context_id
    
    def _contexts_match(self, name1: str, name2: str) -> bool:
        """Determine if two context names are equivalent using fuzzy matching."""
        n1 = self._normalize_context_name(name1)
        n2 = self._normalize_context_name(name2)
        
        # Exact match
        if n1 == n2:
            return True
        
        # Inclusion match
        if n1 in n2 or n2 in n1:
            return True
        
        # Similar words match (50% overlap threshold)
        words1 = set(n1.split())
        words2 = set(n2.split())
        overlap = len(words1.intersection(words2))
        min_words = min(len(words1), len(words2))
        
        return overlap / min_words >= 0.5 if min_words > 0 else False
    
    def _normalize_context_name(self, name: str) -> str:
        """Normalize context name for comparison."""
        return name.lower().replace("_", " ").replace("-", " ").strip()
    
    async def _create_new_context(self, context_name: str, project_id: str,
                                 chunk_data: Dict[str, Any]) -> str:
        """Create a new context based on the chunk that suggested it."""
        
        description = await self._generate_context_description(context_name, chunk_data)
        
        context_id = self.memory_service.create_context(
            project_id=project_id,
            name=context_name,
            description=description,
            custom_fields={
                "created_from_chunk": True,
                "initial_concepts": chunk_data.get("key_concepts", []),
                "creation_reasoning": chunk_data.get("context_reasoning", ""),
                "emergent": True
            }
        )
        
        logger.info(f"Created new emergent context: {context_name} ({context_id})")
        return context_id
    
    async def _generate_context_description(self, context_name: str, 
                                           chunk_data: Dict[str, Any]) -> str:
        """Generate description for new context."""
        
        prompt = f"""
        Se ha identificado un nuevo contexto en el proyecto: "{context_name}"
        
        FRAGMENTO QUE SUGIERE ESTE CONTEXTO:
        {chunk_data.get("content", "")}
        
        CONCEPTOS CLAVE: {chunk_data.get("key_concepts", [])}
        RAZONAMIENTO: {chunk_data.get("context_reasoning", "")}
        
        Genera una descripción concisa (2-3 frases) que explique qué tipo de 
        información pertenece a este contexto.
        
        RESPONDE SOLO LA DESCRIPCIÓN (sin formato, texto plano):
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=prompt,
                config={"temperature": 0.2}
            )
            
            description = response.text.strip()
            # Clean up formatting
            description = description.replace('"', '').replace("'", "")
            return description
            
        except Exception as e:
            logger.error(f"Failed to generate context description: {e}")
            # Fallback description
            concepts = chunk_data.get("key_concepts", [])
            return f"Contexto que agrupa información relacionada con {', '.join(concepts[:3])}."
    
    async def _get_cached_contexts(self, project_id: str) -> List[MemoryContext]:
        """Get contexts for project with caching."""
        
        if project_id not in self._context_cache:
            # Use real context retrieval from memory service
            try:
                contexts = self.memory_service.list_contexts_by_project(project_id)
                self._context_cache[project_id] = contexts
                logger.info(f"Cached {len(contexts)} contexts for project {project_id}")
            except Exception as e:
                logger.error(f"Failed to retrieve contexts for caching: {e}")
                self._context_cache[project_id] = []
        
        return self._context_cache[project_id]
    
    def clear_cache(self, project_id: Optional[str] = None):
        """Clear context cache for a project or all projects."""
        if project_id:
            self._context_cache.pop(project_id, None)
        else:
            self._context_cache.clear()
