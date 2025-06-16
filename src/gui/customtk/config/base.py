"""
Base class for configuration sections.
"""

import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)


class ConfigSection:
    """Base class for configuration sections."""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config = config_manager
        self.widgets = {}
        self.section_frame = None
        
        # Track changes that require restart
        self.pending_changes = {}
        self.requires_restart_fields = set()
        
    def create_section_frame(self, title, requires_restart=False):
        """Create a collapsible section frame with header."""
        self.section_frame = ctk.CTkFrame(self.parent)
        self.section_frame.grid_columnconfigure(0, weight=1)
        
        # Header with icon
        header_frame = ctk.CTkFrame(self.section_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Restart indicator
        restart_icon = "⚠️" if requires_restart else "🔄"
        restart_text = " Requires Restart" if requires_restart else " Hot Reload"
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=restart_icon,
            font=ctk.CTkFont(size=14)
        )
        icon_label.grid(row=0, column=0, padx=(15, 5), pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w", padx=0, pady=10)
        
        status_label = ctk.CTkLabel(
            header_frame,
            text=restart_text,
            font=ctk.CTkFont(size=10),
            text_color=("#EF4444", "#DC2626") if requires_restart else ("#10B981", "#059669")
        )
        status_label.grid(row=0, column=2, padx=(0, 15), pady=10)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.section_frame)
        self.content_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.content_frame.grid_columnconfigure(1, weight=1)
        
        return self.section_frame
    
    def add_field(self, row, label_text, widget_type, **kwargs):
        """Add a field to the section."""
        # Label
        label = ctk.CTkLabel(self.content_frame, text=label_text)
        label.grid(row=row, column=0, sticky="w", padx=15, pady=10)
        
        # Widget
        if widget_type == "entry":
            widget = ctk.CTkEntry(self.content_frame, **kwargs)
        elif widget_type == "combo":
            widget = ctk.CTkComboBox(self.content_frame, **kwargs)
        elif widget_type == "slider":
            widget = ctk.CTkSlider(self.content_frame, **kwargs)
        elif widget_type == "switch":
            widget = ctk.CTkSwitch(self.content_frame, text="", **kwargs)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")
        
        widget.grid(row=row, column=1, sticky="ew" if widget_type in ["entry", "combo"] else "w", padx=15, pady=10)
        
        return widget
    
    def add_slider_with_value(self, row, label_text, **kwargs):
        """Add a slider with value display."""
        # Label
        label = ctk.CTkLabel(self.content_frame, text=label_text)
        label.grid(row=row, column=0, sticky="w", padx=15, pady=10)
        
        # Slider frame
        slider_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        slider_frame.grid(row=row, column=1, sticky="ew", padx=15, pady=10)
        slider_frame.grid_columnconfigure(0, weight=1)
        
        # Slider
        slider = ctk.CTkSlider(slider_frame, **kwargs)
        slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Value label
        value_label = ctk.CTkLabel(slider_frame, text="0.0", width=40)
        value_label.grid(row=0, column=1)
        
        return slider, value_label
    
    def grid(self, **kwargs):
        """Grid the section frame."""
        if self.section_frame:
            self.section_frame.grid(**kwargs)
    
    def load_values(self):
        """Load configuration values into widgets. Override in subclasses."""
        pass
    
    def update_config(self, key, value, requires_restart=False):
        """Track configuration changes without saving immediately."""
        try:
            # Store pending change
            self.pending_changes[key] = value
            
            # Track if this field requires restart
            if requires_restart:
                self.requires_restart_fields.add(key)
            
            logger.info(f"Tracked change {key} = {value} (restart: {requires_restart})")
            return True
        except Exception as e:
            logger.error(f"Failed to track change {key}: {e}")
            return False
    
    def apply_changes(self):
        """Apply all pending changes to config."""
        restart_needed = False
        applied_changes = []
        
        try:
            for key, value in self.pending_changes.items():
                # Set config without saving yet
                self.config.set(key, value, save=False)
                applied_changes.append(key)
                
                # Check if any applied change requires restart
                if key in self.requires_restart_fields:
                    restart_needed = True
            
            # Clear pending changes
            self.pending_changes.clear()
            self.requires_restart_fields.clear()
            
            logger.info(f"Applied {len(applied_changes)} changes")
            return restart_needed, applied_changes
            
        except Exception as e:
            logger.error(f"Failed to apply changes: {e}")
            return False, []
    
    def has_pending_changes(self):
        """Check if there are unsaved changes."""
        return len(self.pending_changes) > 0
