"""
Unified UI components for consistent MnemoX styling.
Base classes and components for maintaining visual consistency.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class MnemoXColors:
    """Unified color palette for MnemoX application."""
    
    # Primary colors
    PRIMARY = ("#3B82F6", "#60A5FA")
    PRIMARY_HOVER = ("#2563EB", "#3B82F6")
    
    # Success colors
    SUCCESS = ("#10B981", "#059669")
    SUCCESS_HOVER = ("#059669", "#047857")
    
    # Warning colors
    WARNING = ("#F59E0B", "#D97706")
    WARNING_HOVER = ("#D97706", "#B45309")
    
    # Error colors
    ERROR = ("#EF4444", "#DC2626")
    ERROR_HOVER = ("#DC2626", "#B91C1C")
    
    # Background colors
    BG_PRIMARY = ("gray90", "gray13")
    BG_SECONDARY = ("gray85", "gray20")
    BG_TERTIARY = ("gray80", "gray25")
    
    # Text colors
    TEXT_PRIMARY = ("gray10", "gray90")
    TEXT_SECONDARY = ("gray40", "gray60")
    TEXT_TERTIARY = ("gray60", "gray40")
    
    # Border colors
    BORDER_LIGHT = ("gray70", "gray30")
    BORDER_MEDIUM = ("gray60", "gray40")
    BORDER_DARK = ("gray50", "gray50")


class MnemoXFonts:
    """Unified typography for MnemoX application with lazy loading."""
    
    _fonts_cache = {}
    
    @classmethod
    def _get_font(cls, key, size, weight="normal", family=None):
        """Get or create font with caching."""
        cache_key = f"{key}_{size}_{weight}_{family}"
        if cache_key not in cls._fonts_cache:
            cls._fonts_cache[cache_key] = ctk.CTkFont(
                size=size, 
                weight=weight,
                family=family if family else None
            )
        return cls._fonts_cache[cache_key]
    
    # Headers
    @classmethod
    def get_header_large(cls):
        return cls._get_font("header_large", 18, "bold")
    
    @classmethod
    def get_header_medium(cls):
        return cls._get_font("header_medium", 16, "bold")
    
    @classmethod
    def get_header_small(cls):
        return cls._get_font("header_small", 14, "bold")
    
    # Body text
    @classmethod
    def get_body_large(cls):
        return cls._get_font("body_large", 12, "normal")
    
    @classmethod
    def get_body_medium(cls):
        return cls._get_font("body_medium", 11, "normal")
    
    @classmethod
    def get_body_small(cls):
        return cls._get_font("body_small", 10, "normal")
    
    # UI elements
    @classmethod
    def get_button_large(cls):
        return cls._get_font("button_large", 12, "bold")
    
    @classmethod
    def get_button_medium(cls):
        return cls._get_font("button_medium", 11, "bold")
    
    @classmethod
    def get_button_small(cls):
        return cls._get_font("button_small", 10, "bold")
    
    # Special
    @classmethod
    def get_monospace(cls):
        return cls._get_font("monospace", 10, "normal", "Consolas")
    
    # Legacy properties for backward compatibility
    @property
    def HEADER_LARGE(self):
        return self.get_header_large()
    
    @property
    def HEADER_MEDIUM(self):
        return self.get_header_medium()
    
    @property
    def HEADER_SMALL(self):
        return self.get_header_small()
    
    @property
    def BODY_LARGE(self):
        return self.get_body_large()
    
    @property
    def BODY_MEDIUM(self):
        return self.get_body_medium()
    
    @property
    def BODY_SMALL(self):
        return self.get_body_small()
    
    @property
    def BUTTON_LARGE(self):
        return self.get_button_large()
    
    @property
    def BUTTON_MEDIUM(self):
        return self.get_button_medium()
    
    @property
    def BUTTON_SMALL(self):
        return self.get_button_small()
    
    @property
    def MONOSPACE(self):
        return self.get_monospace()


class BaseDialog(ctk.CTkToplevel):
    """Base dialog class with consistent MnemoX styling."""
    
    def __init__(
        self, 
        parent, 
        title: str,
        width: int = 400,
        height: int = 300,
        resizable: bool = False
    ):
        super().__init__(parent)
        
        self.parent = parent
        self.result = None
        
        # Configure window with NATIVE titlebar
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(resizable, resizable)
        self.transient(parent)
        self.grab_set()
        
        # Configure styling to match main window
        self.configure(fg_color=MnemoXColors.BG_PRIMARY)
        
        # Center on parent
        self.center_on_parent()
        
        # Create content frame (to be implemented by subclasses)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create button frame
        self.create_button_frame()
        
        # Focus handling
        self.focus()
    
    def center_on_parent(self):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (self.winfo_width() // 2)
        y = parent_y + (parent_height // 2) - (self.winfo_height() // 2)
        
        self.geometry(f"+{x}+{y}")
    
    def create_button_frame(self):
        """Create button frame at bottom."""
        self.button_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.button_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        self.button_frame.pack_propagate(False)
        
        # Button container (centered)
        button_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        button_container.pack(expand=True)
    
    # Removed set_icon method since we don't have custom header
    
    def add_button(
        self, 
        text: str, 
        command: Callable, 
        style: str = "primary",
        side: str = "right"
    ) -> ctk.CTkButton:
        """Add button to dialog."""
        # Color scheme based on style
        if style == "primary":
            fg_color = MnemoXColors.PRIMARY
            hover_color = MnemoXColors.PRIMARY_HOVER
        elif style == "success":
            fg_color = MnemoXColors.SUCCESS
            hover_color = MnemoXColors.SUCCESS_HOVER
        elif style == "warning":
            fg_color = MnemoXColors.WARNING
            hover_color = MnemoXColors.WARNING_HOVER
        elif style == "error":
            fg_color = MnemoXColors.ERROR
            hover_color = MnemoXColors.ERROR_HOVER
        else:  # secondary
            fg_color = "transparent"
            hover_color = MnemoXColors.BG_TERTIARY
        
        button = ctk.CTkButton(
            self.button_frame,
            text=text,
            command=command,
            width=100,
            height=35,
            font=MnemoXFonts.get_button_medium(),
            fg_color=fg_color,
            hover_color=hover_color
        )
        
        if side == "right":
            button.pack(side="right", padx=(10, 20), pady=12)
        else:
            button.pack(side="left", padx=(20, 10), pady=12)
        
        return button
    
    def on_cancel(self):
        """Handle cancel/close."""
        self.result = None
        self.destroy()
    
    def on_confirm(self):
        """Handle confirm (to be overridden)."""
        self.result = True
        self.destroy()


class ToastNotification:
    """Sistema de notificaciones toast mejorado para MnemoX."""
    
    def __init__(self, parent):
        self.parent = parent
        self.active_toasts = []
        
        logger.debug("Sistema de toasts inicializado")
    
    def show_toast(
        self, 
        message: str, 
        toast_type: str = "info",
        duration: int = 3000
    ):
        """Mostrar toast notification con centrado mejorado."""
        toast = EnhancedToast(self.parent, message, toast_type, duration)
        self.active_toasts.append(toast)
        
        # Configurar callback para remoción
        toast.set_removal_callback(lambda t: self._remove_toast(t))
        
        logger.debug(f"Toast mostrado: {toast_type} - {message}")
    
    def _remove_toast(self, toast):
        """Remover toast del stack."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self._reposition_remaining_toasts()
    
    def _reposition_remaining_toasts(self):
        """Reposicionar toasts restantes usando coordenadas reales."""
        from .utils import get_scaling_factor
        
        for i, toast in enumerate(self.active_toasts):
            if hasattr(toast, 'reposition'):
                toast.reposition(i)
    
    def show_success(self, message: str):
        """Mostrar toast de éxito."""
        self.show_toast(message, "success")
    
    def show_warning(self, message: str):
        """Mostrar toast de advertencia."""
        self.show_toast(message, "warning")
    
    def show_error(self, message: str):
        """Mostrar toast de error."""
        self.show_toast(message, "error")
    
    def show_info(self, message: str):
        """Mostrar toast de información."""
        self.show_toast(message, "info")


