"""
Simplified Tray System for MnemoX Lite
Clean implementation with single instance GUI control.
Left click = show/focus GUI, Right click = quit only.
"""

import logging
import sys
from pathlib import Path

try:
    import pystray
    from PIL import Image
except ImportError:
    print("Missing dependencies. Install with: pip install pystray Pillow")
    sys.exit(1)

logger = logging.getLogger(__name__)


class SimplifiedTray:
    """Simplified tray system with clean GUI integration."""
    
    def __init__(self, gui_manager=None, app_instance=None):
        self.icon = None
        self.gui_manager = gui_manager  # Reference to MnemoXApp
        self.app_instance = app_instance  # Same as gui_manager for compatibility
        self.gui_instance = None  # Will be set later
        self.is_running = False
        
        logger.info(f"Simplified tray initialized with gui_manager: {type(gui_manager) if gui_manager else None}")
    
    def create_icon(self):
        """Load logo.png icon."""
        try:
            logo_path = Path(__file__).parent / "logo.png"
            if logo_path.exists():
                image = Image.open(logo_path)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                logger.info(f"Icon loaded from: {logo_path}")
                return image
            else:
                logger.warning("Logo not found, using fallback")
                return self._create_fallback_icon()
                
        except Exception as e:
            logger.warning(f"Error loading logo: {e}")
            return self._create_fallback_icon()
    
    def _create_fallback_icon(self):
        """Create simple fallback icon."""
        image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        # Simple blue circle
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, 28, 28], fill=(59, 130, 246, 255))
        return image
    
    def create_menu(self):
        """Create menu with both Show and Quit options (following GeeksforGeeks pattern)."""
        return pystray.Menu(
            pystray.MenuItem("Show MnemoX", self.on_show_click),
            pystray.MenuItem("Quit MnemoX", self.quit_app)
        )
    
    def on_show_click(self, icon, item):
        """Handle show GUI click from menu."""
        logger.info("=== SHOW MENU ITEM CLICKED ===")
        try:
            if self.gui_manager:
                logger.info(f"GUI manager available: {type(self.gui_manager)}")
                if self.gui_manager.is_gui_visible():
                    # GUI is visible, try to bring to front
                    logger.info("GUI visible, bringing to front")
                    if self.gui_instance and hasattr(self.gui_instance, 'bring_to_front'):
                        self.gui_instance.bring_to_front()
                    elif self.gui_instance and hasattr(self.gui_instance, 'show_window'):
                        self.gui_instance.show_window()
                    else:
                        logger.warning("No GUI instance methods available for bring to front")
                else:
                    # GUI not visible, show it
                    logger.info("GUI not visible, showing")
                    self.gui_manager.show_gui()
            else:
                logger.warning("No GUI manager available")
                
        except Exception as e:
            logger.error(f"Error handling show click: {e}", exc_info=True)
    
    def quit_app(self, icon=None, item=None):
        """Quit the entire application."""
        logger.info("Quitting application from tray")
        
        # Close GUI if exists
        if self.gui_instance and hasattr(self.gui_instance, 'close_window'):
            try:
                self.gui_instance.close_window()
            except Exception as e:
                logger.warning(f"Error closing GUI: {e}")
        
        # Stop tray
        self.is_running = False
        if self.icon:
            self.icon.stop()
        
        # Exit application
        if self.app_instance and hasattr(self.app_instance, 'quit_app'):
            self.app_instance.quit_app()
        else:
            sys.exit(0)
    
    def set_gui_instance(self, gui_instance):
        """Set the GUI instance reference."""
        self.gui_instance = gui_instance
        logger.info(f"GUI instance connected to tray: {type(gui_instance) if gui_instance else None}")
    
    def run(self):
        """Run tray system following GeeksforGeeks pattern."""
        try:
            logger.info("Creating tray icon and menu...")
            image = self.create_icon()
            menu = self.create_menu()
            
            logger.info("Creating pystray.Icon following GeeksforGeeks pattern...")
            
            # Follow the exact GeeksforGeeks pattern - NO default_action
            self.icon = pystray.Icon(
                "mnemox-lite",  # name
                image,          # icon 
                "MnemoX Lite",  # title
                menu=menu       # menu
            )
            
            self.is_running = True
            
            logger.info("Starting tray icon...")
            logger.info("🖱️ LEFT/RIGHT CLICK should show menu")
            logger.info("🖱️ Select 'Show MnemoX' to open GUI")
            
            # Run tray (blocking)
            self.icon.run()
            
        except Exception as e:
            logger.error(f"Error running tray: {e}", exc_info=True)
    
    def stop(self):
        """Stop the tray."""
        self.quit_app()


# Compatibility aliases
EnhancedTray = SimplifiedTray


def run_simple_tray(gui_callback=None):
    """Compatibility function for old callback style."""
    # Create a wrapper for callback mode
    class CallbackWrapper:
        def show_gui(self):
            if gui_callback:
                gui_callback()
        
        def is_gui_visible(self):
            return False  # Always show in callback mode
    
    wrapper = CallbackWrapper()
    tray = SimplifiedTray(gui_manager=wrapper)
    tray.run()
    return tray


def run_enhanced_tray(gui_instance=None):
    """Enhanced tray with direct GUI instance."""
    tray = SimplifiedTray(gui_manager=gui_instance)
    tray.run()
    return tray


if __name__ == "__main__":
    # Standalone mode
    run_simple_tray()
