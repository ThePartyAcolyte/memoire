"""
Dialogs for MnemoX GUI.
Updated to use unified styling system.
"""

import customtkinter as ctk
import logging
from tkinter import messagebox
from .project_dialogs import NewProjectDialog as StyledNewProjectDialog
from ..components import BaseDialog, MnemoXColors, MnemoXFonts

logger = logging.getLogger(__name__)


class NewProjectDialog:
    """Wrapper for styled new project dialog."""
    
    def __init__(self, parent, storage, memory, refresh_callback):
        self.parent = parent
        self.storage = storage
        self.memory = memory
        self.refresh_callback = refresh_callback
    
    def show(self):
        """Show the styled new project dialog."""
        def on_success(project):
            if self.refresh_callback:
                self.refresh_callback()
        
        dialog = StyledNewProjectDialog(
            self.parent.winfo_toplevel(),
            self.storage,
            on_success
        )


class AboutDialog(ctk.CTkToplevel):
    """About dialog with NATIVE titlebar."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure NATIVE window
        self.title("About MnemoX")
        self.geometry("500x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Match main window theme
        self.configure(fg_color=("gray90", "gray13"))
        
        # Center on parent
        self.center_on_parent(parent)
        
        # Create content
        self.create_content()
        self.create_buttons()
    
    def center_on_parent(self, parent):
        """Center on parent window."""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - 250  # 250 = 500/2
        y = parent_y + (parent_height // 2) - 300  # 300 = 600/2
        
        self.geometry(f"500x600+{x}+{y}")
    
    def create_content(self):
        """Create about dialog content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo section
        logo_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(10, 20))
        
        # Large logo
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🧠",
            font=ctk.CTkFont(size=48)
        )
        logo_label.pack()
        
        # App title
        title_label = ctk.CTkLabel(
            logo_frame,
            text="MnemoX Lite",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=MnemoXColors.PRIMARY
        )
        title_label.pack(pady=(10, 5))
        
        # Version
        version_label = ctk.CTkLabel(
            logo_frame,
            text="Version 2.0 - Development",
            font=ctk.CTkFont(size=12),
            text_color=MnemoXColors.TEXT_SECONDARY
        )
        version_label.pack(pady=(0, 20))
        
        # Description section
        desc_frame = ctk.CTkFrame(content_frame)
        desc_frame.pack(fill="x", pady=(0, 15))
        
        desc_content = ctk.CTkFrame(desc_frame, fg_color="transparent")
        desc_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        desc_title = ctk.CTkLabel(
            desc_content,
            text="Semantic Memory System for LLMs",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=MnemoXColors.TEXT_PRIMARY
        )
        desc_title.pack(anchor="w", pady=(0, 10))
        
        description_text = "MnemoX provides persistent semantic memory for Large Language Models through an MCP server implementation. It features intelligent chunking, contextual memory organization, and automatic curation for enhanced AI conversations."
        
        description_label = ctk.CTkLabel(
            desc_content,
            text=description_text,
            font=ctk.CTkFont(size=11),
            text_color=MnemoXColors.TEXT_PRIMARY,
            justify="left",
            wraplength=420
        )
        description_label.pack(anchor="w")
        
        # Features section
        features_frame = ctk.CTkFrame(content_frame)
        features_frame.pack(fill="x", pady=(0, 15))
        
        features_content = ctk.CTkFrame(features_frame, fg_color="transparent")
        features_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        features_title = ctk.CTkLabel(
            features_content,
            text="Key Features",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=MnemoXColors.TEXT_PRIMARY
        )
        features_title.pack(anchor="w", pady=(0, 10))
        
        features = [
            "🔍 Semantic memory with vector search",
            "📁 Project-based memory segregation",
            "🧠 Intelligent context organization", 
            "🔄 Automatic memory curation",
            "🔗 MCP protocol compatibility"
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_content,
                text=feature,
                font=ctk.CTkFont(size=11),
                text_color=MnemoXColors.TEXT_PRIMARY,
                anchor="w"
            )
            feature_label.pack(anchor="w", pady=2)
        
        # Technology section
        tech_frame = ctk.CTkFrame(content_frame)
        tech_frame.pack(fill="x", pady=(0, 15))
        
        tech_content = ctk.CTkFrame(tech_frame, fg_color="transparent")
        tech_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        tech_title = ctk.CTkLabel(
            tech_content,
            text="Technology Stack",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=MnemoXColors.TEXT_PRIMARY
        )
        tech_title.pack(anchor="w", pady=(0, 8))
        
        tech_text = "Python 3.11+ • Qdrant Vector Database • Google Gemini API • CustomTkinter UI"
        tech_label = ctk.CTkLabel(
            tech_content,
            text=tech_text,
            font=ctk.CTkFont(size=10),
            text_color=MnemoXColors.TEXT_SECONDARY,
            wraplength=420
        )
        tech_label.pack(anchor="w")
    
    def create_buttons(self):
        """Create bottom buttons."""
        btn_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        btn_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        btn_frame.pack_propagate(False)
        
        # Close button
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            command=self.destroy,
            width=100,
            height=35
        )
        close_btn.pack(side="right", padx=20, pady=12)
    
    def show(self):
        """Show the dialog (for compatibility)."""
        pass  # Dialog shows automatically
