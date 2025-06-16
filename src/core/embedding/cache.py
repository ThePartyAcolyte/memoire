"""
Cache management for embeddings.

Handles in-memory caching of embeddings to avoid duplicate API calls.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """In-memory cache for embeddings with TTL support."""
    
    def __init__(self, ttl_hours: int = 24):
        """Initialize cache with specified TTL.
        
        Args:
            ttl_hours: Time to live for cache entries in hours
        """
        self._cache: Dict[str, List[float]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.ttl = timedelta(hours=ttl_hours)
        
        logger.info(f"EmbeddingCache initialized with {ttl_hours}h TTL")
    
    def _generate_key(self, text: str, model: str) -> str:
        """Generate cache key for text and model combination."""
        combined = f"{model}:{text}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _is_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if key not in self._timestamps:
            return False
        
        age = datetime.now() - self._timestamps[key]
        return age < self.ttl
    
    def get(self, text: str, model: str) -> Optional[List[float]]:
        """Get embedding from cache if valid.
        
        Args:
            text: Text that was embedded
            model: Model used for embedding
            
        Returns:
            Cached embedding vector or None if not found/expired
        """
        key = self._generate_key(text, model)
        
        if key in self._cache and self._is_valid(key):
            logger.debug(f"Cache hit for text: {text[:50]}...")
            return self._cache[key]
        
        # Clean up expired entry if it exists
        if key in self._cache:
            self._remove(key)
        
        return None
    
    def set(self, text: str, model: str, embedding: List[float]) -> None:
        """Store embedding in cache.
        
        Args:
            text: Text that was embedded
            model: Model used for embedding
            embedding: Embedding vector to cache
        """
        key = self._generate_key(text, model)
        self._cache[key] = embedding
        self._timestamps[key] = datetime.now()
        
        logger.debug(f"Cached embedding for text: {text[:50]}...")
    
    def _remove(self, key: str) -> None:
        """Remove entry from cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        cleared_count = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        
        logger.info(f"Cache cleared: {cleared_count} entries removed")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if now - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            self._remove(key)
        
        if expired_keys:
            logger.info(f"Cache cleanup: {len(expired_keys)} expired entries removed")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        now = datetime.now()
        valid_entries = sum(
            1 for timestamp in self._timestamps.values()
            if now - timestamp < self.ttl
        )
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._cache) - valid_entries,
            "hit_ratio": valid_entries / max(len(self._cache), 1),
            "ttl_hours": self.ttl.total_seconds() / 3600
        }
