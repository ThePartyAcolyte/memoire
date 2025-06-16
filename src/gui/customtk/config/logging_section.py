"""
Logging configuration section.
"""

from .base import ConfigSection


class LoggingSection(ConfigSection):
    """Logging configuration section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the logging section."""
        self.create_section_frame("Logging & Debug", requires_restart=False)
        
        # Log Level
        self.log_level_combo = self.add_field(
            0, "Log Level:", "combo",
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            command=self.update_log_level
        )
        
        # Max File Size
        self.max_file_size_entry = self.add_field(
            1, "Max File Size (MB):", "entry",
            width=100
        )
        self.max_file_size_entry.bind("<FocusOut>", self.update_max_file_size)
        
        # Backup Count
        self.backup_count_entry = self.add_field(
            2, "Backup Count:", "entry",
            width=100
        )
        self.backup_count_entry.bind("<FocusOut>", self.update_backup_count)
    
    def load_values(self):
        """Load configuration values."""
        # Log level
        log_level = self.config.get('logging.level', 'INFO')
        self.log_level_combo.set(log_level)
        
        # Max file size
        max_file_size = self.config.get('logging.max_file_size_mb', 10)
        self.max_file_size_entry.delete(0, "end")
        self.max_file_size_entry.insert(0, str(max_file_size))
        
        # Backup count
        backup_count = self.config.get('logging.backup_count', 3)
        self.backup_count_entry.delete(0, "end")
        self.backup_count_entry.insert(0, str(backup_count))
    
    def update_log_level(self, value):
        """Update log level."""
        self.update_config('logging.level', value, requires_restart=False)
    
    def update_max_file_size(self, event=None):
        """Update max file size."""
        try:
            value = int(self.max_file_size_entry.get())
            self.update_config('logging.max_file_size_mb', value, requires_restart=False)
        except ValueError:
            # Reset to current value on invalid input
            current = self.config.get('logging.max_file_size_mb', 10)
            self.max_file_size_entry.delete(0, "end")
            self.max_file_size_entry.insert(0, str(current))
    
    def update_backup_count(self, event=None):
        """Update backup count."""
        try:
            value = int(self.backup_count_entry.get())
            self.update_config('logging.backup_count', value, requires_restart=False)
        except ValueError:
            # Reset to current value on invalid input
            current = self.config.get('logging.backup_count', 3)
            self.backup_count_entry.delete(0, "end")
            self.backup_count_entry.insert(0, str(current))
