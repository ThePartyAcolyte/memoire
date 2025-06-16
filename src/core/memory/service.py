"""
Memory service orchestrator for MnemoX Lite.

Main MemoryService class that coordinates all memory operations while maintaining
the same API as the original monolithic implementation.
"""

import logging
from typing import List, Dict, Any, Optional

from ...models import (
    Project, MemoryFragment, MemoryContext, CognitiveAnchor, 
    SearchOptions, SearchResult
)
from ..storage import StorageManager
from ..embedding import EmbeddingService

# Import modular functions
from . import projects
from . import fragments
from . import contexts
from . import anchors
from . import search
from . import analytics
from . import health

logger = logging.getLogger(__name__)


class MemoryService:
    """Core service for semantic memory operations.
    
    This orchestrator maintains the same API as the original monolithic implementation
    while delegating to specialized modules for better organization and maintainability.
    """
    
    def __init__(self, storage: StorageManager, embedding: EmbeddingService):
        self.storage = storage
        self.embedding = embedding
        self._default_project_id: Optional[str] = None
        
        logger.info("MemoryService initialized (modular architecture)")
    
    # ==================== PROJECT MANAGEMENT ====================
    
    async def create_project(self, name: str, description: str, 
                           system_prompt: str = "") -> str:
        """Create a new memory project with flexible schema."""
        project_id = await projects.create_project(
            self.storage, name, description, system_prompt
        )
        
        # Set as default if it's the first project
        if not self._default_project_id:
            self._default_project_id = project_id
        
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        return projects.get_project(self.storage, project_id)
    
    def list_projects(self) -> List[Project]:
        """List all projects."""
        return projects.list_projects(self.storage)
    
    def get_default_project_id(self) -> Optional[str]:
        """Get the default project ID."""
        return self._default_project_id
    
    def set_default_project(self, project_id: str):
        """Set the default project."""
        self._default_project_id = project_id
        logger.info(f"Set default project: {project_id}")
    
    # ==================== FRAGMENT OPERATIONS ====================
    
    async def store_fragment(self, project_id: str, content: str,
                           category: str = "general", tags: List[str] = None,
                           source: str = "user", custom_fields: Dict[str, Any] = None,
                           context_ids: List[str] = None, anchor_ids: List[str] = None) -> str:
        """Store a fragment of information with semantic embedding."""
        return await fragments.store_fragment(
            self.storage, self.embedding, project_id, content,
            category, tags, source, custom_fields, context_ids, anchor_ids
        )
    
    def get_fragment(self, fragment_id: str) -> Optional[MemoryFragment]:
        """Get fragment by ID."""
        return fragments.get_fragment(self.storage, fragment_id)
    
    # Fragment updates not supported - use delete + create for modifications
    
    def delete_fragment(self, fragment_id: str) -> bool:
        """Delete a fragment."""
        return self.storage.delete_fragment(fragment_id)
    
    def list_fragments_by_project(self, project_id: str, limit: int = None) -> List[MemoryFragment]:
        """List fragments for a project."""
        if limit is None:
            from src.config import config
            limit = config.get("search.max_results", 50)
            
        return self.storage.list_fragments_by_project(project_id, limit)
    
    # ==================== SEARCH OPERATIONS ====================
    
    async def search_memory(self, query: str, 
                          options: SearchOptions = None) -> List[SearchResult]:
        """Search memory using semantic similarity and filters."""
        if options is None:
            # Get default threshold from config
            from src.config import config
            threshold = config.get("search.similarity_threshold", 0.6)
            max_results = config.get("search.max_results", 50)
            
            options = SearchOptions(
                similarity_threshold=threshold,
                max_results=max_results
            )
            
        return await search.search_memory(
            self.storage, self.embedding, query, options, self._default_project_id
        )
    
    async def find_similar_fragments(self, fragment_id: str, 
                                   limit: int = None) -> List[SearchResult]:
        """Find fragments similar to a given fragment."""
        if limit is None:
            from src.config import config
            limit = config.get("search.max_results", 50) // 10  # Use 1/10th for similar fragments
            
        return await search.find_similar_fragments(
            self.storage, self.embedding, fragment_id, limit
        )
    
    # ==================== CONTEXT OPERATIONS ====================
    
    def create_context(self, project_id: str, name: str,
                      description: str = "", fragment_ids: List[str] = None,
                      custom_fields: Dict[str, Any] = None,
                      parent_context_id: str = None) -> str:
        """Create a new context for organizing fragments."""
        return contexts.create_context(
            self.storage, project_id, name, description,
            fragment_ids, custom_fields, parent_context_id
        )
    
    def get_context(self, context_id: str) -> Optional[MemoryContext]:
        """Get context by ID."""
        return contexts.get_context(self.storage, context_id)
    
    def list_contexts_by_project(self, project_id: str) -> List[MemoryContext]:
        """List all contexts for a project."""
        return self.storage.list_contexts_by_project(project_id)
    
    def get_contexts_by_fragment(self, fragment_id: str) -> List[MemoryContext]:
        """Get all contexts containing a specific fragment."""
        return self.storage.get_contexts_by_fragment(fragment_id)
    
    def add_fragment_to_context(self, context_id: str, fragment_id: str) -> bool:
        """Add a fragment to a context."""
        return contexts.add_fragment_to_context(self.storage, context_id, fragment_id)
    
    # ==================== ANCHOR OPERATIONS ====================
    
    def create_anchor(self, project_id: str, title: str,
                     description: str = "", priority: str = "medium",
                     fragment_ids: List[str] = None, context_ids: List[str] = None,
                     tags: List[str] = None, custom_fields: Dict[str, Any] = None) -> str:
        """Create a new cognitive anchor."""
        return anchors.create_anchor(
            self.storage, project_id, title, description,
            priority, fragment_ids, context_ids, tags, custom_fields
        )
    
    def get_anchor(self, anchor_id: str) -> Optional[CognitiveAnchor]:
        """Get anchor by ID."""
        return anchors.get_anchor(self.storage, anchor_id)
    
    def access_anchor(self, anchor_id: str):
        """Mark an anchor as accessed (updates access count and timestamp)."""
        return anchors.access_anchor(self.storage, anchor_id)
    
    # ==================== ANALYTICS AND INSIGHTS ====================
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a project."""
        return analytics.get_project_stats(self.storage, self.embedding, project_id)
    
    async def find_knowledge_gaps(self, project_id: str, threshold: float = None) -> List[str]:
        """Identify potential knowledge gaps in the memory."""
        if threshold is None:
            from src.config import config
            threshold = config.get("search.similarity_threshold", 0.6) / 2  # Use half of search threshold
            
        return await analytics.find_knowledge_gaps(self.storage, self.embedding, project_id, threshold)
    
    async def suggest_contexts(self, project_id: str) -> List[Dict[str, Any]]:
        """Suggest potential contexts based on fragment clustering."""
        return await analytics.suggest_contexts(self.storage, self.embedding, project_id)
    
    # ==================== HEALTH AND MAINTENANCE ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of memory service and dependencies."""
        return health.health_check(self.storage, self.embedding, self._default_project_id)
    
    def cleanup_old_cache(self):
        """Clean up old cache entries."""
        return health.cleanup_old_cache(self.embedding)


# Export main class
__all__ = ["MemoryService"]
