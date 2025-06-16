"""
Storage Settings configuration section.
"""

from .base import ConfigSection


class StorageSection(ConfigSection):
    """Storage settings configuration section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the storage section."""
        self.create_section_frame("Storage Settings", requires_restart=True)
        
        # Data Directory
        self.data_dir_entry = self.add_field(
            0, "Data Directory:", "entry"
        )
        self.data_dir_entry.bind("<FocusOut>", self.update_data_dir)
        
        # Use Memory Storage
        self.memory_switch = self.add_field(
            1, "Use Memory Storage:", "switch",
            command=self.update_use_memory
        )
        
        # Backup Enabled
        self.backup_switch = self.add_field(
            2, "Backup Enabled:", "switch",
            command=self.update_backup_enabled
        )
    
    def load_values(self):
        """Load configuration values."""
        # Data directory
        data_dir = self.config.get('storage.data_dir', 'data')
        self.data_dir_entry.delete(0, "end")
        self.data_dir_entry.insert(0, data_dir)
        
        # Use memory
        use_memory = self.config.get('storage.use_memory', False)
        if use_memory:
            self.memory_switch.select()
        else:
            self.memory_switch.deselect()
        
        # Backup enabled
        backup_enabled = self.config.get('storage.backup_enabled', True)
        if backup_enabled:
            self.backup_switch.select()
        else:
            self.backup_switch.deselect()
    
    def update_data_dir(self, event=None):
        """Update data directory."""
        value = self.data_dir_entry.get().strip()
        if value:
            self.update_config('storage.data_dir', value, requires_restart=True)
    
    def update_use_memory(self):
        """Update use memory storage."""
        value = self.memory_switch.get() == 1
        self.update_config('storage.use_memory', value, requires_restart=True)
    
    def update_backup_enabled(self):
        """Update backup enabled."""
        value = self.backup_switch.get() == 1
        self.update_config('storage.backup_enabled', value, requires_restart=False)
