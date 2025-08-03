"""
Breadcrumb Address Bar Library

A breadcrumb-style address bar for PySide6/PyQt6 file managers.
"""

from .core import BreadcrumbAddressBar
from .popup import FolderSelectionPopup
from .themes import ThemeManager, get_theme_manager
from .widgets import BreadcrumbItem

__version__ = "0.2.2"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "BreadcrumbAddressBar",
    "BreadcrumbItem",
    "FolderSelectionPopup",
    "ThemeManager",
    "get_theme_manager",
]
