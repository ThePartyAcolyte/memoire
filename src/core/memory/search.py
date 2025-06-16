"""
Search operations for MnemoX memory system.

Handles semantic search, similarity detection, and intelligent fragment discovery.
"""

import logging
from typing import List, Optional

from ...models import SearchOptions, SearchResult, MemoryFragment
from ..storage import StorageManager
from ..embedding import EmbeddingService

logger = logging.getLogger(__name__)


async def search_memory(storage: StorageManager, embedding_service: EmbeddingService,
                       query: str, options: SearchOptions = None,
                       default_project_id: str = None) -> List[SearchResult]:
    """Search memory using semantic similarity and filters.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        query: Search query text
        options: Search configuration options
        default_project_id: Default project ID if none specified in options
        
    Returns:
        List of SearchResult objects sorted by relevance
        
    Raises:
        ValueError: If no project is specified and no default is available
    """
    if options is None:
        options = SearchOptions()
    
    # Use default project if none specified
    if not options.project_id and default_project_id:
        options.project_id = default_project_id
    
    if not options.project_id:
        raise ValueError("No project specified and no default project available")
    
    # Generate query embedding
    query_embedding = await embedding_service.generate_embedding(query)
    
    # Perform search
    results = storage.search_fragments(query_embedding, options)
    
    logger.info(f"Search returned {len(results)} results for query: {query[:50]}...")
    return results


async def find_similar_fragments(storage: StorageManager, embedding_service: EmbeddingService,
                                fragment_id: str, limit: int = 5) -> List[SearchResult]:
    """Find fragments similar to a given fragment.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        fragment_id: ID of the reference fragment
        limit: Maximum number of similar fragments to return
        
    Returns:
        List of SearchResult objects for similar fragments
        
    Raises:
        ValueError: If the reference fragment is not found
    """
    fragment = storage.get_fragment(fragment_id)
    if not fragment:
        raise ValueError(f"Fragment not found: {fragment_id}")
    
    # Use the fragment's content as the search query
    options = SearchOptions(
        project_id=fragment.project_id,
        max_results=limit + 1,  # +1 because we'll filter out the original
        similarity_threshold=0.3  # Lower threshold for similarity search
    )
    
    results = await search_memory(
        storage, embedding_service,
        fragment.content, options
    )
    
    # Filter out the original fragment
    similar_results = [r for r in results if r.fragment.id != fragment_id]
    
    return similar_results[:limit]


async def search_by_category(storage: StorageManager, embedding_service: EmbeddingService,
                            project_id: str, category: str,
                            query: str = "", limit: int = 20) -> List[SearchResult]:
    """Search fragments within a specific category.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        project_id: ID of the project to search in
        category: Category to filter by
        query: Optional semantic query (empty string for category-only search)
        limit: Maximum number of results to return
        
    Returns:
        List of SearchResult objects in the specified category
    """
    options = SearchOptions(
        project_id=project_id,
        max_results=limit,
        categories=[category],
        similarity_threshold=0.1 if query else 0.0  # Lower threshold for category search
    )
    
    # Use query if provided, otherwise use category name for semantic matching
    search_query = query if query else category
    
    return await search_memory(storage, embedding_service, search_query, options)


async def search_by_tags(storage: StorageManager, embedding_service: EmbeddingService,
                        project_id: str, tags: List[str],
                        query: str = "", limit: int = 20) -> List[SearchResult]:
    """Search fragments with specific tags.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        project_id: ID of the project to search in
        tags: List of tags to filter by
        query: Optional semantic query
        limit: Maximum number of results to return
        
    Returns:
        List of SearchResult objects with the specified tags
    """
    options = SearchOptions(
        project_id=project_id,
        max_results=limit,
        tags=tags,
        similarity_threshold=0.1 if query else 0.0
    )
    
    # Use query if provided, otherwise use tags for semantic matching
    search_query = query if query else " ".join(tags)
    
    return await search_memory(storage, embedding_service, search_query, options)


async def advanced_search(storage: StorageManager, embedding_service: EmbeddingService,
                         query: str, **filters) -> List[SearchResult]:
    """Perform advanced search with multiple filter options.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        query: Search query text
        **filters: Additional filter options (project_id, categories, tags, etc.)
        
    Returns:
        List of SearchResult objects matching the advanced criteria
    """
    options = SearchOptions(**filters)
    
    return await search_memory(storage, embedding_service, query, options)


# Export functions
__all__ = [
    "search_memory",
    "find_similar_fragments",
    "search_by_category", 
    "search_by_tags",
    "advanced_search"
]
