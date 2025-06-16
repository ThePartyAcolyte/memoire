"""
Unified MCP Server that receives pre-initialized shared services.
No service initialization - uses shared instances from main process.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions
from mcp.types import Tool, TextContent

from ...mcp.intelligent_middleware import IntelligentMiddleware
from .cognitive_engine import CognitiveEngine

logger = logging.getLogger(__name__)


class UnifiedMnemoXServer:
    """MCP server that uses shared services from main process."""
    
    def __init__(self, storage, embedding, memory):
        # Use shared services directly
        self.storage = storage
        self.embedding = embedding
        self.memory = memory
        self.middleware = None
        self.cognitive_engine = None
        
        # Create MCP server
        self.server = Server("mnemox-lite-unified")
        
        logger.info("Unified MCP server initialized with shared services")
        
    async def initialize(self) -> bool:
        """Initialize middleware and cognitive engine with shared services."""
        try:
            print("🤖 Initializing IntelligentMiddleware with shared services...", file=sys.stderr)
            self.middleware = IntelligentMiddleware(self.memory)
            print("✅ IntelligentMiddleware initialized", file=sys.stderr)
            
            print("🧩 Initializing CognitiveEngine with shared services...", file=sys.stderr)
            self.cognitive_engine = CognitiveEngine(self)
            print("✅ CognitiveEngine initialized", file=sys.stderr)
            
            print("🔌 Registering MCP handlers...", file=sys.stderr)
            await self._register_handlers()
            print("✅ MCP handlers registered", file=sys.stderr)
            
            logger.info("✅ Unified MCP Server initialized with shared services")
            print("🚀 Unified MCP initialization complete!", file=sys.stderr)
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize unified MCP server: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            print(f"📍 Error details: {type(e).__name__}: {str(e)}", file=sys.stderr)
            import traceback
            print(f"📊 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            return False
    
    async def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        # Register tools list handler
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return available tools."""
            return [
                Tool(
                    name="remember",
                    description="Store information in semantic memory with project segregation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "What to remember - facts, decisions, code, anything"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Project to store in (use 'default' for general memory)"
                            },
                            "context": {
                                "type": "string", 
                                "description": "Optional context about this memory"
                            }
                        },
                        "required": ["content", "project_id"]
                    }
                ),
                Tool(
                    name="recall",
                    description="Search memory and get synthesized response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "What you want to know - natural language question"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Project to search in (use 'default' for general memory)"
                            },
                            "focus": {
                                "type": "string",
                                "description": "Optional focus area"
                            }
                        },
                        "required": ["query", "project_id"]
                    }
                ),
                Tool(
                    name="create_project",
                    description="Create a new memory project for domain segregation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Project name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Project description"
                            }
                        },
                        "required": ["name", "description"]
                    }
                ),
                Tool(
                    name="list_projects",
                    description="List all available memory projects",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        # Register tool call handler
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "remember":
                    content = arguments.get("content", "")
                    project_id = arguments.get("project_id", "default")
                    context = arguments.get("context", "")
                    result = await self.cognitive_engine.remember(content, project_id, context)
                    
                    response_text = result.get("message", "Memory stored successfully")
                    if result.get("success", False):
                        response_text += f"\n• Category: {result.get('category', 'general')}"
                        response_text += f"\n• Reasoning: {result.get('reasoning', 'N/A')}"
                    
                    return [TextContent(type="text", text=response_text)]
                    
                elif name == "recall":
                    query = arguments.get("query", "")
                    project_id = arguments.get("project_id", "default")
                    focus = arguments.get("focus", "")
                    result = await self.cognitive_engine.recall(query, project_id, focus)
                    
                    if result.get("success", False):
                        response_text = result.get("response", "No information found")
                        
                        # Add curation info if available
                        if result.get("curation_applied"):
                            response_text += f"\n\n🧹 **Memory Curation Applied**"
                            response_text += f"\n• Fragments before curation: {result.get('fragments_found', 0)}"
                            response_text += f"\n• Fragments after curation: {result.get('fragments_after_curation', 0)}"
                            if result.get("curation_reasoning"):
                                response_text += f"\n• Curation reasoning: {result.get('curation_reasoning')}"
                        
                        # Add insights if available
                        insights = result.get("insights", {})
                        if insights:
                            response_text += f"\n\n📊 **Query Analysis**"
                            response_text += f"\n• Confidence: {result.get('confidence', 0):.1%}"
                            response_text += f"\n• Coverage: {result.get('coverage', 'unknown')}"
                            response_text += f"\n• Fragments found: {result.get('fragments_found', 0)}"
                            
                            if insights.get("knowledge_gaps"):
                                response_text += f"\n• Knowledge gaps: {', '.join(insights['knowledge_gaps'])}"
                    else:
                        response_text = result.get("message", "Failed to recall information")
                    
                    return [TextContent(type="text", text=response_text)]
                
                elif name == "create_project":
                    name_param = arguments.get("name", "")
                    description = arguments.get("description", "")
                    
                    if not name_param or not description:
                        return [TextContent(type="text", text="Error: name and description are required")]
                    
                    project_id = await self.cognitive_engine.create_project(name_param, description)
                    
                    if project_id:
                        response_text = f"✅ Created project '{name_param}' with ID: {project_id}"
                        response_text += f"\n• Description: {description}"
                        response_text += f"\n• Use project_id='{project_id}' in remember/recall operations"
                    else:
                        response_text = "❌ Failed to create project"
                    
                    return [TextContent(type="text", text=response_text)]
                
                elif name == "list_projects":
                    projects = await self.cognitive_engine.list_projects()
                    
                    if projects:
                        response_text = "📁 Available Projects:\n\n"
                        for project in projects:
                            response_text += f"• **{project['name']}** (`{project['id']}`)\n"
                            response_text += f"  {project['description']}\n\n"
                        response_text += "Use these project IDs in remember/recall operations."
                    else:
                        response_text = "No projects found. Create one with create_project()."
                    
                    return [TextContent(type="text", text=response_text)]
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        logger.info("✅ Unified MCP handlers registered: list_tools, call_tool")
    
    def is_ready(self) -> bool:
        """Check if all services are ready."""
        return all([
            self.storage, self.embedding, self.memory, 
            self.middleware, self.cognitive_engine
        ])
    
    async def run(self):
        """Run the unified MCP server."""
        print("🎆 Starting Unified MnemoX MCP Server...", file=sys.stderr)
        
        print("🔌 Connecting to stdio streams...", file=sys.stderr)
        logger.info("🚀 Starting Unified MnemoX MCP Server...")
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                print("📞 Connected to stdio, running unified server...", file=sys.stderr)
                await self.server.run(
                    read_stream, 
                    write_stream,
                    InitializationOptions(
                        server_name="mnemox-lite-unified",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except Exception as e:
            error_msg = f"Error running unified MCP server: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            import traceback
            print(f"📊 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            raise
