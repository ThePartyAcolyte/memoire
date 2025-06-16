"""Anchor storage operations."""

import json
import sqlite3
from datetime import datetime
from typing import Optional

from ...models import CognitiveAnchor

def create_anchor(db_path, anchor: CognitiveAnchor) -> str:
    """Create a new cognitive anchor."""
    import logging
    logger = logging.getLogger(__name__)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO anchors 
        (id, project_id, title, description, priority, 
         fragment_ids, context_ids, tags, access_count, custom_fields,
         created_at, updated_at, last_accessed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        anchor.id, anchor.project_id, anchor.title,
        anchor.description, anchor.priority, json.dumps(anchor.fragment_ids),
        json.dumps(anchor.context_ids), json.dumps(anchor.tags),
        anchor.access_count, json.dumps(anchor.custom_fields),
        anchor.created_at, anchor.updated_at, anchor.last_accessed
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Created anchor: {anchor.title} ({anchor.id})")
    return anchor.id

def get_anchor(db_path, anchor_id: str) -> Optional[CognitiveAnchor]:
    """Get anchor by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM anchors WHERE id = ?", (anchor_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return _row_to_anchor(row)

def _row_to_anchor(row) -> CognitiveAnchor:
    """Convert SQLite row to CognitiveAnchor object."""
    return CognitiveAnchor(
        id=row[0],
        project_id=row[1],
        title=row[2],
        description=row[3] or "",
        priority=row[4] or "medium",
        fragment_ids=json.loads(row[5]) if row[5] else [],
        context_ids=json.loads(row[6]) if row[6] else [],
        tags=json.loads(row[7]) if row[7] else [],
        access_count=row[8] or 0,
        custom_fields=json.loads(row[9]) if row[9] else {},
        created_at=datetime.fromisoformat(row[10]) if row[10] else datetime.now(),
        updated_at=datetime.fromisoformat(row[11]) if row[11] else datetime.now(),
        last_accessed=datetime.fromisoformat(row[12]) if row[12] else datetime.now()
    )
