"""
Remote MCP Server with WebSocket support for cloud deployment.
Based on unified server but uses WebSocket instead of stdio.
"""

import asyncio
import json
import logging
import sys
import websockets
from typing import Dict, Any, List
from websockets.server import WebSocketServerProtocol

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions
from mcp.types import Tool, TextContent

from ...core.storage import StorageManager
from ...core.embedding import EmbeddingService
from ...core.memory import MemoryService
from ..intelligent_middleware import IntelligentMiddleware
from .cognitive_engine import CognitiveEngine

logger = logging.getLogger(__name__)


class RemoteMnemoXServer:
    """Remote MCP server with WebSocket transport."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.storage: StorageManager = None
        self.embedding: EmbeddingService = None
        self.memory: MemoryService = None
        self.middleware: IntelligentMiddleware = None
        self.cognitive_engine: CognitiveEngine = None
        
        # Create MCP server
        self.server = Server("mnemox-lite-remote")
        self.websocket_server = None
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Initialize all services and register MCP handlers."""
        try:
            print("🔧 Starting MnemoX remote initialization...", file=sys.stderr)
            
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
            
            logger.info("✅ Remote MnemoX MCP Server initialized")
            print("🚀 Remote MnemoX initialization complete!", file=sys.stderr)
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize remote server: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
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
    
    async def handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connection and run MCP protocol over it."""
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        print(f"🔌 New connection from {websocket.remote_address}", file=sys.stderr)
        
        try:
            # Create streams from WebSocket
            from .websocket_streams import WebSocketStreams
            streams = WebSocketStreams(websocket)
            
            # Run MCP server with WebSocket streams
            await self.server.run(
                streams.read_stream,
                streams.write_stream,
                InitializationOptions(
                    server_name="mnemox-lite-remote",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {websocket.remote_address}")
            print(f"🔌 Connection closed: {websocket.remote_address}", file=sys.stderr)
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {e}")
            print(f"❌ WebSocket error: {e}", file=sys.stderr)
    
    async def run(self):
        """Run the remote MCP server."""
        print("🎆 Starting Remote MnemoX MCP Server...", file=sys.stderr)
        
        if not await self.initialize():
            error_msg = "Failed to initialize remote server"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        self.is_running = True
        
        try:
            # Start WebSocket server
            print(f"🌐 Starting WebSocket server on port {self.port}...", file=sys.stderr)
            self.websocket_server = await websockets.serve(
                self.handle_websocket_connection,
                "0.0.0.0",  # Listen on all interfaces for cloud deployment
                self.port,
                ping_interval=30,  # Keep connections alive
                ping_timeout=10,
                max_size=1024*1024,  # 1MB max message size
            )
            
            logger.info(f"🚀 Remote MnemoX server running on port {self.port}")
            print(f"✅ Server running on http://0.0.0.0:{self.port}", file=sys.stderr)
            print("🎯 Ready to accept MCP connections via WebSocket", file=sys.stderr)
            
            # Keep server running
            await self.websocket_server.wait_closed()
            
        except Exception as e:
            error_msg = f"Error running remote server: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            import traceback
            print(f"📊 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            raise
        finally:
            self.is_running = False
    
    def shutdown(self):
        """Shutdown the server."""
        if self.websocket_server and self.is_running:
            logger.info("Shutting down WebSocket server...")
            print("🛑 Shutting down WebSocket server...", file=sys.stderr)
            self.websocket_server.close()
    
    def is_ready(self) -> bool:
        """Check if all services are ready."""
        return all([
            self.storage, self.embedding, self.memory, 
            self.middleware, self.cognitive_engine
        ])