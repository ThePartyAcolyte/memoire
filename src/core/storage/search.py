"""Search operations for vector database."""

from typing import List, Tuple
from qdrant_client import models
from ...models import SearchOptions

def semantic_search(qdrant_client, query_embedding: List[float], options: SearchOptions) -> List[Tuple[str, float]]:
    """Perform semantic search using Qdrant."""
    from .db import get_or_create_collection
    
    if not options.project_id:
        raise ValueError("Project ID required for search")
    
    collection_name = get_or_create_collection(qdrant_client, options.project_id)
    
    # Build filter conditions using Qdrant's powerful filtering
    filter_conditions = []
    
    # Category filter
    if options.categories:
        filter_conditions.append(
            models.FieldCondition(
                key="category",
                match=models.MatchAny(any=options.categories)
            )
        )
    
    # Tags filter - any tag matches
    if options.tags:
        filter_conditions.append(
            models.FieldCondition(
                key="tags",
                match=models.MatchAny(any=options.tags)
            )
        )
    
    # Custom field filters
    if options.custom_field_filters:
        for field, value in options.custom_field_filters.items():
            filter_conditions.append(
                models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=value)
                )
            )
    
    # Combine all conditions with AND
    query_filter = models.Filter(
        must=filter_conditions
    ) if filter_conditions else None
    
    # Perform the search
    search_results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=options.max_results,
        score_threshold=options.similarity_threshold,  # Qdrant handles this natively
        with_payload=True,
        with_vectors=False  # Save bandwidth, we don't need vectors back
    )
    
    # Convert to our format
    results = []
    for hit in search_results:
        results.append((hit.id, hit.score))
    
    return results