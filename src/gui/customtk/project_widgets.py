"""
Widgets actualizados para projects tab usando componentes corregidos.
"""

import customtkinter as ctk
import logging
from datetime import datetime
from .components import ProjectDialog, ConfirmDialog

logger = logging.getLogger(__name__)


class ProjectWidget(ctk.CTkFrame):
    """Widget individual para mostrar información de proyecto con acciones."""
    
    def __init__(self, parent, project, storage, memory, refresh_callback):
        super().__init__(parent)
        
        self.project = project
        self.storage = storage
        self.memory = memory
        self.refresh_callback = refresh_callback
        
        self.configure(fg_color=("gray95", "gray15"), corner_radius=8)
        self.grid_columnconfigure(1, weight=1)
        
        self.create_content()
    
    def create_content(self):
        """Crear contenido del widget de proyecto."""
        # Icono del proyecto
        icon_label = ctk.CTkLabel(
            self,
            text="📁",
            font=ctk.CTkFont(size=24),
            width=40
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=15, sticky="n")
        
        # Información del proyecto
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Nombre del proyecto
        name_label = ctk.CTkLabel(
            info_frame,
            text=self.project.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="ew")
        
        # Descripción (si existe)
        if self.project.description:
            desc_text = self.project.description
            if len(desc_text) > 100:
                desc_text = desc_text[:97] + "..."
            
            desc_label = ctk.CTkLabel(
                info_frame,
                text=desc_text,
                font=ctk.CTkFont(size=11),
                text_color=("gray60", "gray40"),
                anchor="w",
                wraplength=400
            )
            desc_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # Estadísticas del proyecto
        self.create_stats_section(info_frame)
        
        # Botones de acción
        self.create_action_buttons()
    
    def create_stats_section(self, parent):
        """Crear sección de estadísticas del proyecto."""
        try:
            # Obtener estadísticas del proyecto
            project_id = getattr(self.project, 'project_id', None) or getattr(self.project, 'id', None)
            
            if not project_id:
                raise ValueError("Project has no valid ID attribute")
            
            # Usar los métodos correctos del storage
            try:
                # Intentar primero los métodos count_*
                fragment_count = self.storage.count_fragments_by_project(project_id)
                context_count = self.storage.count_contexts_by_project(project_id)
            except AttributeError:
                # Fallback: usar list_* y contar manualmente
                logger.debug(f"Using fallback list methods for project {project_id}")
                fragments = self.storage.list_fragments_by_project(project_id) or []
                contexts = self.storage.list_contexts_by_project(project_id) or []
                fragment_count = len(fragments)
                context_count = len(contexts)
            
            stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
            stats_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
            
            # Fragmentos
            fragments_label = ctk.CTkLabel(
                stats_frame,
                text=f"📝 {fragment_count} fragments",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray50")
            )
            fragments_label.grid(row=0, column=0, sticky="w")
            
            # Contextos
            contexts_label = ctk.CTkLabel(
                stats_frame,
                text=f"🏷️ {context_count} contexts",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray50")
            )
            contexts_label.grid(row=0, column=1, sticky="w", padx=(20, 0))
            
            # ID del proyecto (útil para debug)
            id_label = ctk.CTkLabel(
                stats_frame,
                text=f"ID: {project_id}",
                font=ctk.CTkFont(size=9),
                text_color=("gray40", "gray60")
            )
            id_label.grid(row=0, column=2, sticky="e", padx=(20, 0))
            
            stats_frame.grid_columnconfigure(2, weight=1)
            
        except Exception as e:
            logger.error(f"Error loading project stats for project '{self.project.name}' (ID: {getattr(self.project, 'id', 'unknown')}): {e}", exc_info=True)
            # Mostrar stats por defecto en caso de error
            error_label = ctk.CTkLabel(
                parent,
                text=f"Error loading stats: {str(e)[:50]}...",
                font=ctk.CTkFont(size=10),
                text_color=("#EF4444", "#DC2626")
            )
            error_label.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    
    def create_action_buttons(self):
        """Crear botones de acción del proyecto."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=(10, 15), pady=15)
        
        # Botón editar
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            command=self.edit_project,
            width=80,
            height=30,
            font=ctk.CTkFont(size=11)
        )
        edit_btn.grid(row=0, column=0, pady=(0, 5))
        
        # Botón eliminar
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete",
            command=self.delete_project,
            width=80,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=("#EF4444", "#DC2626"),
            hover_color=("#DC2626", "#B91C1C")
        )
        delete_btn.grid(row=1, column=0)
    
    def edit_project(self):
        """Editar proyecto usando el patrón correcto del AboutDialog."""
        def on_save(project_data):
            try:
                # Obtener el proyecto existente y actualizarlo
                project_id = getattr(self.project, 'project_id', None) or getattr(self.project, 'id', None)
                
                if not project_id:
                    raise ValueError("Project ID not found")
                
                # Obtener proyecto existente del storage
                existing_project = self.storage.get_project(project_id)
                if not existing_project:
                    raise ValueError(f"Project {project_id} not found in storage")
                
                # Actualizar campos
                existing_project.name = project_data['name']
                existing_project.description = project_data['description']
                existing_project.updated_at = datetime.now()
                
                # Guardar usando el objeto Project completo
                result = self.storage.update_project(existing_project)
                
                if result:
                    # Mostrar toast de éxito
                    main_gui = self.find_main_gui()
                    if main_gui and hasattr(main_gui, 'toast'):
                        main_gui.toast.show_success(f"Project '{project_data['name']}' updated successfully!")
                    # Refrescar lista
                    self.refresh_callback()
                else:
                    main_gui = self.find_main_gui()
                    if main_gui and hasattr(main_gui, 'toast'):
                        main_gui.toast.show_error("Failed to update project")
                        
            except Exception as e:
                logger.error(f"Error updating project: {e}", exc_info=True)
                main_gui = self.find_main_gui()
                if main_gui and hasattr(main_gui, 'toast'):
                    main_gui.toast.show_error(f"Error updating project: {e}")
        
        # Preparar datos existentes
        project_data = {
            'name': self.project.name,
            'description': self.project.description or ''
        }
        
        # Usar self.root como parent (igual que AboutDialog)
        main_gui = self.find_main_gui()
        parent_window = main_gui.root if main_gui and hasattr(main_gui, 'root') else self
        
        # Importar aquí para evitar import circular
        from .components import ProjectDialog
        
        dialog = ProjectDialog(
            parent_window,
            title="Edit Project",
            project_data=project_data,
            on_save=on_save
        )
    
    def delete_project(self):
        """Eliminar proyecto con confirmación."""
        def on_confirm():
            try:
                # Eliminar proyecto usando storage
                project_id = getattr(self.project, 'project_id', None) or getattr(self.project, 'id', None)
                
                result = self.storage.delete_project(project_id)
                if result:
                    # Mostrar toast de éxito
                    main_gui = self.find_main_gui()
                    if main_gui and hasattr(main_gui, 'toast'):
                        main_gui.toast.show_success(f"Project '{self.project.name}' deleted successfully!")
                    # Refrescar lista
                    self.refresh_callback()
                else:
                    main_gui = self.find_main_gui()
                    if main_gui and hasattr(main_gui, 'toast'):
                        main_gui.toast.show_error("Failed to delete project")
            except Exception as e:
                logger.error(f"Error deleting project: {e}")
                main_gui = self.find_main_gui()
                if main_gui and hasattr(main_gui, 'toast'):
                    main_gui.toast.show_error(f"Error deleting project: {e}")
        
        # Usar la ventana principal como parent, no el widget
        main_gui = self.find_main_gui()
        parent_window = main_gui.root if main_gui and hasattr(main_gui, 'root') else self
        
        dialog = ConfirmDialog(
            parent_window,
            title="Delete Project",
            message=f"Are you sure you want to delete project '{self.project.name}'?\n\nThis action cannot be undone and will remove all associated fragments and contexts.",
            confirm_text="Delete",
            cancel_text="Cancel",
            icon="🗑️",
            danger=True
        )
        
        dialog.on_confirm = on_confirm
    
    def find_main_gui(self):
        """Encontrar la instancia principal de GUI para acceso a toast."""
        widget = self
        while widget:
            if hasattr(widget, 'toast') and hasattr(widget, 'root'):
                return widget
            widget = getattr(widget, 'master', None) or getattr(widget, 'parent', None)
        return None
