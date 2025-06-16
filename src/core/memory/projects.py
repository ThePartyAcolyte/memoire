"""
Project management operations for MnemoX memory system.

Handles creation, configuration, and management of memory projects with flexible schemas.
"""

import logging
from typing import List, Optional
from datetime import datetime
import uuid

from ...models import Project
from ..storage import StorageManager

logger = logging.getLogger(__name__)


async def create_project(storage: StorageManager, name: str, 
                        description: str, system_prompt: str = "") -> str:
    """Create a new memory project.
    
    Args:
        storage: Storage manager instance
        name: Project name
        description: Project description
        system_prompt: Custom system prompt (deprecated, ignored)
        
    Returns:
        Project ID of the created project
    """
    project_id = str(uuid.uuid4())
    
    project = Project(
        id=project_id,
        name=name,
        description=description,
        created_at=datetime.now()
    )
    
    # Store in database
    stored_id = storage.create_project(project)
    
    logger.info(f"Created project: {name} ({stored_id})")
    return stored_id


async def generate_system_prompt(name: str, description: str) -> str:
    """Generate a system prompt for the project using LLM (future enhancement).
    
    Args:
        name: Project name
        description: Project description
        
    Returns:
        Generated system prompt string
    """
    # For now, return a template-based prompt
    # TODO: Use LLM to generate custom system prompt based on description
    
    return f"""You are working with a semantic memory system for: {name}

PROJECT DESCRIPTION: {description}

MEMORY STRUCTURE:
- FRAGMENTS: Store information, insights, notes, and data related to this project
- CONTEXTS: Organize fragments into thematic groups for coherent navigation  
- ANCHORS: Mark important reference points and high-value information

USAGE GUIDELINES:
- Use descriptive categories and tags for fragments
- Organize related information into contexts
- Create anchors for critical insights or frequently referenced information
- Leverage custom fields to capture domain-specific metadata
- Adapt the organization to the nature of your content

This memory system is completely flexible - organize information in whatever way makes most sense for your specific use case."""


def get_project(storage: StorageManager, project_id: str) -> Optional[Project]:
    """Get project by ID.
    
    Args:
        storage: Storage manager instance
        project_id: ID of the project to retrieve
        
    Returns:
        Project object if found, None otherwise
    """
    return storage.get_project(project_id)


def list_projects(storage: StorageManager) -> List[Project]:
    """List all projects.
    
    Args:
        storage: Storage manager instance
        
    Returns:
        List of Project objects
    """
    return storage.list_projects()


def delete_project(storage: StorageManager, project_id: str) -> bool:
    """Delete a project and all its data.
    
    Args:
        storage: Storage manager instance
        project_id: ID of the project to delete
        
    Returns:
        True if deletion was successful
    """
    try:
        storage.delete_project(project_id)
        logger.info(f"Deleted project: {project_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        return False


# Export functions
__all__ = [
    "create_project",
    "generate_system_prompt", 
    "get_project",
    "list_projects",
    "delete_project"
]
