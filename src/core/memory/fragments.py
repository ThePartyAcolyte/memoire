"""Fragment operations for Memoire memory system.

Handles CRUD operations for cognitive fragments - the basic units of semantic memory.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.logging_config import get_logger
from ...models import MemoryFragment
from ..storage import StorageManager
from ..embedding import EmbeddingService
from ...config import config

logger = get_logger('memoire.mcp.memory')


async def store_fragment(storage: StorageManager, embedding_service: EmbeddingService,
                        project_id: str, content: str,
                        category: str = "general", tags: List[str] = None,
                        source: str = "user", custom_fields: Dict[str, Any] = None,
                        context_ids: List[str] = None, anchor_ids: List[str] = None) -> str:
    """Store a fragment of information with semantic embedding.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        project_id: ID of the project this fragment belongs to
        content: Text content of the fragment
        category: Category for organization (default: "general")
        tags: List of tags for the fragment
        source: Source of the fragment (default: "user")
        custom_fields: Additional metadata fields
        context_ids: List of context IDs this fragment belongs to
        anchor_ids: List of anchor IDs that reference this fragment
        
    Returns:
        Fragment ID of the stored fragment
        
    Raises:
        ValueError: If content is empty or invalid
    """
    if tags is None: tags = []
    if custom_fields is None: custom_fields = {}
    if context_ids is None: context_ids = []
    if anchor_ids is None: anchor_ids = []
    
    # Validate inputs
    if not content or not content.strip():
        logger.error("store_fragment called with empty content")
        raise ValueError("Fragment content cannot be empty")
    
    max_content_length = config.get("fragment_limits.max_content_length", 10000)
    if len(content) > max_content_length:
        logger.warning(f"Fragment content is very long ({len(content)} chars), truncating to {max_content_length}")
        content = content[:max_content_length] # Truncate content
    
    # Generate embedding
    embedding = await embedding_service.generate_embedding(content, task_type='RETRIEVAL_DOCUMENT')

    # Create fragment object
    fragment_id = str(uuid.uuid4())
    fragment = MemoryFragment(
        id=fragment_id,
        project_id=project_id,
        content=content,
        category=category,
        tags=tags,
        source=source,
        context_ids=context_ids,
        anchor_ids=anchor_ids,
        custom_fields=custom_fields,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Store in database
    stored_id = storage.store_fragment(fragment, embedding)
    
    logger.info(f"Stored fragment: {stored_id} in project {project_id}")
    return stored_id


def get_fragment(storage: StorageManager, fragment_id: str) -> Optional[MemoryFragment]:
    """Get fragment by ID.
    
    Args:
        storage: Storage manager instance
        fragment_id: ID of the fragment to retrieve
        
    Returns:
        MemoryFragment object if found, None otherwise
    """
    return storage.get_fragment(fragment_id)


async def delete_fragments(storage: StorageManager, fragment_ids: List[str], project_id: str) -> bool:
    """Delete multiple fragments by their IDs."""
    try:
        success = storage.delete_fragments(fragment_ids, project_id)
        logger.info(f"Deleted {len(fragment_ids)} fragments from project {project_id}")
        return success
    except Exception as e:
        logger.error(f"Error deleting fragments: {e}", exc_info=True)
        return False


# Fragment update functionality removed - use deletion + creation instead
# Fragment deletion moved to storage layer and implemented
# Fragment listing implemented in storage layer


def validate_fragment_content(content: str, max_length: int = 10000) -> bool:
    """Validate fragment content meets requirements.
    
    Args:
        content: Fragment content to validate
        max_length: Maximum allowed content length
        
    Returns:
        True if content is valid
        
    Raises:
        ValueError: If content is invalid
    """
    if not content or not content.strip():
        logger.error("Validation failed: content is empty")
        raise ValueError("Fragment content cannot be empty")
    
    if len(content) > max_length:
        logger.error(f"Validation failed: content length {len(content)} exceeds max_length {max_length}")
        raise ValueError(f"Fragment content too long: {len(content)} > {max_length}")
    
    return True


# Export functions
__all__ = [
    "store_fragment",
    "get_fragment", 
    "validate_fragment_content"
]
