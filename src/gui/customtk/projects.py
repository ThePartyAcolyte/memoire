"""
Projects tab refactorizado con debugging completo y manejo robusto de errores.
"""

import customtkinter as ctk
import logging
from .components import ProjectDialog, ConfirmDialog
from .project_widgets import ProjectWidget

logger = logging.getLogger('mnemox.projects')


class ProjectsTab:
    """Projects tab refactorizado con manejo robusto de errores."""
    
    def __init__(self, parent, storage, embedding, memory, config):
        self.parent = parent
        self.storage = storage
        self.embedding = embedding
        self.memory = memory
        self.config = config
        
        self.projects_frame = None
        self.projects_container = None
        self.search_var = None
        self.cached_projects = []
        self.loading_state = False
        
        logger.info("Inicializando ProjectsTab...")
        self.create_projects_tab()
    
    def create_projects_tab(self):
        """Create projects tab content."""
        logger.debug("Creando interfaz de proyectos...")
        
        self.projects_frame = ctk.CTkFrame(self.parent)
        self.projects_frame.grid_columnconfigure(0, weight=1)
        self.projects_frame.grid_rowconfigure(2, weight=1)
        
        # Header section
        self.create_header()
        
        # Search and filters section
        self.create_search_section()
        
        # Projects list section
        self.create_projects_list()
        
        # Action buttons section
        self.create_action_buttons()
        
        logger.info("Interfaz de proyectos creada exitosamente")
    
    def create_header(self):
        """Create header with title and new project button."""
        header_frame = ctk.CTkFrame(self.projects_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Project Management",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # New project button
        new_project_btn = ctk.CTkButton(
            header_frame,
            text="+ New Project",
            command=self.create_new_project,
            width=140,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        new_project_btn.grid(row=0, column=1, sticky="e")
    
    def create_search_section(self):
        """Create search and filter controls."""
        search_frame = ctk.CTkFrame(self.projects_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Search:",
            font=ctk.CTkFont(size=12)
        )
        search_label.grid(row=0, column=0, padx=(15, 10), pady=15)
        
        # Search entry
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search projects by name or description...",
            height=35
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        
        # Results count
        self.results_label = ctk.CTkLabel(
            search_frame,
            text="Loading...",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        self.results_label.grid(row=0, column=2, padx=(10, 15), pady=15)
    
    def create_projects_list(self):
        """Create main projects list."""
        self.projects_container = ctk.CTkScrollableFrame(self.projects_frame)
        self.projects_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.projects_container.grid_columnconfigure(0, weight=1)
        
        # Mostrar loading state inicialmente
        self.show_loading_state()
        
        # Cargar proyectos de forma asíncrona (simulada)
        self.projects_frame.after(100, self.initial_load_projects)
    
    def create_action_buttons(self):
        """Create action buttons at bottom."""
        actions_frame = ctk.CTkFrame(self.projects_frame, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_projects_list,
            width=120,
            height=35
        )
        refresh_btn.grid(row=0, column=0, sticky="w")
        
        # Debug button (temporal para debugging)
        debug_btn = ctk.CTkButton(
            actions_frame,
            text="🐛 Debug Info",
            command=self.show_debug_info,
            width=120,
            height=35,
            fg_color=("#8B5CF6", "#7C3AED")
        )
        debug_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Export button (for future implementation)
        export_btn = ctk.CTkButton(
            actions_frame,
            text="📤 Export",
            command=self.export_projects,
            width=120,
            height=35,
            fg_color=("gray70", "gray30"),
            state="disabled"
        )
        export_btn.grid(row=0, column=2, sticky="e")
    
    def show_debug_info(self):
        """Mostrar información de debug."""
        logger.info("=== DEBUG INFO - PROJECTS ===")
        logger.info(f"Storage instance: {type(self.storage)}")
        
        # Mostrar TODOS los métodos del storage
        all_methods = [m for m in dir(self.storage) if not m.startswith('_')]
        logger.info(f"ALL storage methods: {all_methods}")
        
        # Métodos relacionados con proyectos
        project_methods = [m for m in dir(self.storage) if 'project' in m.lower()]
        logger.info(f"Project-related methods: {project_methods}")
        
        # Métodos relacionados con fragmentos
        fragment_methods = [m for m in dir(self.storage) if 'fragment' in m.lower()]
        logger.info(f"Fragment-related methods: {fragment_methods}")
        
        # Métodos relacionados con contextos
        context_methods = [m for m in dir(self.storage) if 'context' in m.lower()]
        logger.info(f"Context-related methods: {context_methods}")
        
        logger.info(f"Cached projects count: {len(self.cached_projects)}")
        logger.info(f"Loading state: {self.loading_state}")
        
        # Intentar obtener proyectos directamente
        try:
            logger.info("Intentando llamar storage.list_projects()...")
            projects = self.storage.list_projects()
            logger.info(f"Resultado: {len(projects) if projects else 0} proyectos")
            for i, proj in enumerate(projects[:3] if projects else []):
                logger.info(f"  Proyecto {i}: {proj.name} (ID: {proj.id})")
        except Exception as e:
            logger.error(f"Error en storage.list_projects(): {e}", exc_info=True)
        
        # Mostrar en toast
        main_gui = self.find_main_gui()
        if main_gui and hasattr(main_gui, 'toast'):
            main_gui.toast.show_info(f"Debug info logged. Projects cached: {len(self.cached_projects)}")
    
    def show_loading_state(self):
        """Mostrar estado de carga."""
        # Limpiar contenedor
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(
            self.projects_container,
            text="🔄 Loading projects...",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        loading_label.grid(row=0, column=0, pady=40)
        
        self.results_label.configure(text="Loading...")
    
    def initial_load_projects(self):
        """Carga inicial de proyectos con manejo completo de errores."""
        logger.info("Iniciando carga inicial de proyectos...")
        self.loading_state = True
        
        try:
            # Verificar que storage esté disponible
            if not self.storage:
                raise Exception("Storage instance is None")
            
            # Verificar que el método exista
            if not hasattr(self.storage, 'list_projects'):
                raise Exception(f"Storage {type(self.storage)} does not have list_projects method")
            
            logger.info("Llamando a storage.list_projects()...")
            projects = self.storage.list_projects()
            
            if projects is None:
                logger.warning("storage.list_projects() returned None")
                projects = []
            
            logger.info(f"Obtenidos {len(projects)} proyectos del storage")
            
            # Validar cada proyecto
            valid_projects = []
            for i, project in enumerate(projects):
                try:
                    # Verificar que tenga los atributos necesarios
                    if not hasattr(project, 'name'):
                        logger.warning(f"Proyecto {i} no tiene atributo 'name': {project}")
                        continue
                    if not hasattr(project, 'id'):  # Usar 'id' en lugar de 'project_id'
                        logger.warning(f"Proyecto {i} no tiene atributo 'id': {project}")
                        continue
                    
                    valid_projects.append(project)
                    logger.debug(f"Proyecto válido: {project.name} (ID: {project.id})")
                    
                except Exception as proj_error:
                    logger.error(f"Error validando proyecto {i}: {proj_error}")
            
            self.cached_projects = valid_projects
            
            # Nota: No podemos agregar project_id dinámicamente a modelos Pydantic
            # En su lugar, usaremos getattr consistentemente en el código
            
            logger.info(f"Cached {len(self.cached_projects)} proyectos válidos")
            
            # Mostrar proyectos
            self.display_projects(self.cached_projects)
            
        except Exception as e:
            logger.error(f"Error crítico cargando proyectos: {e}", exc_info=True)
            self.show_error_state(str(e))
        finally:
            self.loading_state = False
    
    def show_error_state(self, error_message):
        """Mostrar estado de error con detalles."""
        # Limpiar contenedor
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        
        error_frame = ctk.CTkFrame(self.projects_container, fg_color=("#FECACA", "#7F1D1D"))
        error_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=40)
        error_frame.grid_columnconfigure(0, weight=1)
        
        # Icono y título de error
        error_icon = ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=ctk.CTkFont(size=32)
        )
        error_icon.grid(row=0, column=0, pady=(20, 10))
        
        error_title = ctk.CTkLabel(
            error_frame,
            text="Error Loading Projects",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#7F1D1D", "#FECACA")
        )
        error_title.grid(row=1, column=0, pady=(0, 10))
        
        # Mensaje de error (truncado)
        error_msg = error_message if len(error_message) < 100 else error_message[:97] + "..."
        error_detail = ctk.CTkLabel(
            error_frame,
            text=error_msg,
            font=ctk.CTkFont(size=11),
            text_color=("#7F1D1D", "#FECACA"),
            wraplength=400
        )
        error_detail.grid(row=2, column=0, pady=(0, 20), padx=20)
        
        # Botón retry
        retry_btn = ctk.CTkButton(
            error_frame,
            text="🔄 Retry",
            command=self.retry_load_projects,
            width=100,
            height=35,
            fg_color=("#DC2626", "#EF4444")
        )
        retry_btn.grid(row=3, column=0, pady=(0, 20))
        
        self.results_label.configure(text="Error loading projects")
    
    def retry_load_projects(self):
        """Reintentar carga de proyectos."""
        logger.info("Reintentando carga de proyectos...")
        self.show_loading_state()
        self.projects_frame.after(500, self.initial_load_projects)
    
    def create_new_project(self):
        """Create new project dialog."""
        def on_save(project_data):
            try:
                logger.info(f"Creando nuevo proyecto: {project_data['name']}")
                
                result = self.storage.create_project(
                    project_data['name'], 
                    project_data['description']
                )
                
                if result:
                    logger.info(f"Proyecto '{project_data['name']}' creado exitosamente")
                    main_gui = self.find_main_gui()
                    if main_gui and hasattr(main_gui, 'toast'):
                        main_gui.toast.show_success(f"Project '{project_data['name']}' created successfully!")
                    self.refresh_projects_list()
                else:
                    logger.error(f"Falló la creación del proyecto: {project_data['name']}")
                    main_gui = self.find_main_gui()
                    if main_gui and hasattr(main_gui, 'toast'):
                        main_gui.toast.show_error("Failed to create project")
                        
            except Exception as e:
                logger.error(f"Error creating project: {e}", exc_info=True)
                main_gui = self.find_main_gui()
                if main_gui and hasattr(main_gui, 'toast'):
                    main_gui.toast.show_error(f"Error creating project: {e}")
        
        dialog = ProjectDialog(
            self.projects_frame.winfo_toplevel(),
            title="Create New Project",
            on_save=on_save
        )
    
    def find_main_gui(self):
        """Encontrar la instancia principal de GUI para acceso a toast."""
        widget = self.parent
        while widget:
            if hasattr(widget, 'toast') and hasattr(widget, 'root'):
                return widget
            widget = getattr(widget, 'master', None) or getattr(widget, 'parent', None)
        return None
    
    def on_search_change(self, *args):
        """Handle search input changes."""
        if self.loading_state:
            return
            
        search_term = self.search_var.get().lower().strip()
        self.filter_projects(search_term)
    
    def filter_projects(self, search_term=""):
        """Filter projects based on search term."""
        try:
            if not self.cached_projects:
                logger.warning("No cached projects available for filtering")
                return
            
            if search_term:
                filtered_projects = []
                for project in self.cached_projects:
                    try:
                        name_match = search_term in project.name.lower()
                        desc_match = (project.description and 
                                    search_term in project.description.lower())
                        
                        if name_match or desc_match:
                            filtered_projects.append(project)
                    except Exception as e:
                        logger.warning(f"Error filtering project {project}: {e}")
                        
                projects_to_show = filtered_projects
            else:
                projects_to_show = self.cached_projects
            
            # Update results count
            total_count = len(self.cached_projects)
            filtered_count = len(projects_to_show)
            
            if search_term:
                self.results_label.configure(text=f"{filtered_count} of {total_count} projects")
            else:
                self.results_label.configure(text=f"{total_count} projects")
            
            # Update display
            self.display_projects(projects_to_show)
            
        except Exception as e:
            logger.error(f"Error filtering projects: {e}", exc_info=True)
            self.results_label.configure(text="Error filtering")
    
    def display_projects(self, projects):
        """Display filtered projects list."""
        logger.debug(f"Displaying {len(projects)} projects")
        
        # Clear existing widgets
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        
        if not projects:
            if self.search_var and self.search_var.get().strip():
                # No results for search
                no_results_label = ctk.CTkLabel(
                    self.projects_container,
                    text=f"No projects found matching '{self.search_var.get()}'",
                    text_color=("gray60", "gray40"),
                    font=ctk.CTkFont(size=12)
                )
                no_results_label.grid(row=0, column=0, pady=40)
            else:
                # No projects at all
                empty_state_label = ctk.CTkLabel(
                    self.projects_container,
                    text="No projects found\n\nClick '+ New Project' to create your first project",
                    text_color=("gray60", "gray40"),
                    font=ctk.CTkFont(size=12),
                    justify="center"
                )
                empty_state_label.grid(row=0, column=0, pady=40)
        else:
            # Display projects
            for i, project in enumerate(projects):
                try:
                    project_widget = ProjectWidget(
                        self.projects_container,
                        project,
                        self.storage,
                        self.memory,
                        self.refresh_projects_list
                    )
                    project_widget.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
                    logger.debug(f"Displayed project widget {i}: {project.name}")
                    
                except Exception as e:
                    logger.error(f"Error creating widget for project {i} ({project}): {e}")
    
    def refresh_projects_list(self):
        """Refresh the complete projects list."""
        logger.info("Refreshing projects list...")
        
        # Reset search
        if self.search_var:
            self.search_var.set("")
        
        # Show loading and reload
        self.show_loading_state()
        self.projects_frame.after(100, self.initial_load_projects)
    
    def export_projects(self):
        """Export projects data (placeholder for future implementation)."""
        logger.info("Export projects functionality not yet implemented")
    
    def grid(self, **kwargs):
        """Grid the projects frame."""
        if self.projects_frame:
            self.projects_frame.grid(**kwargs)
    
    def grid_remove(self):
        """Remove the projects frame from grid."""
        if self.projects_frame:
            self.projects_frame.grid_remove()
