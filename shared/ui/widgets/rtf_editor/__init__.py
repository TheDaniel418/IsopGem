# RTF Editor Package

"""RTF Editor package for handling rich text editing functionality."""

"""RTF Editor package components."""

# This file makes the rtf_editor directory a Python package

"""
Purpose: Provides a rich text editor component with stable table and image handling.

This file is part of the shared UI widgets pillar and serves as a reusable component.
It provides rich text editing capabilities with full support for formatting,
tables, images, and custom annotations.

Key components:
- RTFEditorWindow: Main rich text editor window
- DocumentFormat: Model for document serialization and storage

Dependencies:
- PyQt6: For UI components
"""

from .document_manager import DocumentManager
from .format_toolbar import FormatToolBar
from .image_manager import ImageManager
from .models import AnnotationMetadata, DocumentFormat, ImageMetadata, TableMetadata
from .rtf_editor_window import RTFEditorWindow
from .table_manager import TableManager
from .zoom_manager import ZoomManager

# Export main classes
__all__ = [
    "RTFEditorWindow",
    "FormatToolBar",
    "TableManager",
    "ImageManager",
    "ZoomManager",
    "DocumentManager",
    "DocumentFormat",
    "AnnotationMetadata",
    "ImageMetadata",
    "TableMetadata",
]
