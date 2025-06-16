"""
Utility functions for MnemoX GUI.
Cross-platform helpers and common functionality.
"""

import platform
import logging

logger = logging.getLogger(__name__)


def get_scaling_factor(window):
    """
    Detectar factor de scaling de manera segura multiplataforma.
    
    Args:
        window: Ventana tkinter/customtkinter para referencia
        
    Returns:
        float: Factor de scaling (1.0 = sin scaling, 1.75 = 175%, etc.)
    """
    try:
        system = platform.system()
        logger.debug(f"Sistema operativo detectado: {system}")
        
        if system == "Windows":
            # Windows: usar ctypes para obtener factor real
            from ctypes import windll
            scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100
            logger.debug(f"Windows scaling factor (ctypes): {scale_factor}")
            return scale_factor
        else:
            # Mac/Linux: usar método estándar de tkinter
            current_dpi = window.winfo_fpixels('1i')
            scale_factor = current_dpi / 96
            logger.debug(f"{system} DPI: {current_dpi}, scaling factor: {scale_factor}")
            return scale_factor
    except Exception as e:
        logger.warning(f"Error detectando scaling: {e}, usando fallback 1.0")
        # Fallback: sin scaling
        return 1.0


def center_window_on_screen(window, width, height):
    """
    Centrar ventana en pantalla considerando scaling.
    
    Args:
        window: Ventana a centrar
        width: Ancho deseado
        height: Alto deseado
    """
    try:
        window.update_idletasks()
        
        # Obtener dimensiones de pantalla
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calcular posición centrada
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
        logger.debug(f"Ventana centrada: {width}x{height}+{x}+{y}")
        
    except Exception as e:
        logger.warning(f"Error centrando ventana: {e}")