class EnhancedToast(ctk.CTkToplevel):
    """Toast mejorado con centrado real usando scaling."""
    
    def __init__(self, parent, message, toast_type="info", duration=3000):
        super().__init__(parent)
        
        self.parent = parent
        self.duration = duration
        self.removal_callback = None
        
        # Sin barra nativa
        self.overrideredirect(True)
        
        # Configurar ventana
        self.geometry("300x70")
        self.transient(parent)
        self.attributes('-topmost', True)
        
        # Colores según tipo
        colors = {
            "success": "#10B981",
            "error": "#EF4444", 
            "warning": "#F59E0B",
            "info": "#3B82F6"
        }
        
        color = colors.get(toast_type, colors["info"])
        self.configure(fg_color=color)
        
        self.create_content(message)
        self.position_toast()
        
        # Auto-cerrar
        self.after(duration, self.close_toast)
    
    def create_content(self, message):
        """Crear contenido del toast."""
        # Frame principal con padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Mensaje centrado
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="white",
            wraplength=220,
            justify="center"
        )
        message_label.pack(side="left", fill="both", expand=True)
        
        # Botón cerrar discreto
        close_btn = ctk.CTkButton(
            main_frame,
            text="×",
            width=18,
            height=18,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("white", "gray20"),
            text_color="white",
            command=self.close_toast
        )
        close_btn.pack(side="right", padx=(8, 0))
    
    def position_toast(self):
        """Posicionar toast centrado horizontalmente usando coordenadas reales."""
        from .utils import get_scaling_factor
        
        # Forzar actualización
        self.update()
        
        # Detectar factor de scaling
        scaling_factor = get_scaling_factor(self)
        
        # Obtener dimensiones de pantalla (lógicas)
        screen_width_logical = self.winfo_screenwidth()
        
        # Calcular dimensiones reales
        screen_width_real = int(screen_width_logical * scaling_factor)
        
        # Obtener índice en el stack
        parent_instance = getattr(self.parent, 'toast', None)
        toast_index = 0
        if parent_instance and hasattr(parent_instance, 'active_toasts'):
            try:
                toast_index = parent_instance.active_toasts.index(self)
            except ValueError:
                toast_index = len(parent_instance.active_toasts)
        
        # USAR COORDENADAS REALES DIRECTAMENTE (corrección del POC)
        x_real = (screen_width_real - 300) // 2
        y_real = 20 + (toast_index * 80)
        
        self.geometry(f"300x70+{x_real}+{y_real}")
        
        logger.debug(f"Toast posicionado: x={x_real}, y={y_real} (index={toast_index}, scaling={scaling_factor})")
    
    def reposition(self, new_index):
        """Reposicionar toast en nueva posición del stack."""
        from .utils import get_scaling_factor
        
        scaling_factor = get_scaling_factor(self)
        screen_width_logical = self.winfo_screenwidth()
        screen_width_real = int(screen_width_logical * scaling_factor)
        
        x_real = (screen_width_real - 300) // 2
        y_real = 20 + (new_index * 80)
        
        self.geometry(f"300x70+{x_real}+{y_real}")
    
    def set_removal_callback(self, callback):
        """Configurar callback para remoción."""
        self.removal_callback = callback
    
    def close_toast(self):
        """Cerrar toast."""
        try:
            if self.removal_callback:
                self.removal_callback(self)
            self.destroy()
        except Exception as e:
            logger.warning(f"Error cerrando toast: {e}")


