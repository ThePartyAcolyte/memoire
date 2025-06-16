"""
Core data models for MnemoX Lite semantic memory system.

This module defines the fundamental data structures that implement the core concepts:
- Cognitive Fragments: Units of information with semantic embeddings  
- Cognitive Contexts: Thematic groupings of related fragments
- Cognitive Anchors: Important reference points for navigation
- Projects: Flexible schemas for different use cases
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


# ProjectSettings removed - simplified single-user local system
# Configuration now handled at application level


class Project(BaseModel):
    """
    A project represents a separate semantic memory space for domain segregation.
    Simplified model for single-user local deployment.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Note: Removed user_id (single-user), system_prompt (unused), 
    # settings (obsolete), is_default (handled by 'default' project)


class MemoryFragment(BaseModel):
    """
    A cognitive fragment is a basic unit of information with semantic embedding.
    Contains both core system fields and completely flexible custom metadata.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str  # Required: which project this fragment belongs to
    
    # Core content
    content: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    source: str = "user"  # user, import, api, mcp, etc.
    
    # Semantic organization
    context_ids: List[str] = Field(default_factory=list)
    anchor_ids: List[str] = Field(default_factory=list)
    
    # Completely flexible metadata - the key to schema flexibility
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # System fields (not for user modification)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Embedding stored separately in ChromaDB
    # embedding: List[float] - handled by storage layer
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryContext(BaseModel):
    """
    A cognitive context groups related fragments thematically.
    Enables coherent navigation through related information.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str  # Required: which project this context belongs to
    
    # Core fields
    name: str
    description: str = ""
    
    # Organization
    fragment_ids: List[str] = Field(default_factory=list)
    parent_context_id: Optional[str] = None
    child_context_ids: List[str] = Field(default_factory=list)
    
    # Flexible metadata
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Automatic aggregations
    fragment_count: int = 0
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CognitiveAnchor(BaseModel):
    """
    A cognitive anchor marks important reference points for navigation.
    High-value information that should resurface contextually.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str  # Required: which project this anchor belongs to
    
    # Core fields  
    title: str
    description: str = ""
    priority: str = "medium"  # low, medium, high, critical
    
    # References
    fragment_ids: List[str] = Field(default_factory=list)
    context_ids: List[str] = Field(default_factory=list)
    
    # Navigation metadata
    tags: List[str] = Field(default_factory=list)
    access_count: int = 0
    
    # Flexible metadata
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)


class SearchOptions(BaseModel):
    """Options for semantic and structured search."""
    project_id: Optional[str] = None  # Filter by specific project
    max_results: int = 10
    similarity_threshold: float = 0.5
    
    # Structural filters
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    context_ids: Optional[List[str]] = None
    anchor_ids: Optional[List[str]] = None
    
    # Custom field filters
    custom_field_filters: Optional[Dict[str, Any]] = None
    
    # Date range
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Search behavior
    include_related: bool = False
    group_by_context: bool = False


class SearchResult(BaseModel):
    """Result from semantic search with relevance and context."""
    fragment: MemoryFragment
    similarity: float
    context: Optional[MemoryContext] = None
    anchors: List[CognitiveAnchor] = Field(default_factory=list)
    related_fragments: List[str] = Field(default_factory=list)


# Export all models
__all__ = [
    "Project", 
    "MemoryFragment", "MemoryContext", "CognitiveAnchor",
    "SearchOptions", "SearchResult"
]
