"""
Utilidades para la GUI de MnemoX.
Funciones helper migradas desde test_complete_poc.py
"""

import platform


def get_scaling_factor(window):
    """Detectar factor de scaling de manera segura multiplataforma."""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows: usar ctypes para obtener factor real
            from ctypes import windll
            scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100
            return scale_factor
        else:
            # Mac/Linux: usar método estándar de tkinter
            current_dpi = window.winfo_fpixels('1i')
            scale_factor = current_dpi / 96
            return scale_factor
    except Exception as e:
        # Fallback: sin scaling
        return 1.0


def center_window_on_screen(window, width, height):
    """Centrar ventana en pantalla."""
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