class ConfirmDialog(BaseDialog):
    """Confirmation dialog with consistent styling."""
    
    def __init__(
        self, 
        parent, 
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        icon: str = "❓",
        danger: bool = False
    ):
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.danger = danger
        
        super().__init__(parent, title, width=450, height=250)
        
        self.set_icon(icon)
        self.create_content()
        self.create_buttons()
    
    def create_content(self):
        """Create dialog content."""
        # Message
        message_label = ctk.CTkLabel(
            self.content_frame,
            text=self.message,
            font=MnemoXFonts.get_body_large(),
            text_color=MnemoXColors.TEXT_PRIMARY,
            wraplength=380,
            justify="center"
        )
        message_label.pack(expand=True, pady=20)
    
    def create_buttons(self):
        """Create dialog buttons."""
        # Cancel button
        self.add_button(
            self.cancel_text,
            self.on_cancel,
            style="secondary",
            side="left"
        )
        
        # Confirm button
        style = "error" if self.danger else "primary"
        self.add_button(
            self.confirm_text,
            self.on_confirm,
            style=style,
            side="right"
        )


class ProjectDialog(ctk.CTkToplevel):
    """Diálogo para crear/editar proyectos con ventana NATIVA."""
    
    def __init__(self, parent, title="Proyecto", project_data=None, on_save=None):
        super().__init__(parent)
        
        self.project_data = project_data or {}
        self.on_save_callback = on_save
        self.result = None
        
        # USAR VENTANA NATIVA - No overrideredirect
        # self.overrideredirect(True)  # REMOVIDO - Usar barra nativa
        
        # Configuración básica con tamaño FIJO
        self.title(title)
        self.geometry("500x400")  # Aumentar altura para que se vean los botones
        self.minsize(500, 400)   # Tamaño mínimo
        self.transient(parent)
        self.grab_set()
        
        # Aplicar tema consistente con ventana principal
        self.configure(fg_color=("gray90", "gray13"))  # Mismo que main window
        
        # Centrar en ventana padre
        self.center_on_parent(parent)
        
        # Solo crear contenido (sin header personalizado)
        self.create_content()
    
    def center_on_parent(self, parent):
        """Centrar en ventana padre con mejor control."""
        # Forzar actualización de geometría
        self.update_idletasks()
        
        # Obtener dimensiones de la ventana padre
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y() 
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Obtener dimensiones de esta ventana
        dialog_width = self.winfo_reqwidth()
        dialog_height = self.winfo_reqheight()
        
        # Si las dimensiones no están listas, usar valores por defecto
        if dialog_width <= 1:
            dialog_width = 500
        if dialog_height <= 1:
            dialog_height = 400
            
        # Calcular posición centrada
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        # Asegurar que la ventana esté dentro de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Ajustar si está fuera de pantalla
        if x < 0:
            x = 50
        if y < 0:
            y = 50
        if x + dialog_width > screen_width:
            x = screen_width - dialog_width - 50
        if y + dialog_height > screen_height:
            y = screen_height - dialog_height - 50
            
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Forzar segunda actualización después del posicionamiento
        self.update_idletasks()
    
    def create_content(self):
        """Crear contenido del diálogo."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nombre del proyecto
        name_label = ctk.CTkLabel(
            content,
            text="Project Name:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            content,
            placeholder_text="Enter project name...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Descripción
        desc_label = ctk.CTkLabel(
            content,
            text="Description (optional):",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        desc_label.pack(anchor="w", pady=(0, 5))
        
        self.desc_textbox = ctk.CTkTextbox(
            content,
            height=120,
            font=ctk.CTkFont(size=11)
        )
        self.desc_textbox.pack(fill="both", expand=True, pady=(0, 20))
        
        # Cargar datos existentes si es edición
        if self.project_data:
            self.name_entry.insert(0, self.project_data.get('name', ''))
            self.desc_textbox.insert("1.0", self.project_data.get('description', ''))
        
        # Botones de acción
        self.create_action_buttons(content)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción."""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Botón cancelar
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel_action,
            width=120,
            height=35,
            fg_color="transparent",
            border_width=1
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Botón guardar
        save_text = "Update" if self.project_data else "Create"
        save_btn = ctk.CTkButton(
            btn_frame,
            text=save_text,
            command=self.save_action,
            width=120,
            height=35
        )
        save_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
    
    def save_action(self):
        """Acción de guardar."""
        name = self.name_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end-1c").strip()
        
        if not name:
            # Aquí se podría mostrar un toast de error
            return
        
        self.result = {
            'name': name,
            'description': description
        }
        
        if self.on_save_callback:
            self.on_save_callback(self.result)
        
        self.destroy()
    
    def cancel_action(self):
        """Acción de cancelar."""
        self.result = None
        self.destroy()
