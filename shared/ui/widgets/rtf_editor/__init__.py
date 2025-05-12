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
- RichTextEditorWidget: Lightweight embeddable rich text editor
- BaseRTFEditor: Abstract base class defining editor interface
- DocumentFormat: Model for document serialization and storage
- CommandHistory: Command pattern implementation for undo/redo

Dependencies:
- PyQt6: For UI components
"""

from .base_rtf_editor import BaseRTFEditor
from .commands import (
    AlignmentCommand,
    Command,
    CommandHistory,
    DeleteTextCommand,
    FormatCommand,
    InsertImageCommand,
    InsertTextCommand,
    TextCommand,
)
from .document_manager import DocumentManager
from .format_toolbar import FormatToolBar
from .image_manager import ImageManager
from .models import AnnotationMetadata, DocumentFormat, ImageMetadata, TableMetadata
from .rich_text_editor_widget import RichTextEditorWidget
from .rtf_editor_window import RTFEditorWindow
from .table_manager import TableManager

# Include utility classes
from .utils import ImageUtils, StyleMappingsUtils, TextFormattingUtils
from .zoom_manager import ZoomManager

# Export main classes
__all__ = [
    "RTFEditorWindow",
    "RichTextEditorWidget",
    "BaseRTFEditor",
    "FormatToolBar",
    "TableManager",
    "ImageManager",
    "ZoomManager",
    "DocumentManager",
    "DocumentFormat",
    "AnnotationMetadata",
    "ImageMetadata",
    "TableMetadata",
    "Command",
    "CommandHistory",
    "TextCommand",
    "InsertTextCommand",
    "DeleteTextCommand",
    "FormatCommand",
    "AlignmentCommand",
    "InsertImageCommand",
    "TextFormattingUtils",
    "StyleMappingsUtils",
    "ImageUtils",
]
