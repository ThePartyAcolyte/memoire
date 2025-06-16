"""
Logging configuration for MnemoX Lite.
Separates app logs from MCP logs for better debugging.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Setup logging configuration with separate files for app and MCP."""
    
    # Remove any existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Base formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # APP Logger (GUI, tray, main app logic)
    app_logger = logging.getLogger('mnemox.app')
    app_logger.setLevel(logging.DEBUG)
    
    app_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)
    
    # MCP Logger (memory operations, storage, embeddings)
    mcp_logger = logging.getLogger('mnemox.mcp')
    mcp_logger.setLevel(logging.DEBUG)
    
    mcp_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f"mcp_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    mcp_handler.setFormatter(formatter)
    mcp_logger.addHandler(mcp_handler)
    
    # Console handler for critical errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    
    # Add console to both loggers
    app_logger.addHandler(console_handler)
    mcp_logger.addHandler(console_handler)
    
    # Root logger setup for any other libraries
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    
    root_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f"system_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    root_handler.setFormatter(formatter)
    root_logger.addHandler(root_handler)
    
    # Log startup
    app_logger.info("=" * 60)
    app_logger.info("MnemoX Lite logging initialized")
    app_logger.info(f"App logs: {app_handler.baseFilename}")
    app_logger.info(f"MCP logs: {mcp_handler.baseFilename}")
    app_logger.info("=" * 60)
    
    return app_logger, mcp_logger

def get_app_logger():
    """Get the app logger."""
    return logging.getLogger('mnemox.app')

def get_mcp_logger():
    """Get the MCP logger."""
    return logging.getLogger('mnemox.mcp')
