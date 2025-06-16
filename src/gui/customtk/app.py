"""
CustomTkinter GUI Application for MnemoX
Modern, dark-themed desktop application with modular architecture.
"""

import customtkinter as ctk
import logging
import datetime
from .overview import OverviewTab
from .projects import ProjectsTab
from .config import (
    APISection, ProcessingSection, SearchSection, ChunkingSection,
    StorageSection, IntelligenceSection, LoggingSection
)
from .widgets import AboutDialog
from .components import ToastNotification
from .utils import center_window_on_screen

logger = logging.getLogger('mnemox.app')


class MnemoXGUI:
    """Main CustomTkinter GUI application."""
    
    def __init__(self, storage, embedding, memory, app_instance=None, tray_instance=None):
        self.storage = storage
        self.embedding = embedding
        self.memory = memory
        self.app = app_instance
        self.tray = tray_instance  # Referencia al tray para notificaciones
        
        # GUI state
        self.root = None
        self.current_tab = "overview"
        
        # Tab instances
        self.overview_tab = None
        self.projects_tab = None
        self.config_sections = {}
        
        # Toast notification system
        self.toast = None
        
        logger.info("CustomTkinter GUI inicializado")
    
    def setup_appearance(self):
        """Configure CustomTkinter appearance with system theme support."""
        # Configurar tema oscuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configurar para que Windows respete el tema oscuro
        try:
            import tkinter as tk
            # Intentar configurar el tema oscuro nativo en Windows
            if hasattr(tk, '_default_root') and tk._default_root:
                tk._default_root.tk.call('tk', 'windowingsystem')  # Test if tk is available
                
            # Configurar variables de entorno para tema oscuro
            import os
            os.environ['TK_THEME'] = 'dark'
            
        except Exception as e:
            logger.debug(f"Could not set native dark theme: {e}")
            
        logger.info("Dark theme configured for CustomTkinter")
    
    def create_main_window(self):
        """Crear la ventana principal con barra de título NATIVA."""
        self.root = ctk.CTk()
        
        # USAR BARRA NATIVA - No usar overrideredirect
        # self.root.overrideredirect(True)  # COMENTADO - Usar barra nativa
        
        # Configuración inicial
        self.window_width = 700
        self.window_height = 800
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Configurar título de ventana
        self.root.title("MnemoX")
        
        # Configurar icono
        self.setup_window_icon()
        
        # Configurar grid weights para layout responsivo
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)  # Content area should expand (navigation=0, content=1, status=2)
        
        # Crear componentes (SIN barra de título personalizada)
        self.create_navigation()
        self.create_content_area()
        self.create_status_bar()
        
        # Centrar ventana usando utilidades mejoradas
        self.center_window_improved()
        
        logger.info("Ventana principal creada con barra de título NATIVA")
    
    def setup_window_icon(self):
        """Configurar icono de ventana."""
        try:
            from pathlib import Path
            ico_path = Path(__file__).parent.parent.parent.parent / "logo.ico"
            if ico_path.exists():
                self.root.iconbitmap(str(ico_path))
                logger.info(f"Icono de ventana configurado: {ico_path}")
            else:
                logger.warning(f"Icono no encontrado: {ico_path}")
        except Exception as e:
            logger.warning(f"No se pudo configurar icono: {e}")
    
    def center_window_improved(self):
        """Centrar ventana usando utilidades mejoradas."""
        center_window_on_screen(self.root, self.window_width, self.window_height)
    
    def hide_window(self):
        """Hide window (available from tray)."""
        logger.info("Hiding GUI window - available from tray")
        if self.root:
            self.root.withdraw()  # Hide instead of destroy
            
        # Notify tray that GUI was hidden
        if self.tray and hasattr(self.tray, 'on_gui_hidden'):
            self.tray.on_gui_hidden()
    
    def on_window_close(self):
        """Manejar evento de cierre de ventana (X nativa)."""
        # En lugar de cerrar, ocultar la ventana
        self.hide_window()
        return "break"  # Prevenir cierre por defecto
    
    def set_tray_instance(self, tray_instance):
        """Configurar instancia del tray para notificaciones."""
        self.tray = tray_instance
        logger.debug("Instancia tray configurada en GUI")
    
    def show_window(self):
        """Show window (called from tray)."""
        logger.info("Showing GUI window")
        if self.root:
            self.root.deiconify()  # Show window
            self.root.lift()  # Bring to front
            self.root.focus_force()  # Give focus
    
    def bring_to_front(self):
        """Bring window to front if already visible."""
        if self.root:
            self.root.lift()
            self.root.focus_force()
            logger.info("GUI brought to front")
    
    def create_navigation(self):
        """Create navigation tabs - Overview, Projects, Configuration, and About."""
        nav_frame = ctk.CTkFrame(self.root, height=50, corner_radius=0)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)  # row=0 sin titlebar personalizada
        nav_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Overview button
        self.overview_btn = ctk.CTkButton(
            nav_frame,
            text="Overview",
            command=lambda: self.switch_tab("overview"),
            corner_radius=0,
            height=50
        )
        self.overview_btn.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        
        # Projects button
        self.projects_btn = ctk.CTkButton(
            nav_frame,
            text="Projects",
            command=lambda: self.switch_tab("projects"),
            corner_radius=0,
            height=50,
            fg_color="transparent"
        )
        self.projects_btn.grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        
        # Configuration button
        self.config_btn = ctk.CTkButton(
            nav_frame,
            text="Configuration",
            command=lambda: self.switch_tab("config"),
            corner_radius=0,
            height=50,
            fg_color="transparent"
        )
        self.config_btn.grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        
        # About button
        self.about_btn = ctk.CTkButton(
            nav_frame,
            text="About",
            command=self.show_about,
            corner_radius=0,
            height=50,
            fg_color="transparent"
        )
        self.about_btn.grid(row=0, column=3, sticky="ew", padx=1, pady=1)
    
    def create_content_area(self):
        """Create the main content area."""
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))  # navigation=0, content=1, status=2
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Create overview tab
        self.create_overview_content()
        
        # Create projects tab
        self.create_projects_content()
        
        # Create configuration tab
        self.create_config_content()
        
        # Show initial tab
        self.current_tab = "overview"
        self.overview_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.overview_btn.configure(fg_color=("gray75", "gray25"))
    
    def create_overview_content(self):
        """Create overview tab using OverviewTab module."""
        from src.config import config
        self.overview_tab = OverviewTab(
            self.content_frame, 
            self.storage, 
            self.embedding, 
            self.memory,
            config
        )
    
    def create_projects_content(self):
        """Create projects tab using ProjectsTab module."""
        from src.config import config
        self.projects_tab = ProjectsTab(
            self.content_frame, 
            self.storage, 
            self.embedding, 
            self.memory,
            config
        )
    
    def create_config_content(self):
        """Create configuration tab with all sections."""
        self.config_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.config_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.config_frame,
            text="Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 20))
        
        # Create all configuration sections
        from src.config import config
        
        self.config_sections["api"] = APISection(self.config_frame, config)
        self.config_sections["api"].grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        self.config_sections["processing"] = ProcessingSection(self.config_frame, config)
        self.config_sections["processing"].grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        
        self.config_sections["search"] = SearchSection(self.config_frame, config)
        self.config_sections["search"].grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        
        self.config_sections["chunking"] = ChunkingSection(self.config_frame, config)
        self.config_sections["chunking"].grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        
        self.config_sections["storage"] = StorageSection(self.config_frame, config)
        self.config_sections["storage"].grid(row=5, column=0, sticky="ew", padx=20, pady=5)
        
        self.config_sections["intelligence"] = IntelligenceSection(self.config_frame, config)
        self.config_sections["intelligence"].grid(row=6, column=0, sticky="ew", padx=20, pady=5)
        
        self.config_sections["logging"] = LoggingSection(self.config_frame, config)
        self.config_sections["logging"].grid(row=7, column=0, sticky="ew", padx=20, pady=5)
        
        # Action buttons
        self.create_config_actions()
    
    def create_config_actions(self):
        """Create configuration action buttons."""
        actions_frame = ctk.CTkFrame(self.config_frame)
        actions_frame.grid(row=8, column=0, sticky="ew", padx=20, pady=20)
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Reload config button
        reload_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Reload Config",
            command=self.reload_config,
            height=35
        )
        reload_btn.grid(row=0, column=0, padx=5, pady=10)
        
        # Save config button  
        save_btn = ctk.CTkButton(
            actions_frame,
            text="💾 Save Config",
            command=self.save_config,
            height=35
        )
        save_btn.grid(row=0, column=1, padx=5, pady=10)
        
        # Reset to defaults button
        reset_btn = ctk.CTkButton(
            actions_frame,
            text="⚠️ Reset Defaults",
            command=self.reset_to_defaults,
            height=35,
            fg_color=("#EF4444", "#DC2626")
        )
        reset_btn.grid(row=0, column=2, padx=5, pady=10)
    
    def create_status_bar(self):
        """Create status bar at bottom."""
        status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)  # navigation=0, content=1, status=2
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Last updated: Never",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    
    def switch_tab(self, tab_name):
        """Switch between tabs."""
        # Hide all tabs
        if self.overview_tab:
            self.overview_tab.grid_remove()
        if self.projects_tab:
            self.projects_tab.grid_remove()
        if hasattr(self, 'config_frame'):
            self.config_frame.grid_remove()
        
        # Reset button colors
        self.overview_btn.configure(fg_color="transparent")
        self.projects_btn.configure(fg_color="transparent")
        self.config_btn.configure(fg_color="transparent")
        self.about_btn.configure(fg_color="transparent")
        
        # Show selected tab and highlight button
        if tab_name == "overview":
            self.overview_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.overview_btn.configure(fg_color=("gray75", "gray25"))
            self.overview_tab.refresh_stats()
        elif tab_name == "projects":
            self.projects_tab.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.projects_btn.configure(fg_color=("gray75", "gray25"))
            self.projects_tab.refresh_projects_list()
        elif tab_name == "config":
            self.config_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.config_btn.configure(fg_color=("gray75", "gray25"))
            self.load_all_config_values()
        
        self.current_tab = tab_name
        self.update_status(f"Switched to {tab_name.title()}")
        logger.info(f"Switched to {tab_name} tab")
    
    def load_all_config_values(self):
        """Load configuration values into all sections."""
        for section in self.config_sections.values():
            if hasattr(section, 'load_values'):
                section.load_values()
        
        # Refresh API status
        if 'api' in self.config_sections:
            self.config_sections['api'].refresh_status()
    
    def reload_config(self):
        """Reload configuration from file."""
        try:
            from src.config import config
            config.load_config()
            self.load_all_config_values()
            self.update_status("Configuration reloaded from file")
            logger.info("Configuration reloaded")
        except Exception as e:
            self.update_status(f"Error reloading config: {e}")
            logger.error(f"Error reloading config: {e}")
    
    def save_config(self):
        """Save all pending configuration changes."""
        try:
            restart_needed = False
            total_changes = 0
            
            # Apply changes from all sections
            for section_name, section in self.config_sections.items():
                if hasattr(section, 'apply_changes'):
                    section_restart, changes = section.apply_changes()
                    if section_restart:
                        restart_needed = True
                    total_changes += len(changes)
            
            # Save the config file
            from src.config import config
            if config.save_config():
                if total_changes > 0:
                    if restart_needed:
                        self.show_restart_dialog(total_changes)
                    else:
                        self.update_status(f"Configuration saved - {total_changes} changes applied")
                        self.toast.show_success(f"Configuration saved! {total_changes} changes applied.")
                else:
                    self.update_status("No changes to save")
                    self.toast.show_info("No changes to save.")
            else:
                self.update_status("Error saving configuration")
                
        except Exception as e:
            self.update_status(f"Error saving config: {e}")
            logger.error(f"Error saving config: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults with styled confirmation."""
        from .components import ConfirmDialog
        
        def on_confirm():
            try:
                from src.config import config
                config._config = config._get_default_config()
                config.save_config()
                self.load_all_config_values()
                self.update_status("Configuration reset to defaults")
                self.toast.show_success("Configuration reset to defaults successfully")
                logger.info("Configuration reset to defaults")
            except Exception as e:
                self.update_status(f"Error resetting config: {e}")
                self.toast.show_error(f"Error resetting config: {e}")
                logger.error(f"Error resetting config: {e}")
        
        dialog = ConfirmDialog(
            self.root,
            title="Reset Configuration",
            message="Reset all configuration to defaults?\nThis action cannot be undone.",
            confirm_text="Reset",
            cancel_text="Cancel",
            icon="⚠️",
            danger=True
        )
        
        # Override the confirm method
        dialog.on_confirm = on_confirm
    
    def show_restart_dialog(self, changes_count):
        """Show dialog informing about required restart."""
        restart_dialog = ctk.CTkToplevel(self.root)
        restart_dialog.title("Restart Required")
        restart_dialog.geometry("400x200")
        restart_dialog.transient(self.root)
        restart_dialog.grab_set()
        
        # Center dialog
        restart_dialog.update_idletasks()
        x = (self.root.winfo_x() + self.root.winfo_width() // 2) - (400 // 2)
        y = (self.root.winfo_y() + self.root.winfo_height() // 2) - (200 // 2)
        restart_dialog.geometry(f"400x200+{x}+{y}")
        
        # Warning icon and message
        icon_label = ctk.CTkLabel(
            restart_dialog,
            text="⚠️",
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(20, 10))
        
        message_label = ctk.CTkLabel(
            restart_dialog,
            text=f"Configuration saved successfully!\n{changes_count} changes applied.\n\nSome changes require Claude Desktop to be restarted\nto take effect.",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        message_label.pack(pady=10)
        
        # OK button
        ok_btn = ctk.CTkButton(
            restart_dialog,
            text="OK",
            command=restart_dialog.destroy,
            width=100,
            height=35
        )
        ok_btn.pack(pady=20)
        
        self.update_status(f"Configuration saved - restart Claude Desktop to apply all changes")
    
    def show_about(self):
        """Show about dialog."""
        about_dialog = AboutDialog(self.root)
        about_dialog.show()
    
    def update_status(self, message):
        """Update status bar with message and timestamp."""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.status_label.configure(text=f"{message} - {timestamp}")
    
    def close_window(self):
        """Close application completely (called when exiting from tray)."""
        logger.info("Closing application completely")
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación GUI."""
        logger.info("Iniciando GUI CustomTkinter...")
        
        # Configurar apariencia
        self.setup_appearance()
        
        # Crear y mostrar ventana
        self.create_main_window()
        
        # Configurar protocolo de cierre para interceptar X nativa
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Inicializar sistema de toasts después de crear la ventana
        self.toast = ToastNotification(self.root)
        
        # Cargar datos iniciales
        if self.overview_tab:
            self.overview_tab.refresh_stats()
        
        self.update_status("GUI lista")
        
        # Iniciar loop principal
        logger.info("GUI lista, iniciando loop principal")
        self.root.mainloop()
        
        logger.info("GUI cerrada")


def run_gui_standalone(storage, embedding, memory, app_instance=None):
    """Run GUI as standalone application."""
    gui = MnemoXGUI(storage, embedding, memory, app_instance)
    gui.run()
