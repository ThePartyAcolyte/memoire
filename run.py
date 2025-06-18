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
import platform

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

def is_wsl():
    """Detect if running under Windows Subsystem for Linux."""
    try:
        # Check for WSL in /proc/version
        if os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    return True
        
        # Alternative check: WSL environment variables
        if os.environ.get('WSL_DISTRO_NAME') or os.environ.get('WSLENV'):
            return True
            
        return False
    except Exception:
        return False

def should_enable_gui():
    """Determine if GUI should be enabled based on environment."""
    # Check explicit environment variable first
    enable_gui = os.environ.get('ENABLE_GUI', '').lower()
    if enable_gui in ('false', '0', 'no', 'off'):
        return False
    elif enable_gui in ('true', '1', 'yes', 'on'):
        return True
    
    # Auto-detect based on environment
    if is_wsl():
        # WSL detected - default to headless unless explicitly enabled
        return False
    
    # Check if we're in a headless environment (no DISPLAY on Linux)
    if platform.system() == 'Linux' and not os.environ.get('DISPLAY'):
        return False
    
    # Default to GUI enabled on Windows and when DISPLAY is available
    return True

def main():
    """Main entry point using unified architecture."""
    # Initialize logging first
    from src.logging_config import setup_logging
    app_logger, mcp_logger = setup_logging()
    
    # Determine GUI mode
    gui_enabled = should_enable_gui()
    mode_str = "GUI mode" if gui_enabled else "headless mode"
    
    app_logger.info(f"Starting MnemoX Lite application in {mode_str}")
    safe_print(f"🚀 Starting MnemoX Lite in {mode_str}")
    
    if is_wsl():
        safe_print("ℹ️ WSL environment detected")
    
    if not gui_enabled:
        safe_print("ℹ️ Set ENABLE_GUI=true to force GUI mode")
    
    # Import using the ORIGINAL style that worked
    from src.app import MnemoXApp
    
    app = MnemoXApp(enable_gui=gui_enabled)
    
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
