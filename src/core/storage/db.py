"""Database initialization and common operations."""

import sqlite3
import logging
from pathlib import Path
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

logger = logging.getLogger(__name__)

def init_sqlite(db_path):
    """Create SQLite tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    cursor = conn.cursor()
    
    # Projects table - simplified schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Fragments table - simplified schema (metadata only, embeddings in Qdrant)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fragments (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            tags TEXT,  -- JSON array
            source TEXT DEFAULT 'user',
            context_ids TEXT,  -- JSON array
            anchor_ids TEXT,   -- JSON array
            custom_fields TEXT,  -- JSON object
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    """)
    
    # Contexts table - simplified schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contexts (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            fragment_ids TEXT,  -- JSON array
            parent_context_id TEXT,
            child_context_ids TEXT,  -- JSON array
            custom_fields TEXT,  -- JSON object
            fragment_count INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            FOREIGN KEY (parent_context_id) REFERENCES contexts (id) ON DELETE SET NULL
        )
    """)
    
    # Anchors table - simplified schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anchors (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            fragment_ids TEXT,  -- JSON array
            context_ids TEXT,   -- JSON array
            tags TEXT,          -- JSON array
            access_count INTEGER DEFAULT 0,
            custom_fields TEXT,  -- JSON object
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            last_accessed TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    """)
    
    # Create useful indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fragments_project ON fragments (project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fragments_category ON fragments (category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_project ON contexts (project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anchors_project ON anchors (project_id)")
    
    conn.commit()
    conn.close()
    
    logger.info("SQLite database initialized successfully")

def get_or_create_collection(qdrant_client, project_id):
    """Get or create Qdrant collection for a project."""
    collection_name = f"project_{project_id.replace('-', '_')}"
    
    try:
        # Try to get existing collection
        collection_info = qdrant_client.get_collection(collection_name)
        logger.debug(f"Using existing collection: {collection_name}")
    except Exception:
        # Create new collection with optimized settings
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=768,  # text-embedding-005 dimension
                distance=Distance.COSINE,
            ),
            # Optimizations for better performance
            hnsw_config=models.HnswConfigDiff(
                m=16,  # Number of bi-directional links for every new element during construction
                ef_construct=100,  # Size of the dynamic candidate list
            ),
            optimizers_config=models.OptimizersConfigDiff(
                default_segment_number=2,  # Number of segments to optimize
            ),
        )
        logger.info(f"Created new collection: {collection_name}")
    
    return collection_name