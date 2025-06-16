"""
Individual project widget for MnemoX GUI.
Displays project information with edit and delete functionality.
Uses unified styling system.
"""

import customtkinter as ctk
import logging
from .project_dialogs import EditProjectDialog, DeleteProjectDialog
from ..components import MnemoXColors, MnemoXFonts

logger = logging.getLogger(__name__)


class ProjectWidget(ctk.CTkFrame):
    """Individual project widget with detailed information and actions."""
    
    def __init__(self, parent, project, storage, memory, refresh_callback):
        super().__init__(parent)
        self.project = project
        self.storage = storage
        self.memory = memory
        self.refresh_callback = refresh_callback
        
        self.grid_columnconfigure(1, weight=1)
        
        # Get project stats
        self.fragments_count = 0
        self.contexts_count = 0
        self.load_project_stats()
        
        self.create_widgets()
    
    def load_project_stats(self):
        """Load project statistics."""
        try:
            fragments = self.storage.list_fragments_by_project(self.project.id, limit=10000)
            contexts = self.storage.list_contexts_by_project(self.project.id)
            self.fragments_count = len(fragments)
            self.contexts_count = len(contexts)
        except Exception as e:
            logger.error(f"Error loading project stats: {e}")
    
    def create_widgets(self):
        """Create project widget content."""
        # Project name
        self.name_label = ctk.CTkLabel(
            self,
            text=self.project.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.name_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(15, 5))
        
        # Description
        description_text = self.project.description if self.project.description else "No description"
        self.description_label = ctk.CTkLabel(
            self,
            text=description_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray40"),
            anchor="w",
            wraplength=300
        )
        self.description_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 10))
        
        # Stats
        stats_text = f"📄 {self.fragments_count} fragments • 🗂️ {self.contexts_count} contexts"
        self.stats_label = ctk.CTkLabel(
            self,
            text=stats_text,
            font=ctk.CTkFont(size=10),
            text_color=("#3B82F6", "#60A5FA"),
            anchor="w"
        )
        self.stats_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 10))
        
        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=2, sticky="e", padx=15, pady=(0, 10))
        
        # Edit button
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Edit",
            command=self.edit_project,
            width=60,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            command=self.delete_project,
            width=70,
            height=25,
            font=ctk.CTkFont(size=10),
            fg_color=("#EF4444", "#DC2626"),
            hover_color=("#DC2626", "#B91C1C")
        )
        delete_btn.pack(side="left")
    
    def edit_project(self):
        """Open styled edit dialog for project."""
        def on_success(updated_project):
            # Update the UI
            self.name_label.configure(text=updated_project.name)
            desc_text = updated_project.description if updated_project.description else "No description"
            self.description_label.configure(text=desc_text)
            
            if self.refresh_callback:
                self.refresh_callback()
        
        dialog = EditProjectDialog(
            self.winfo_toplevel(),
            self.project,
            self.storage,
            on_success
        )
    
    def delete_project(self):
        """Delete project with styled confirmation dialog."""
        def on_success():
            # Remove widget from UI
            self.destroy()
            if self.refresh_callback:
                self.refresh_callback()
        
        dialog = DeleteProjectDialog(
            self.winfo_toplevel(),
            self.project,
            self.storage,
            on_success
        )
