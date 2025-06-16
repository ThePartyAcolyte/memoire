"""Context storage operations."""

import json
import sqlite3
from datetime import datetime
from typing import Optional

from ...models import MemoryContext

def create_context(db_path, context: MemoryContext) -> str:
    """Create a new context."""
    import logging
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO contexts 
        (id, project_id, name, description, fragment_ids, 
         parent_context_id, child_context_ids, custom_fields, fragment_count, 
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        context.id, context.project_id, context.name,
        context.description, json.dumps(context.fragment_ids),
        context.parent_context_id, json.dumps(context.child_context_ids),
        json.dumps(context.custom_fields), context.fragment_count,
        context.created_at, context.updated_at
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Created context: {context.name} ({context.id})")
    return context.id

def get_context(db_path, context_id: str) -> Optional[MemoryContext]:
    """Get context by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contexts WHERE id = ?", (context_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return _row_to_context(row)

def list_contexts_by_project(db_path, project_id: str) -> list[MemoryContext]:
    """List all contexts for a project."""
    import logging
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM contexts WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    contexts = [_row_to_context(row) for row in rows]
    logger.debug(f"Found {len(contexts)} contexts for project {project_id}")
    return contexts


def get_contexts_by_fragment(db_path, fragment_id: str) -> list[MemoryContext]:
    """Get all contexts that contain a specific fragment."""
    import logging
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Search for contexts where fragment_ids JSON contains the fragment_id
    cursor.execute(
        "SELECT * FROM contexts WHERE json_extract(fragment_ids, '$') LIKE ?",
        (f'%"{fragment_id}"%',)
    )
    rows = cursor.fetchall()
    conn.close()
    
    contexts = [_row_to_context(row) for row in rows]
    logger.debug(f"Found {len(contexts)} contexts containing fragment {fragment_id}")
    return contexts


def update_context_fragments(db_path, context_id: str, fragment_ids: list[str]) -> bool:
    """Update the fragment list for a context."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE contexts 
            SET fragment_ids = ?, fragment_count = ?, updated_at = ?
            WHERE id = ?
        """, (
            json.dumps(fragment_ids),
            len(fragment_ids),
            datetime.now(),
            context_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Updated context {context_id} with {len(fragment_ids)} fragments")
        return success
        
    except Exception as e:
        logger.error(f"Failed to update context fragments: {e}")
        return False


def _row_to_context(row) -> MemoryContext:
    """Convert SQLite row to MemoryContext object."""
    return MemoryContext(
        id=row[0],
        project_id=row[1],
        name=row[2],
        description=row[3],
        fragment_ids=json.loads(row[4]),
        parent_context_id=row[5],
        child_context_ids=json.loads(row[6]),
        custom_fields=json.loads(row[7]),
        fragment_count=row[8],
        created_at=datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S.%f'),
        updated_at=datetime.strptime(row[10], '%Y-%m-%d %H:%M:%S.%f')
    )
