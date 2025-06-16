"""
MCP Server with cognitive engine and proper MCP protocol implementation.
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

from ...core.storage import StorageManager
from ...core.embedding import EmbeddingService
from ...core.memory import MemoryService
from ..intelligent_middleware import IntelligentMiddleware
from .cognitive_engine import CognitiveEngine

logger = logging.getLogger(__name__)


class MnemoXServer:
    """Main MCP server with cognitive engine integration."""
    
    def __init__(self):
        self.storage: StorageManager = None
        self.embedding: EmbeddingService = None
        self.memory: MemoryService = None
        self.middleware: IntelligentMiddleware = None
        self.cognitive_engine: CognitiveEngine = None
        
        # Create MCP server
        self.server = Server("mnemox-lite")
        
    async def initialize(self) -> bool:
        """Initialize all services and register MCP handlers."""
        try:
            print("🔧 Starting MnemoX initialization...", file=sys.stderr)
            
            # Initialize core services
            print("📦 Initializing StorageManager...", file=sys.stderr)
            self.storage = StorageManager(use_memory=False)
            print("✅ StorageManager initialized", file=sys.stderr)
            
            print("🧠 Initializing EmbeddingService...", file=sys.stderr)
            self.embedding = EmbeddingService()
            print("✅ EmbeddingService initialized", file=sys.stderr)
            
            print("💾 Initializing MemoryService...", file=sys.stderr)
            self.memory = MemoryService(self.storage, self.embedding)
            print("✅ MemoryService initialized", file=sys.stderr)
            
            print("🤖 Initializing IntelligentMiddleware...", file=sys.stderr)
            self.middleware = IntelligentMiddleware(self.memory)
            print("✅ IntelligentMiddleware initialized", file=sys.stderr)
            
            # Initialize cognitive engine
            print("🧩 Initializing CognitiveEngine...", file=sys.stderr)
            self.cognitive_engine = CognitiveEngine(self)
            print("✅ CognitiveEngine initialized", file=sys.stderr)
            
            # Register MCP handlers
            print("🔌 Registering MCP handlers...", file=sys.stderr)
            await self._register_handlers()
            print("✅ MCP handlers registered", file=sys.stderr)
            
            logger.info("✅ MnemoX MCP Server initialized with cognitive engine")
            print("🚀 MnemoX initialization complete!", file=sys.stderr)
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize: {e}"
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
                        
                        # Add insights if available
                        insights = result.get("insights", {})
                        if insights:
                            response_text += f"\n\n• Confidence: {result.get('confidence', 0):.1%}"
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
        
        logger.info("✅ MCP handlers registered: list_tools, call_tool")
    
    def is_ready(self) -> bool:
        """Check if all services are ready."""
        return all([
            self.storage, self.embedding, self.memory, 
            self.middleware, self.cognitive_engine
        ])
    
    async def run(self):
        """Run the MCP server."""
        print("🎆 Starting MnemoX MCP Server...", file=sys.stderr)
        
        if not await self.initialize():
            error_msg = "Failed to initialize server"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            sys.exit(1)
       
        print("🔌 Connecting to stdio streams...", file=sys.stderr)
        logger.info("🚀 Starting MnemoX MCP Server...")
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                print("📞 Connected to stdio, running server...", file=sys.stderr)
                await self.server.run(
                    read_stream, 
                    write_stream,
                    InitializationOptions(
                        server_name="mnemox-lite",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except Exception as e:
            error_msg = f"Error running MCP server: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            import traceback
            print(f"📊 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            raise


# Main execution
async def main():
    """Main entry point."""
    print("🎯 MCP main() function started", file=sys.stderr)
    server = MnemoXServer()
    print("🏗️ MnemoXServer instance created", file=sys.stderr)
    await server.run()


if __name__ == "__main__":
    print("🔥 Starting MCP server script...", file=sys.stderr)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    print("📝 Logging configured", file=sys.stderr)
    
    # Run server
    try:
        print("🚀 About to run asyncio.run(main())...", file=sys.stderr)
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error in main execution: {e}", file=sys.stderr)
        import traceback
        print(f"📊 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
        raise
