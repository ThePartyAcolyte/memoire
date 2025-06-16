"""
Simplified natural language MCP handlers.
The Cognitive Engine that interprets user intent and manages memory operations.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class CognitiveEngine:
    """
    The cognitive engine that interprets natural language input and manages memory.
    
    This is the heart of the system - it decides:
    - What to store and how to organize it
    - What to retrieve and how to synthesize it
    - When to update/overwrite existing memories
    """
    
    def __init__(self, server):
        self.server = server
        # Note: Removed default_user (single-user system)
        # Note: Removed default_project (now handled per-request)
    
    async def _ensure_default_project(self) -> str:
        """Ensure we have a default project available."""
        # Check if 'default' project exists
        existing_project = self.server.storage.get_project("default")
        if existing_project:
            return "default"
        
        # Create default project with fixed ID 'default'
        from ...models import Project
        default_project = Project(
            id="default",
            name="General Memory",
            description="Default project for general memory storage"
        )
        
        project_id = self.server.storage.create_project(default_project)
        logger.info(f"Created default project: {project_id}")
        return project_id
    
    async def remember(self, content: str, project_id: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Store information in semantic memory with intelligent processing.
        
        Now uses enhanced chunking and contextualization when available.
        """
        if not self.server.is_ready():
            raise RuntimeError("Services not ready")
        
        try:
            # Ensure project exists (create default if needed)
            if project_id == "default":
                project_id = await self._ensure_default_project()
            else:
                # Verify project exists
                existing_project = self.server.storage.get_project(project_id)
                if not existing_project:
                    return {
                        "success": False,
                        "error": f"Project '{project_id}' not found",
                        "message": "Project does not exist. Use list_projects() to see available projects or create_project() to create a new one."
                    }
            
            # Try enhanced processing first
            if hasattr(self.server.middleware, 'process_remember_enhanced'):
                try:
                    enhanced_result = await self.server.middleware.process_remember_enhanced(
                        content, project_id, context
                    )
                    
                    if enhanced_result.get("success"):
                        return {
                            "success": True,
                            "message": enhanced_result.get("message", "Content processed with enhanced intelligence"),
                            "fragments_created": enhanced_result.get("fragments_created", 1),
                            "fragment_ids": enhanced_result.get("fragment_ids", []),
                            "contexts_used": enhanced_result.get("contexts_used", []),
                            "category": "enhanced_processing",
                            "reasoning": "Content chunked and contextualized intelligently"
                        }
                except Exception as e:
                    logger.warning(f"Enhanced processing failed, falling back to legacy: {e}")
            
            # Fallback to legacy processing
            project_state = {
                "project_name": "Personal Memory", 
                "description": "Personal memory storage",
                "clusters": []
            }
            
            analysis = self.server.middleware.analyze_content(content, project_state)
            
            fragment_id = await self.server.memory.store_fragment(
                project_id, 
                content, 
                source="natural_language"
            )
            
            cluster_info = f"categorized as '{analysis.get('target_cluster', 'general')}'"
            confidence_info = f"with {analysis.get('confidence', 0.5):.1%} confidence"
            
            return {
                "success": True,
                "message": f"Remembered and {cluster_info} {confidence_info}",
                "fragment_id": fragment_id,
                "category": analysis.get('target_cluster', 'general'),
                "reasoning": analysis.get('reasoning', 'Content stored successfully')
            }
            
        except Exception as e:
            logger.error(f"Error in remember: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store memory"
            }
    
    async def recall(self, query: str, project_id: str, focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Search memory and return a synthesized, coherent response.
        
        Now uses enhanced recall with curation when available.
        """
        if not self.server.is_ready():
            raise RuntimeError("Services not ready")
        
        try:
            # Ensure project exists (create default if needed)
            if project_id == "default":
                project_id = await self._ensure_default_project()
            else:
                # Verify project exists
                existing_project = self.server.storage.get_project(project_id)
                if not existing_project:
                    return {
                        "success": False,
                        "error": f"Project '{project_id}' not found",
                        "message": "Project does not exist. Use list_projects() to see available projects."
                    }
            
            # Try enhanced recall first
            if hasattr(self.server, 'middleware') and hasattr(self.server.middleware, 'process_recall_enhanced'):
                try:
                    # Check if curation is enabled
                    from src.config import config
                    curation_enabled = config.get('intelligence.enable_curation', True)
                    
                    if curation_enabled:
                        enhanced_result = await self.server.middleware.process_recall_enhanced(
                            query, project_id, focus
                        )
                        
                        if enhanced_result.get("success"):
                            response_data = {
                                "success": True,
                                "response": enhanced_result.get("response", "No response generated"),
                                "confidence": enhanced_result.get("confidence", 0.5),
                                "coverage": enhanced_result.get("coverage", "partial"),
                                "fragments_found": enhanced_result.get("fragments_found", 0),
                                "insights": enhanced_result.get("insights", {})
                            }
                            
                            # Add curation info if available
                            if enhanced_result.get("curation_applied"):
                                response_data["curation_applied"] = True
                                response_data["fragments_after_curation"] = enhanced_result.get("fragments_after_curation", 0)
                                response_data["curation_reasoning"] = enhanced_result.get("curation_reasoning", "")
                                
                            return response_data
                except Exception as e:
                    logger.warning(f"Enhanced recall with curation failed, falling back to legacy: {e}")
            
            # Fallback to legacy recall
            from ...models import SearchOptions
            options = SearchOptions(
                project_id=project_id,
                max_results=15,
                similarity_threshold=0.3
            )
            
            search_results = await self.server.memory.search_memory(
                query, 
                options
            )
            
            if not search_results:
                return {
                    "success": True,
                    "response": f"I don't have any memories related to '{query}'. Would you like me to remember something about this topic?",
                    "confidence": 0.0,
                    "coverage": "none",
                    "fragments_found": 0
                }
            
            synthesis = self.server.middleware.synthesize_memory_response(
                query, 
                search_results
            )
            
            response = synthesis.get("synthesized_response", "Unable to synthesize response")
            confidence = synthesis.get("confidence", 0.5)
            coverage = synthesis.get("information_coverage", "partial")
            gaps = synthesis.get("gaps", [])
            patterns = synthesis.get("patterns_identified", [])
            
            response_data = {
                "success": True,
                "response": response,
                "confidence": confidence,
                "coverage": coverage,
                "fragments_found": len(search_results),
                "insights": {
                    "patterns": patterns,
                    "knowledge_gaps": gaps,
                    "completeness": coverage
                }
            }
            
            if confidence < 0.6:
                response_data["note"] = "This response is based on limited information. Consider adding more details to improve future recalls."
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in recall: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to recall memories"
            }
    
    async def create_project(self, name: str, description: str) -> Optional[str]:
        """Create a new memory project."""
        try:
            if not self.server.is_ready():
                return None
            
            from ...models import Project
            project = Project(
                name=name,
                description=description
            )
            
            project_id = self.server.storage.create_project(project)
            logger.info(f"Created project: {name} ({project_id})")
            return project_id
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    async def list_projects(self) -> List[Dict[str, str]]:
        """List all available projects."""
        try:
            if not self.server.is_ready():
                return []
            
            # Ensure default project exists
            await self._ensure_default_project()
            
            # Get all projects  
            projects = self.server.storage.list_projects()
            
            # Convert to simple dict format
            result = []
            for project in projects:
                result.append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []


# Legacy handlers for backward compatibility (can be removed later)
class MemoryHandlers:
    def __init__(self, server):
        self.cognitive_engine = CognitiveEngine(server)
    
    # New simplified interface
    async def remember(self, content: str, project_id: str = "default", context: str = None) -> Dict[str, Any]:
        """Remember something using natural language."""
        return await self.cognitive_engine.remember(content, project_id, context)
    
    async def recall(self, query: str, project_id: str = "default", focus: str = None) -> Dict[str, Any]:
        """Recall information using natural language query."""
        return await self.cognitive_engine.recall(query, project_id, focus)
