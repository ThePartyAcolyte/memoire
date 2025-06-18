"""
MnemoX Unified Application
Single class that manages MCP server, GUI, tray, and all services.
"""

import os
import sys
import asyncio
import threading
import logging
import time
from pathlib import Path

# Tray imports (keep optional)
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

logger = logging.getLogger(__name__)


class MnemoXApp:
    """Unified application managing all MnemoX components."""
    
    def __init__(self, enable_gui=True):
        # Initialize logging
        from src.logging_config import get_app_logger
        self.logger = get_app_logger()
        
        self.logger.info(f"Initializing MnemoXApp (GUI: {'enabled' if enable_gui else 'disabled'})...")
        
        # GUI/Tray control
        self.enable_gui = enable_gui
        
        # Core services (reuse existing)
        self.storage = None
        self.embedding = None
        self.memory = None
        
        # MCP server (reuse existing)
        self.mcp_server = None
        
        # GUI components (refactored for single instance)
        self.gui_instance = None
        self.gui_thread = None
        
        # Tray (simplified)
        self.tray_instance = None
        self.tray_thread = None
        
        # State control
        self.is_running = False
        self.gui_created = False
        self.gui_visible = False
        
        # Thread safety
        import threading
        self._gui_lock = threading.Lock()
        
    async def initialize_core_services(self):
        """Initialize core services (existing logic, unchanged)."""
        try:
            from src.core.storage import StorageManager
            from src.core.embedding import EmbeddingService
            from src.core.memory import MemoryService
            
            print("📦 Creating StorageManager...", file=sys.stderr)
            self.storage = StorageManager(use_memory=False)
            
            print("🧠 Creating EmbeddingService...", file=sys.stderr)
            self.embedding = EmbeddingService()
            
            print("💾 Creating MemoryService...", file=sys.stderr)
            self.memory = MemoryService(self.storage, self.embedding)
            
            print("✅ Core services initialized", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize core services: {e}", file=sys.stderr)
            return False
    
    async def initialize_mcp_server(self):
        """Initialize MCP server (existing logic, unchanged)."""
        try:
            from src.mcp.server.unified import UnifiedMnemoXServer
            
            print("🔌 Creating MCP server...", file=sys.stderr)
            self.mcp_server = UnifiedMnemoXServer(
                storage=self.storage,
                embedding=self.embedding,
                memory=self.memory
            )
            
            if await self.mcp_server.initialize():
                print("✅ MCP server initialized", file=sys.stderr)
                return True
            else:
                print("❌ MCP server initialization failed", file=sys.stderr)
                return False
                
        except Exception as e:
            print(f"❌ MCP server error: {e}", file=sys.stderr)
            return False
    
    def initialize_gui_system(self):
        """Initialize GUI system with single instance control."""
        self.logger.info("GUI system configured for single instance control")
        return True
    
    def initialize_tray(self):
        """Initialize simplified tray system."""
        if not self.enable_gui:
            self.logger.info("GUI disabled - skipping tray initialization")
            print("ℹ️ GUI disabled - running in headless mode", file=sys.stderr)
            return True  # Return True so app continues
            
        if not TRAY_AVAILABLE:
            self.logger.warning("Tray dependencies not available")
            print("⚠️ Tray dependencies not available", file=sys.stderr)
            return False
            
        try:
            self.logger.info("Configuring simplified tray system...")
            # Tray will be created later with direct GUI instance reference
            self.logger.info("Tray system configured successfully")
            print("✅ Tray system configured", file=sys.stderr)
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing tray: {e}", exc_info=True)
            print(f"❌ Tray error: {e}", file=sys.stderr)
            return False
    

    def create_and_start_tray(self):
        """Create and start simplified tray with GUI instance."""
        if not self.enable_gui:
            self.logger.info("GUI disabled - skipping tray creation")
            return
            
        if not TRAY_AVAILABLE:
            print("❌ TRAY_AVAILABLE is False, skipping tray", file=sys.stderr)
            return
            
        def run_tray():
            try:
                print("🎛️ Importing SimplifiedTray...", file=sys.stderr)
                from src.tray.simple_tray import SimplifiedTray
                
                print("🎛️ Creating SimplifiedTray instance...", file=sys.stderr)
                self.tray_instance = SimplifiedTray(
                    gui_manager=self,
                    app_instance=self
                )
                
                print("🎛️ Starting tray.run()...", file=sys.stderr)
                self.tray_instance.run()
                
            except Exception as e:
                self.logger.error(f"Tray thread error: {e}", exc_info=True)
                print(f"❌ Tray thread error: {e}", file=sys.stderr)
                import traceback
                print(f"Tray traceback: {traceback.format_exc()}", file=sys.stderr)
        
        print("🔄 Starting tray thread...", file=sys.stderr)
        self.tray_thread = threading.Thread(target=run_tray, daemon=True, name="SimplifiedTray")
        self.tray_thread.start()
        print("✅ Simplified tray thread started", file=sys.stderr)
    

    def show_gui(self):
        """Show GUI with single instance control."""
        self.logger.info("=== SHOW_GUI CALLED ===")
        print("🖥️ show_gui() called", file=sys.stderr)
        
        with self._gui_lock:
            if self.gui_created and self.gui_instance:
                # GUI already exists, just show it
                self.logger.info("Bringing existing GUI to front")
                print("🔄 Bringing existing GUI to front", file=sys.stderr)
                try:
                    self.gui_instance.show_window()
                    self.gui_visible = True
                    return
                except Exception as e:
                    self.logger.error(f"Error showing existing GUI: {e}")
                    # GUI might be corrupted, recreate
                    self.gui_created = False
                    self.gui_instance = None
            
            if not self.gui_created:
                # Create new GUI instance
                self.logger.info("Creating new GUI instance")
                print("🖥️ Creating new GUI instance...", file=sys.stderr)
                
                def run_gui():
                    try:
                        from src.gui.customtk.app import MnemoXGUI
                        
                        self.gui_instance = MnemoXGUI(
                            storage=self.storage,
                            embedding=self.embedding,
                            memory=self.memory,
                            app_instance=self,
                            tray_instance=self.tray_instance
                        )
                        
                        self.gui_created = True
                        self.gui_visible = True
                        
                        # Connect tray to GUI
                        if self.tray_instance:
                            self.tray_instance.set_gui_instance(self.gui_instance)
                        
                        self.logger.info("Starting GUI main loop")
                        self.gui_instance.run()
                        
                        # GUI closed
                        self.gui_created = False
                        self.gui_visible = False
                        self.gui_instance = None
                        
                    except Exception as e:
                        self.logger.error(f"GUI error: {e}", exc_info=True)
                        print(f"❌ GUI error: {e}", file=sys.stderr)
                        self.gui_created = False
                        self.gui_instance = None
                
                self.gui_thread = threading.Thread(target=run_gui, daemon=True, name="MnemoXGUI")
                self.gui_thread.start()
                
                self.logger.info("GUI thread started")
                print("✅ GUI thread started", file=sys.stderr)
    
    def hide_gui(self):
        """Hide GUI window."""
        if self.gui_instance and hasattr(self.gui_instance, 'hide_window'):
            try:
                self.gui_instance.hide_window()
                self.gui_visible = False
                self.logger.info("GUI hidden")
            except Exception as e:
                self.logger.error(f"Error hiding GUI: {e}")
        else:
            self.logger.warning("No GUI instance to hide")
    
    def is_gui_visible(self):
        """Check if GUI is currently visible."""
        return self.gui_visible and self.gui_created
    
    def quit_app(self, icon=None, item=None):
        """Quit the entire application."""
        print("🛑 Shutting down MnemoX...", file=sys.stderr)
        self.is_running = False
        
        # Tray will stop automatically when the process exits
        # No need to manually stop tray in compatibility mode
        
        # MCP server will stop when main async loop ends
        sys.exit(0)
    
    async def run(self):
        """Run the unified application."""
        print("🚀 Starting MnemoX Lite unified application...", file=sys.stderr)
        
        # Check environment
        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️ Warning: GOOGLE_API_KEY not set", file=sys.stderr)
        
        # Initialize all components
        if not await self.initialize_core_services():
            self.logger.error("Core services initialization failed")
            return False
            
        if not await self.initialize_mcp_server():
            self.logger.error("MCP server initialization failed")
            return False
            
        if not self.initialize_gui_system():
            self.logger.error("GUI system initialization failed")
            return False
            
        if not self.initialize_tray():
            self.logger.warning("Tray initialization failed, continuing without tray")
            print("⚠️ Continuing without system tray", file=sys.stderr)
        
        # Start tray only if GUI is enabled (GUI opens on demand)
        if self.enable_gui:
            self.create_and_start_tray()
            # Give threads a moment to start
            await asyncio.sleep(1)
        else:
            print("ℹ️ Running in headless mode - no GUI/tray", file=sys.stderr)
        
        # Run MCP server (this blocks until shutdown)
        print("✅ All components started, running MCP server...", file=sys.stderr)
        self.is_running = True
        
        try:
            await self.mcp_server.run()
        except Exception as e:
            print(f"❌ MCP server stopped: {e}", file=sys.stderr)
            
        return True
