"""
Project-specific dialogs with unified MnemoX styling.
"""

import customtkinter as ctk
import logging
from tkinter import messagebox
from ..components import BaseDialog, MnemoXColors, MnemoXFonts

logger = logging.getLogger(__name__)


class EditProjectDialog(BaseDialog):
    """Styled dialog for editing projects."""
    
    def __init__(self, parent, project, storage, on_success=None):
        self.project = project
        self.storage = storage
        self.on_success = on_success
        
        super().__init__(
            parent,
            title="Edit Project",
            width=500,
            height=400
        )
        
        self.set_icon("✏️")
        self.create_content()
        self.create_buttons()
    
    def create_content(self):
        """Create dialog content."""
        # Project name section
        name_section = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        name_section.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(
            name_section,
            text="Project Name:",
            font=MnemoXFonts.get_header_small(),
            text_color=MnemoXColors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.name_entry = ctk.CTkEntry(
            name_section,
            height=40,
            font=MnemoXFonts.get_body_large(),
            placeholder_text="Enter project name..."
        )
        self.name_entry.pack(fill="x")
        self.name_entry.insert(0, self.project.name)
        
        # Description section
        desc_section = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        desc_section.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(
            desc_section,
            text="Description:",
            font=MnemoXFonts.get_header_small(),
            text_color=MnemoXColors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.description_text = ctk.CTkTextbox(
            desc_section,
            font=MnemoXFonts.get_body_medium(),
            wrap="word"
        )
        self.description_text.pack(fill="both", expand=True)
        
        if self.project.description:
            self.description_text.insert("1.0", self.project.description)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def create_buttons(self):
        """Create dialog buttons."""
        self.add_button("Cancel", self.on_cancel, style="secondary", side="left")
        self.add_button("Save Changes", self.save_project, style="primary", side="right")
    
    def save_project(self):
        """Save project changes."""
        new_name = self.name_entry.get().strip()
        new_description = self.description_text.get("1.0", "end-1c").strip()
        
        if not new_name:
            # Find root window for toast
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
            
            if hasattr(root_window, 'toast'):
                root_window.toast.show_error("Project name cannot be empty")
            else:
                messagebox.showerror("Error", "Project name cannot be empty")
            return
        
        try:
            # Update project object
            self.project.name = new_name
            self.project.description = new_description if new_description else None
            
            # Save to storage
            success = self.storage.update_project(self.project)
            
            if success:
                self.result = {
                    'success': True,
                    'project': self.project
                }
                
                # Find root window for toast
                root_window = self.parent
                while hasattr(root_window, 'parent') and root_window.parent:
                    root_window = root_window.parent
                
                if hasattr(root_window, 'toast'):
                    root_window.toast.show_success(f"Project '{new_name}' updated successfully")
                
                if self.on_success:
                    self.on_success(self.project)
                
                self.destroy()
            else:
                root_window = self.parent
                while hasattr(root_window, 'parent') and root_window.parent:
                    root_window = root_window.parent
                    
                if hasattr(root_window, 'toast'):
                    root_window.toast.show_error("Failed to update project in database")
                else:
                    messagebox.showerror("Error", "Failed to update project in database")
                    
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
                
            if hasattr(root_window, 'toast'):
                root_window.toast.show_error(f"Failed to update project: {e}")
            else:
                messagebox.showerror("Error", f"Failed to update project: {e}")


class DeleteProjectDialog(BaseDialog):
    """Styled dialog for deleting projects with confirmation."""
    
    def __init__(self, parent, project, storage, on_success=None):
        self.project = project
        self.storage = storage
        self.on_success = on_success
        self.fragments_count = 0
        self.contexts_count = 0
        
        # Get project stats for confirmation
        self.load_project_stats()
        
        super().__init__(
            parent,
            title="Delete Project",
            width=500,
            height=450
        )
        
        self.set_icon("⚠️")
        self.create_content()
        self.create_buttons()
    
    def load_project_stats(self):
        """Load project statistics for confirmation dialog."""
        try:
            fragments = self.storage.list_fragments_by_project(self.project.id, limit=10000)
            contexts = self.storage.list_contexts_by_project(self.project.id)
            self.fragments_count = len(fragments)
            self.contexts_count = len(contexts)
        except Exception as e:
            logger.error(f"Error loading project stats: {e}")
    
    def create_content(self):
        """Create dialog content."""
        # Warning section
        warning_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=MnemoXColors.ERROR,
            corner_radius=8
        )
        warning_frame.pack(fill="x", pady=(10, 20))
        
        warning_content = ctk.CTkFrame(warning_frame, fg_color="transparent")
        warning_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            warning_content,
            text="⚠️ DANGER ZONE",
            font=MnemoXFonts.get_header_small(),
            text_color="white"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            warning_content,
            text="This action cannot be undone",
            font=MnemoXFonts.get_body_medium(),
            text_color="white"
        ).pack(anchor="w", pady=(5, 0))
        
        # Project info section
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            info_content,
            text="You are about to delete:",
            font=MnemoXFonts.get_body_large(),
            text_color=MnemoXColors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        # Project name
        name_frame = ctk.CTkFrame(info_content, fg_color=MnemoXColors.BG_TERTIARY)
        name_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            name_frame,
            text=f"📁 {self.project.name}",
            font=MnemoXFonts.get_header_small(),
            text_color=MnemoXColors.PRIMARY
        ).pack(padx=15, pady=10)
        
        # Stats
        stats_text = f"Including {self.fragments_count} fragments and {self.contexts_count} contexts"
        ctk.CTkLabel(
            info_content,
            text=stats_text,
            font=MnemoXFonts.get_body_medium(),
            text_color=MnemoXColors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 15))
        
        # Confirmation section
        confirm_section = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        confirm_section.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            confirm_section,
            text="Type the project name to confirm deletion:",
            font=MnemoXFonts.get_body_large(),
            text_color=MnemoXColors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.confirm_entry = ctk.CTkEntry(
            confirm_section,
            height=40,
            font=MnemoXFonts.get_body_large(),
            placeholder_text=self.project.name
        )
        self.confirm_entry.pack(fill="x")
        
        # Focus on confirmation entry
        self.confirm_entry.focus()
    
    def create_buttons(self):
        """Create dialog buttons."""
        self.add_button("Cancel", self.on_cancel, style="secondary", side="left")
        self.add_button("Delete Project", self.delete_project, style="error", side="right")
    
    def delete_project(self):
        """Delete the project after confirmation."""
        if self.confirm_entry.get().strip() != self.project.name:
            # Find root window for toast
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
            
            if hasattr(root_window, 'toast'):
                root_window.toast.show_error("Project name does not match")
            else:
                messagebox.showerror("Error", "Project name does not match")
            return
        
        try:
            # Delete project from storage
            self.storage.delete_project(self.project.id)
            
            self.result = {
                'success': True,
                'deleted_project_id': self.project.id
            }
            
            # Find root window for toast
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
            
            if hasattr(root_window, 'toast'):
                root_window.toast.show_success(f"Project '{self.project.name}' deleted successfully")
            
            if self.on_success:
                self.on_success()
            
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
                
            if hasattr(root_window, 'toast'):
                root_window.toast.show_error(f"Failed to delete project: {e}")
            else:
                messagebox.showerror("Error", f"Failed to delete project: {e}")


