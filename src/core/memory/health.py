"""
Health and maintenance operations for MnemoX memory system.

Provides health checks, maintenance operations, and system monitoring.
"""

import logging
from typing import Dict, Any

from ..storage import StorageManager
from ..embedding import EmbeddingService

logger = logging.getLogger(__name__)


def health_check(storage: StorageManager, embedding_service: EmbeddingService,
                default_project_id: str = None) -> Dict[str, Any]:
    """Check health of memory service and dependencies.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        default_project_id: Default project ID if available
        
    Returns:
        Dictionary with health status of all components
    """
    health = {
        "memory_service": True,
        "embedding_service": True,
        "storage": storage.health_check(),
        "default_project": default_project_id,
        "cache_stats": embedding_service.get_cache_stats()
    }
    
    return health


def cleanup_old_cache(embedding_service: EmbeddingService) -> Dict[str, Any]:
    """Clean up old cache entries.
    
    Args:
        embedding_service: Embedding service instance
        
    Returns:
        Dictionary with cleanup results
    """
    # Get stats before cleanup
    before_stats = embedding_service.get_cache_stats()
    
    # Perform cleanup
    removed_entries = embedding_service.cleanup_cache()
    
    # Get stats after cleanup
    after_stats = embedding_service.get_cache_stats()
    
    logger.info(f"Cache cleanup: {removed_entries} expired entries removed")
    
    return {
        "removed_entries": removed_entries,
        "before_stats": before_stats,
        "after_stats": after_stats
    }


def clear_all_cache(embedding_service: EmbeddingService) -> Dict[str, Any]:
    """Clear all cache entries.
    
    Args:
        embedding_service: Embedding service instance
        
    Returns:
        Dictionary with clear results
    """
    # Get stats before clearing
    before_stats = embedding_service.get_cache_stats()
    
    # Clear cache
    embedding_service.clear_cache()
    
    # Get stats after clearing
    after_stats = embedding_service.get_cache_stats()
    
    logger.info("All cache entries cleared")
    
    return {
        "before_stats": before_stats,
        "after_stats": after_stats
    }


def optimize_storage(storage: StorageManager, project_id: str = None) -> Dict[str, Any]:
    """Optimize storage performance and cleanup.
    
    Args:
        storage: Storage manager instance
        project_id: Optional project ID to optimize (all projects if None)
        
    Returns:
        Dictionary with optimization results
        
    Raises:
        NotImplementedError: This functionality is not yet implemented
    """
    # TODO: Implement storage optimization
    # Could include SQLite VACUUM, Qdrant optimization, index rebuilding
    raise NotImplementedError("Storage optimization not yet implemented")


def backup_project(storage: StorageManager, project_id: str, 
                  backup_path: str) -> Dict[str, Any]:
    """Create a backup of a project.
    
    Args:
        storage: Storage manager instance
        project_id: ID of the project to backup
        backup_path: Path where backup should be stored
        
    Returns:
        Dictionary with backup results
        
    Raises:
        NotImplementedError: This functionality is not yet implemented
    """
    # TODO: Implement project backup
    # Should export SQLite data and Qdrant collections
    raise NotImplementedError("Project backup not yet implemented")


def restore_project(storage: StorageManager, backup_path: str,
                   new_project_id: str = None) -> Dict[str, Any]:
    """Restore a project from backup.
    
    Args:
        storage: Storage manager instance
        backup_path: Path to the backup file
        new_project_id: Optional new project ID (generates one if None)
        
    Returns:
        Dictionary with restore results
        
    Raises:
        NotImplementedError: This functionality is not yet implemented
    """
    # TODO: Implement project restore
    # Should import SQLite data and recreate Qdrant collections
    raise NotImplementedError("Project restore not yet implemented")


def validate_data_integrity(storage: StorageManager, project_id: str) -> Dict[str, Any]:
    """Validate data integrity for a project.
    
    Args:
        storage: Storage manager instance
        project_id: ID of the project to validate
        
    Returns:
        Dictionary with validation results
        
    Raises:
        NotImplementedError: This functionality is not yet implemented
    """
    # TODO: Implement data integrity validation
    # Should check:
    # - Fragment embeddings exist in Qdrant
    # - Context references are valid
    # - Anchor references are valid
    # - No orphaned data
    raise NotImplementedError("Data integrity validation not yet implemented")


def get_system_metrics(storage: StorageManager, embedding_service: EmbeddingService) -> Dict[str, Any]:
    """Get comprehensive system metrics.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        
    Returns:
        Dictionary with system metrics
    """
    metrics = {
        "storage_health": storage.health_check(),
        "cache_stats": embedding_service.get_cache_stats(),
        "embedding_provider": embedding_service.provider.__class__.__name__,
        "embedding_model": embedding_service.model,
        "embedding_dimension": embedding_service.dimension
    }
    
    return metrics


def maintenance_report(storage: StorageManager, embedding_service: EmbeddingService,
                      project_id: str = None) -> Dict[str, Any]:
    """Generate a comprehensive maintenance report.
    
    Args:
        storage: Storage manager instance
        embedding_service: Embedding service instance
        project_id: Optional project ID to focus on
        
    Returns:
        Dictionary with maintenance report
    """
    report = {
        "system_health": health_check(storage, embedding_service),
        "system_metrics": get_system_metrics(storage, embedding_service),
        "recommendations": []
    }
    
    # Add project-specific stats if requested
    if project_id:
        try:
            report["project_stats"] = storage.get_stats(project_id)
        except Exception as e:
            logger.error(f"Failed to get project stats for {project_id}: {e}")
            report["project_stats"] = {"error": str(e)}
    
    # Generate basic recommendations
    cache_stats = embedding_service.get_cache_stats()
    if cache_stats.get("hit_rate", 0) < 0.5:
        report["recommendations"].append("Cache hit rate is low - consider reviewing usage patterns")
    
    return report


# Export functions
__all__ = [
    "health_check",
    "cleanup_old_cache",
    "clear_all_cache",
    "optimize_storage",
    "backup_project",
    "restore_project",
    "validate_data_integrity",
    "get_system_metrics",
    "maintenance_report"
]
