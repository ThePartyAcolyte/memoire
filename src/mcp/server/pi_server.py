"""
Raspberry Pi optimized MCP Server with WebSocket support.
Memory-optimized configuration for Pi 3 hardware.
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
from .websocket_streams import WebSocketStreams

logger = logging.getLogger(__name__)


class PiMnemoXServer:
    """Raspberry Pi optimized MCP server with WebSocket transport."""
    
    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.storage: StorageManager = None
        self.embedding: EmbeddingService = None
        self.memory: MemoryService = None
        self.middleware: IntelligentMiddleware = None
        self.cognitive_engine: CognitiveEngine = None
        
        # Create MCP server
        self.server = Server("mnemox-lite-pi")
        self.websocket_server = None
        self.is_running = False
        
        # Pi-specific optimizations
        self._configure_pi_optimizations()
        
    def _configure_pi_optimizations(self):
        """Configure optimizations for Raspberry Pi 3."""
        # Reduce memory usage
        import gc
        gc.set_threshold(100, 5, 5)  # More aggressive garbage collection
        
        # Set lower limits for Pi
        self.max_concurrent_connections = 5  # Limit concurrent connections
        self.max_message_size = 512 * 1024  # 512KB max message
        self.ping_interval = 60  # Longer ping interval to reduce CPU
        
        logger.info("Pi optimizations configured")
        
    async def initialize(self) -> bool:
        """Initialize all services with Pi optimizations."""
        try:
            print("🔧 Starting MnemoX Pi initialization...", file=sys.stderr)
            
            # Initialize core services with Pi-friendly settings
            print("📦 Initializing StorageManager (Pi optimized)...", file=sys.stderr)
            self.storage = StorageManager(use_memory=False)
            print("✅ StorageManager initialized", file=sys.stderr)
            
            print("🧠 Initializing EmbeddingService...", file=sys.stderr)
            self.embedding = EmbeddingService()
            print("✅ EmbeddingService initialized", file=sys.stderr)
            
            print("💾 Initializing MemoryService (Pi optimized)...", file=sys.stderr)
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
            
            logger.info("✅ Pi MnemoX MCP Server initialized")
            print("🚀 Pi MnemoX initialization complete!", file=sys.stderr)
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize Pi server: {e}"
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
            """Handle tool calls with Pi optimizations."""
            try:
                if name == "remember":
                    content = arguments.get("content", "")
                    project_id = arguments.get("project_id", "default")
                    context = arguments.get("context", "")
                    result = await self.cognitive_engine.remember(content, project_id, context)
                    
                    response_text = result.get("message", "Memory stored successfully")
                    if result.get("success", False):
                        response_text += f"\n• Category: {result.get('category', 'general')}"
                        # Shorter response for Pi to save bandwidth
                    
                    return [TextContent(type="text", text=response_text)]
                    
                elif name == "recall":
                    query = arguments.get("query", "")
                    project_id = arguments.get("project_id", "default")
                    focus = arguments.get("focus", "")
                    result = await self.cognitive_engine.recall(query, project_id, focus)
                    
                    if result.get("success", False):
                        response_text = result.get("response", "No information found")
                        
                        # Simplified insights for Pi
                        if result.get("fragments_found", 0) > 0:
                            response_text += f"\n\n📊 Found {result.get('fragments_found', 0)} relevant fragments"
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
                        response_text = f"✅ Created project '{name_param}' (ID: {project_id})"
                    else:
                        response_text = "❌ Failed to create project"
                    
                    return [TextContent(type="text", text=response_text)]
                
                elif name == "list_projects":
                    projects = await self.cognitive_engine.list_projects()
                    
                    if projects:
                        response_text = "📁 Available Projects:\n\n"
                        for project in projects:
                            response_text += f"• {project['name']} ({project['id']})\n"
                        response_text += f"\nTotal: {len(projects)} projects"
                    else:
                        response_text = "No projects found. Create one with create_project()."
                    
                    return [TextContent(type="text", text=response_text)]
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error handling Pi tool call {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connection with Pi optimizations."""
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        logger.info(f"New connection from {client_ip}")
        print(f"🔌 New connection from {client_ip}", file=sys.stderr)
        
        try:
            # Create streams from WebSocket
            streams = WebSocketStreams(websocket)
            
            # Run MCP server with WebSocket streams
            await self.server.run(
                streams.read_stream,
                streams.write_stream,
                InitializationOptions(
                    server_name="mnemox-lite-pi",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {client_ip}")
            print(f"🔌 Connection closed: {client_ip}", file=sys.stderr)
        except Exception as e:
            logger.error(f"Error handling WebSocket connection from {client_ip}: {e}")
            print(f"❌ WebSocket error from {client_ip}: {e}", file=sys.stderr)
    
    async def run(self):
        """Run the Pi MCP server."""
        print("🎆 Starting Pi MnemoX MCP Server...", file=sys.stderr)
        
        if not await self.initialize():
            error_msg = "Failed to initialize Pi server"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        self.is_running = True
        
        try:
            # Start WebSocket server with Pi optimizations
            print(f"🌐 Starting WebSocket server on {self.host}:{self.port}...", file=sys.stderr)
            self.websocket_server = await websockets.serve(
                self.handle_websocket_connection,
                self.host,
                self.port,
                ping_interval=self.ping_interval,
                ping_timeout=20,
                max_size=self.max_message_size,
                max_queue=32,  # Limit queue size for Pi
            )
            
            logger.info(f"🚀 Pi MnemoX server running on {self.host}:{self.port}")
            print(f"✅ Pi server running on {self.host}:{self.port}", file=sys.stderr)
            print("🎯 Ready to accept MCP connections via WebSocket", file=sys.stderr)
            
            # Display connection info
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                print(f"📱 Local network URL: ws://{local_ip}:{self.port}", file=sys.stderr)
            except:
                pass
            
            # Keep server running
            await self.websocket_server.wait_closed()
            
        except Exception as e:
            error_msg = f"Error running Pi server: {e}"
            logger.error(error_msg)
            print(f"❌ {error_msg}", file=sys.stderr)
            import traceback
            print(f"📊 Traceback:\n{traceback.format_exc()}", file=sys.stderr)
            raise
        finally:
            self.is_running = False
    
    def shutdown(self):
        """Shutdown the Pi server."""
        if self.websocket_server and self.is_running:
            logger.info("Shutting down Pi WebSocket server...")
            print("🛑 Shutting down Pi WebSocket server...", file=sys.stderr)
            self.websocket_server.close()
    
    def is_ready(self) -> bool:
        """Check if all services are ready."""
        return all([
            self.storage, self.embedding, self.memory, 
            self.middleware, self.cognitive_engine
        ])