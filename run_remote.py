#!/usr/bin/env python3
"""
MnemoX Lite - Remote Server Entry Point
WebSocket-based MCP server for remote deployment (Render.com, Railway, etc.)
"""

import os
import sys
import signal
import asyncio
import logging
from pathlib import Path

# Configure UTF-8 output
if os.name == 'nt':  # Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def safe_print(message):
    """Print with fallback for encoding issues."""
    try:
        print(message, file=sys.stderr)
    except UnicodeEncodeError:
        fallback = (
            message.replace("🚀", "[START]")
                   .replace("⚠️", "[WARNING]")
                   .replace("🔌", "[CONNECT]")
                   .replace("🛑", "[STOP]")
                   .replace("❌", "[ERROR]")
                   .replace("✅", "[OK]")
        )
        print(fallback, file=sys.stderr)

async def main():
    """Main entry point for remote server."""
    # Force headless mode
    os.environ['ENABLE_GUI'] = 'false'
    
    # Initialize logging
    from src.logging_config import setup_logging
    app_logger, mcp_logger = setup_logging()
    
    app_logger.info("Starting MnemoX Lite remote server")
    safe_print("🚀 Starting MnemoX Lite remote server")
    
    # Check required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        safe_print("❌ GOOGLE_API_KEY environment variable is required")
        sys.exit(1)
    
    port = int(os.getenv("PORT", "8080"))
    safe_print(f"🔌 Server will run on port {port}")
    
    try:
        # Import remote server
        from src.mcp.server.remote import RemoteMnemoXServer
        
        # Create and initialize server
        server = RemoteMnemoXServer(port=port)
        
        # Handle shutdown gracefully
        def signal_handler(signum, frame):
            app_logger.info(f"Received signal {signum}, shutting down...")
            safe_print(f"\n🛑 Shutting down server (signal {signum})")
            server.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run server
        safe_print("✅ Starting WebSocket server...")
        await server.run()
        
    except KeyboardInterrupt:
        app_logger.info("Received keyboard interrupt")
        safe_print("\n🛑 Received interrupt signal")
    except Exception as e:
        app_logger.error(f"Error in remote server: {e}", exc_info=True)
        safe_print(f"❌ Error in remote server: {e}")
        import traceback
        safe_print(f"📊 Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        app_logger.info("Remote server stopped")
        safe_print("✅ Remote server stopped")

if __name__ == "__main__":
    asyncio.run(main())