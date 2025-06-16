#!/usr/bin/env python3
"""
MnemoX Lite - Unified Application Launcher
Starts MCP server, GUI, and system tray in unified architecture.
"""

import os
import sys
import signal
import asyncio
from pathlib import Path

# Configure UTF-8 output for Windows
if os.name == 'nt':  # Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def safe_print(message):
    """Print with fallback for encoding issues."""
    try:
        print(message, file=sys.stderr)  # All output to stderr for MCP compatibility
    except UnicodeEncodeError:
        # Fallback: replace emojis with simple text
        fallback = (
            message.replace("🚀", "[START]")
                   .replace("⚠️", "[WARNING]")
                   .replace("🔌", "[CONNECT]")
                   .replace("🛑", "[STOP]")
                   .replace("🎛️", "[TRAY]")
                   .replace("❌", "[ERROR]")
                   .replace("✅", "[OK]")
        )
        print(fallback, file=sys.stderr)

def main():
    """Main entry point using unified architecture."""
    # Initialize logging first
    from src.logging_config import setup_logging
    app_logger, mcp_logger = setup_logging()
    
    app_logger.info("Starting MnemoX Lite application")
    
    # Import using the ORIGINAL style that worked
    from src.app import MnemoXApp
    
    app = MnemoXApp()
    
    # Handle shutdown gracefully
    def signal_handler(signum, frame):
        app_logger.info(f"Received signal {signum}, shutting down...")
        safe_print("\n🛑 Shutting down MnemoX...")
        app.quit_app()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the unified app
        app_logger.info("Starting unified application")
        success = asyncio.run(app.run())
        if not success:
            app_logger.error("Application failed to start")
            sys.exit(1)
            
    except KeyboardInterrupt:
        app_logger.info("Received keyboard interrupt")
        safe_print("\n🛑 Received interrupt signal")
    except Exception as e:
        app_logger.error(f"Error in main process: {e}", exc_info=True)
        safe_print(f"❌ Error in main process: {e}")
        import traceback
        safe_print(f"📊 Main traceback:\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        app_logger.info("Application stopped")
        safe_print("✅ Process stopped")

if __name__ == "__main__":
    main()
