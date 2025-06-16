"""
Widgets package for MnemoX CustomTkinter GUI.
Unified styling system components.
"""

from .project_widget import ProjectWidget
from .dialogs import NewProjectDialog, AboutDialog
from .project_dialogs import EditProjectDialog, DeleteProjectDialog

__all__ = [
    'ProjectWidget', 
    'NewProjectDialog', 
    'AboutDialog',
    'EditProjectDialog',
    'DeleteProjectDialog'
]
