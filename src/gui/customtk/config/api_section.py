"""
API Configuration section.
"""

import customtkinter as ctk
import os
from .base import ConfigSection


class APISection(ConfigSection):
    """API Keys status section."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, config_manager)
        self.create_section()
    
    def create_section(self):
        """Create the API section."""
        self.create_section_frame("API Configuration", requires_restart=False)
        
        # Google API Key status
        self.add_field(0, "Google API Key:", "label")
        google_status = "✅ Set" if os.getenv("GOOGLE_API_KEY") else "❌ Missing"
        self.google_status_label = ctk.CTkLabel(
            self.content_frame, 
            text=google_status,
            text_color=("#10B981", "#059669") if os.getenv("GOOGLE_API_KEY") else ("#EF4444", "#DC2626")
        )
        self.google_status_label.grid(row=0, column=1, sticky="w", padx=15, pady=10)
    
    def add_field(self, row, label_text, widget_type):
        """Override to add just labels for API section."""
        label = ctk.CTkLabel(self.content_frame, text=label_text)
        label.grid(row=row, column=0, sticky="w", padx=15, pady=10)
    
    def refresh_status(self):
        """Refresh API key status."""
        google_status = "✅ Set" if os.getenv("GOOGLE_API_KEY") else "❌ Missing"
        self.google_status_label.configure(
            text=google_status,
            text_color=("#10B981", "#059669") if os.getenv("GOOGLE_API_KEY") else ("#EF4444", "#DC2626")
        )
