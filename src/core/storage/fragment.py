"""Fragment storage operations."""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from qdrant_client.http.models import PointStruct
from ...models import MemoryFragment

def store_fragment(db_path, qdrant_client, fragment: MemoryFragment, embedding: List[float]) -> str:
    """Store fragment in both SQLite and Qdrant."""
    from .db import get_or_create_collection
    import logging
    logger = logging.getLogger(__name__)
    
    # Store metadata in SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO fragments 
        (id, project_id, content, category, tags, source, 
         context_ids, anchor_ids, custom_fields, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fragment.id, fragment.project_id, fragment.content,
        fragment.category, json.dumps(fragment.tags), fragment.source,
        json.dumps(fragment.context_ids), json.dumps(fragment.anchor_ids),
        json.dumps(fragment.custom_fields), fragment.created_at, fragment.updated_at
    ))
    
    conn.commit()
    conn.close()
    
    # Store embedding in Qdrant
    collection_name = get_or_create_collection(qdrant_client, fragment.project_id)
    
    # Prepare payload for rich filtering capabilities
    payload = {
        "fragment_id": fragment.id,
        "project_id": fragment.project_id,
        "category": fragment.category,
        "tags": fragment.tags,
        "source": fragment.source,
        "content_preview": fragment.content[:200],  # For quick reference
        "created_at": fragment.created_at.isoformat(),
        **fragment.custom_fields  # Merge custom fields directly
    }
    
    point = PointStruct(
        id=fragment.id,
        vector=embedding,
        payload=payload
    )
    
    qdrant_client.upsert(
        collection_name=collection_name,
        points=[point]
    )
    
    logger.info(f"Stored fragment: {fragment.id} in project {fragment.project_id}")
    return fragment.id

def get_fragment(db_path, fragment_id: str) -> Optional[MemoryFragment]:
    """Get fragment by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM fragments WHERE id = ?", (fragment_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return _row_to_fragment(row)

def delete_fragment(db_path, qdrant_client, fragment_id: str) -> bool:
    """Delete fragment from both SQLite and Qdrant."""
    from .db import get_or_create_collection
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # First get the fragment to know which project/collection it belongs to
        fragment = get_fragment(db_path, fragment_id)
        if not fragment:
            logger.warning(f"Fragment {fragment_id} not found for deletion")
            return False
        
        # Delete from SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM fragments WHERE id = ?", (fragment_id,))
        sqlite_success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        # Delete from Qdrant
        collection_name = get_or_create_collection(qdrant_client, fragment.project_id)
        
        qdrant_client.delete(
            collection_name=collection_name,
            points_selector=[fragment_id]
        )
        
        if sqlite_success:
            logger.info(f"Successfully deleted fragment: {fragment_id}")
            return True
        else:
            logger.warning(f"Fragment {fragment_id} was not found in SQLite")
            return False
            
    except Exception as e:
        logger.error(f"Failed to delete fragment {fragment_id}: {e}")
        return False


def list_fragments_by_project(db_path, project_id: str, limit: int = 100) -> List[MemoryFragment]:
    """List fragments for a project."""
    import logging
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM fragments WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
        (project_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    fragments = [_row_to_fragment(row) for row in rows]
    logger.debug(f"Found {len(fragments)} fragments for project {project_id}")
    return fragments


def _row_to_fragment(row) -> MemoryFragment:
    """Convert SQLite row to MemoryFragment object."""
    return MemoryFragment(
        id=row[0],
        project_id=row[1],
        content=row[2],
        category=row[3] or "general",
        tags=json.loads(row[4]) if row[4] else [],
        source=row[5] or "user",
        context_ids=json.loads(row[6]) if row[6] else [],
        anchor_ids=json.loads(row[7]) if row[7] else [],
        custom_fields=json.loads(row[8]) if row[8] else {},
        created_at=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
        updated_at=datetime.fromisoformat(row[10]) if row[10] else datetime.now()
    )
