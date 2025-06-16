"""
MCP tools definitions and schemas.
Simple natural language interface for memory operations.
"""

from typing import Dict, Any, List


def get_tool_schemas() -> List[Dict[str, Any]]:
    """Return simplified MCP tool schemas for natural language interaction."""
    
    return [
        {
            "name": "remember",
            "description": "Store information in semantic memory with project segregation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string", 
                        "description": "What to remember - use natural language, can be facts, decisions, code, anything"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project to store in (use 'default' for general memory, or specific project ID)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about this memory (category, tags, etc.)"
                    }
                },
                "required": ["content", "project_id"]
            }
        },
        {
            "name": "recall",
            "description": "Search memory and get a synthesized, coherent response about what you want to know.",
            "inputSchema": {
                "type": "object", 
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What you want to know - use natural language question"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project to search in (use 'default' for general memory, or specific project ID)"
                    },
                    "focus": {
                        "type": "string",
                        "description": "Optional focus area (timeframe, specific topic, etc.)"
                    }
                },
                "required": ["query", "project_id"]
            }
        },
        {
            "name": "create_project",
            "description": "Create a new memory project for domain segregation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name (e.g., 'Research Notes', 'Work Projects')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description explaining its purpose"
                    }
                },
                "required": ["name", "description"]
            }
        },
        {
            "name": "list_projects",
            "description": "List all available memory projects.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]
