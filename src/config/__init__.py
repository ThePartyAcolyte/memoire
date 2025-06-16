"""
Configuration manager for MnemoX Lite.
Handles JSON config loading, hot reloading, and environment variable overrides.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class ConfigManager:
    """Thread-safe configuration manager with hot reload support."""
    
    def __init__(self, config_path: str = "config.json"):
        # Always resolve paths relative to project root
        project_root = Path(__file__).parent.parent.parent  # From src/config/ to project root
        if not Path(config_path).is_absolute():
            self.config_path = project_root / config_path
        else:
            self.config_path = Path(config_path)
        
        self._config: Dict[str, Any] = {}
        self._lock = Lock()
        self._observers = []
        
        # Load initial config
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from JSON file with env var overrides."""
        try:
            with self._lock:
                if not self.config_path.exists():
                    logger.warning(f"Config file {self.config_path.absolute()} not found, using defaults")
                    self._config = self._get_default_config()
                    return False
                
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                
                # Apply environment variable overrides
                self._apply_env_overrides()
                
                logger.info(f"Configuration loaded from {self.config_path.absolute()}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = self._get_default_config()
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to JSON file."""
        try:
            with self._lock:
                # Create backup
                if self.config_path.exists():
                    backup_path = self.config_path.with_suffix('.json.bak')
                    # Only create backup if original exists
                    import shutil
                    shutil.copy2(self.config_path, backup_path)
                
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Configuration saved to {self.config_path}")
                self._notify_observers()
                return True
                
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'processing.model')."""
        with self._lock:
            keys = key_path.split('.')
            value = self._config
            
            try:
                for key in keys:
                    value = value[key]
                return value
            except (KeyError, TypeError):
                return default
    
    def set(self, key_path: str, value: Any, save: bool = True) -> bool:
        """Set configuration value using dot notation."""
        with self._lock:
            keys = key_path.split('.')
            config = self._config
            
            try:
                # Navigate to parent
                for key in keys[:-1]:
                    if key not in config:
                        config[key] = {}
                    config = config[key]
                
                # Set value
                config[keys[-1]] = value
                
                if save:
                    return self.save_config()
                return True
                
            except Exception as e:
                logger.error(f"Failed to set config {key_path}: {e}")
                return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self.get(section, {})
    
    def add_observer(self, callback):
        """Add observer for configuration changes."""
        self._observers.append(callback)
    
    def remove_observer(self, callback):
        """Remove configuration change observer."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self):
        """Notify all observers of configuration changes."""
        for callback in self._observers:
            try:
                callback(self._config)
            except Exception as e:
                logger.error(f"Observer callback failed: {e}")
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # API Keys
        if os.getenv("GOOGLE_API_KEY"):
            self._config.setdefault("api_keys", {})["google"] = os.getenv("GOOGLE_API_KEY")
        
        # Override specific settings from env vars
        env_mappings = {
            "MNEMOX_USE_MEMORY": ("storage.use_memory", lambda x: x.lower() == "true"),
            "MNEMOX_DATA_DIR": ("storage.data_dir", str),
            "MNEMOX_LOG_LEVEL": ("logging.level", str),
            "MNEMOX_SIMILARITY_THRESHOLD": ("search.similarity_threshold", float),
            "MNEMOX_MAX_RESULTS": ("search.max_results", int),
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                try:
                    self.set(config_key, converter(env_value), save=False)
                except Exception as e:
                    logger.warning(f"Failed to apply env override {env_var}: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file is missing."""
        return {
            "embedding": {
                "provider": "google",
                "model": "text-embedding-005",
                "dimension": 768,
                "cache_ttl_hours": 24,
                "batch_size": 10,
                "delay_seconds": 0.1
            },
            "processing": {
                "model": "gemini-2.5-flash-preview-05-20",
                "temperature": 0.3,
                "max_tokens": 8192
            },
            "search": {
                "similarity_threshold": 0.6,
                "max_results": 50
            },
            "chunking": {
                "min_chunk_words": 20,
                "max_chunk_words": 150,
                "semantic_overlap_threshold": 0.9
            },
            "storage": {
                "data_dir": "data",
                "use_memory": False,
                "backup_enabled": True
            },
            "intelligence": {
                "enable_curation": True,
                "curation_similarity_threshold": 0.54,
                "curation_search_threshold": 0.4
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "max_file_size_mb": 10,
                "backup_count": 3
            }
        }
    
    def validate_config(self) -> list[str]:
        """Validate configuration and return warnings/errors."""
        warnings = []
        
        # Check API keys availability
        google_key = os.getenv("GOOGLE_API_KEY")
        
        if not google_key:
            warnings.append("Google API key not found in environment variables")
        
        # Validate processing model
        processing_model = self.get("processing.model")
        if not processing_model or not isinstance(processing_model, str):
            warnings.append("Invalid processing model configuration")
        
        # Validate similarity threshold
        threshold = self.get("search.similarity_threshold")
        if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            warnings.append("Invalid similarity threshold, must be between 0 and 1")
        
        # Validate chunking parameters
        min_words = self.get("chunking.min_chunk_words", 0)
        max_words = self.get("chunking.max_chunk_words", 0)
        if min_words >= max_words:
            warnings.append("Invalid chunking word limits")
        
        return warnings


# Global config instance
config = ConfigManager()
