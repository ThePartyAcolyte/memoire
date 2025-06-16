"""Utility functions for storage operations."""

import sqlite3
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_stats(db_path, qdrant_client, project_id: str) -> Dict[str, int]:
    """Get statistics for a project."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Count fragments
    cursor.execute("SELECT COUNT(*) FROM fragments WHERE project_id = ?", (project_id,))
    stats["fragments"] = cursor.fetchone()[0]
    
    # Count contexts
    cursor.execute("SELECT COUNT(*) FROM contexts WHERE project_id = ?", (project_id,))
    stats["contexts"] = cursor.fetchone()[0]
    
    # Count anchors
    cursor.execute("SELECT COUNT(*) FROM anchors WHERE project_id = ?", (project_id,))
    stats["anchors"] = cursor.fetchone()[0]
    
    conn.close()
    
    # Count vectors in Qdrant
    try:
        collection_name = f"project_{project_id.replace('-', '_')}"
        collection_info = qdrant_client.get_collection(collection_name)
        stats["vectors"] = collection_info.points_count
    except Exception:
        stats["vectors"] = 0
    
    return stats

def health_check(db_path, qdrant_client) -> Dict[str, Any]:
    """Check health of both storage systems."""
    health = {
        "sqlite": False,
        "qdrant": False,
        "collections": 0,
        "total_points": 0
    }
    
    # Check SQLite
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        health["sqlite"] = True
        conn.close()
    except Exception as e:
        logger.error(f"SQLite health check failed: {e}")
    
    # Check Qdrant
    try:
        collections = qdrant_client.get_collections()
        health["qdrant"] = True
        health["collections"] = len(collections.collections)
        
        # Count total points across all collections
        total_points = 0
        for collection in collections.collections:
            info = qdrant_client.get_collection(collection.name)
            total_points += info.points_count
        health["total_points"] = total_points
        
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
    
    return health