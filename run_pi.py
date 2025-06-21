#!/usr/bin/env python3
"""
MnemoX Lite - Raspberry Pi Entry Point
WebSocket-based MCP server optimized for Raspberry Pi deployment
"""

import os
import sys
import signal
import asyncio
import logging
from pathlib import Path

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
    """Main entry point for Raspberry Pi server."""
    # Force headless mode for Pi
    os.environ['ENABLE_GUI'] = 'false'
    
    # Initialize logging
    from src.logging_config import setup_logging
    app_logger, mcp_logger = setup_logging()
    
    app_logger.info("Starting MnemoX Lite on Raspberry Pi")
    safe_print("🚀 Starting MnemoX Lite on Raspberry Pi")
    
    # Check required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        safe_print("❌ GOOGLE_API_KEY environment variable is required")
        safe_print("💡 Set it with: export GOOGLE_API_KEY='your-key'")
        sys.exit(1)
    
    # Get local network IP for WebSocket server
    import socket
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "localhost"
    
    port = int(os.getenv("PORT", "8080"))
    safe_print(f"🔌 Server will run on {local_ip}:{port}")
    safe_print(f"🌐 WebSocket URL: ws://{local_ip}:{port}")
    
    try:
        # Import Pi-optimized server
        from src.mcp.server.pi_server import PiMnemoXServer
        
        # Create and initialize server
        server = PiMnemoXServer(port=port, host="0.0.0.0")  # Listen on all interfaces
        
        # Handle shutdown gracefully
        def signal_handler(signum, frame):
            app_logger.info(f"Received signal {signum}, shutting down...")
            safe_print(f"\n🛑 Shutting down Pi server (signal {signum})")
            server.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run server
        safe_print("✅ Starting Pi WebSocket server...")
        safe_print(f"📱 Connect clients to: ws://{local_ip}:{port}")
        await server.run()
        
    except KeyboardInterrupt:
        app_logger.info("Received keyboard interrupt")
        safe_print("\n🛑 Received interrupt signal")
    except Exception as e:
        app_logger.error(f"Error in Pi server: {e}", exc_info=True)
        safe_print(f"❌ Error in Pi server: {e}")
        import traceback
        safe_print(f"📊 Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        app_logger.info("Pi server stopped")
        safe_print("✅ Pi server stopped")

if __name__ == "__main__":
    asyncio.run(main())