class NewProjectDialog(BaseDialog):
    """Styled dialog for creating new projects."""
    
    def __init__(self, parent, storage, on_success=None):
        self.storage = storage
        self.on_success = on_success
        
        super().__init__(
            parent,
            title="Create New Project",
            width=500,
            height=350
        )
        
        self.set_icon("📁")
        self.create_content()
        self.create_buttons()
    
    def create_content(self):
        """Create dialog content."""
        # Project name section
        name_section = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        name_section.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(
            name_section,
            text="Project Name:",
            font=MnemoXFonts.get_header_small(),
            text_color=MnemoXColors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.name_entry = ctk.CTkEntry(
            name_section,
            height=40,
            font=MnemoXFonts.get_body_large(),
            placeholder_text="Enter project name..."
        )
        self.name_entry.pack(fill="x")
        
        # Description section
        desc_section = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        desc_section.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(
            desc_section,
            text="Description (optional):",
            font=MnemoXFonts.get_header_small(),
            text_color=MnemoXColors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.description_text = ctk.CTkTextbox(
            desc_section,
            font=MnemoXFonts.get_body_medium(),
            wrap="word"
        )
        self.description_text.pack(fill="both", expand=True)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def create_buttons(self):
        """Create dialog buttons."""
        self.add_button("Cancel", self.on_cancel, style="secondary", side="left")
        self.add_button("Create Project", self.create_project, style="success", side="right")
    
    def create_project(self):
        """Create the new project."""
        name = self.name_entry.get().strip()
        description = self.description_text.get("1.0", "end-1c").strip()
        
        if not name:
            # Find root window for toast
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
            
            if hasattr(root_window, 'toast'):
                root_window.toast.show_error("Project name is required")
            else:
                messagebox.showerror("Error", "Project name is required")
            return
        
        try:
            # Import here to avoid circular imports
            from src.models import Project
            from datetime import datetime
            import uuid
            
            # Create new project object
            project = Project(
                id=str(uuid.uuid4()),
                name=name,
                description=description if description else None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to storage
            project_id = self.storage.create_project(project)
            
            self.result = {
                'success': True,
                'project': project
            }
            
            # Find root window for toast
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
            
            if hasattr(root_window, 'toast'):
                root_window.toast.show_success(f"Project '{name}' created successfully")
            
            if self.on_success:
                self.on_success(project)
            
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            root_window = self.parent
            while hasattr(root_window, 'parent') and root_window.parent:
                root_window = root_window.parent
                
            if hasattr(root_window, 'toast'):
                root_window.toast.show_error(f"Failed to create project: {e}")
            else:
                messagebox.showerror("Error", f"Failed to create project: {e}")
