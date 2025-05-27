"""
@file rich_text_editor_widget.py
@description Enhanced embeddable rich text editor widget with full RTF capabilities.
@author Daniel
@created 2024-06-11
@lastModified 2024-12-19
@dependencies PyQt6

A QWidget-based rich text editor with comprehensive formatting toolbar, image support,
table management, zoom controls, and all the features from the RTF editor window,
but designed for embedding in other widgets or dialogs.
"""

from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QTextCharFormat, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QTextEdit, QToolBar, QVBoxLayout, QWidget, QHBoxLayout, 
    QSplitter, QFrame, QStatusBar, QMenuBar, QMenu
)

# Import all the powerful components from the RTF editor system
from .format_toolbar import FormatToolBar
from .table_manager import TableManager
from .image_manager import ImageManager
from .zoom_manager import ZoomManager
from .commands import CommandHistory
from .document_manager import DocumentManager


class RichTextEditorWidget(QWidget):
    """
    @class RichTextEditorWidget
    @description Enhanced embeddable rich text editor with full RTF capabilities.

    This widget brings all the power of the RTF editor window into an embeddable
    component that can be used in dialogs, panels, or other widgets. It includes:
    
    - Advanced formatting toolbar with font controls, colors, alignment
    - Table creation and management
    - Image insertion and editing
    - Zoom controls
    - Undo/redo with command history
    - Document management capabilities
    - Menu system (optional)
    - Status bar with information
    
    The widget maintains the BaseRTFEditor protocol for consistent API.
    """

    # Signals
    content_changed = pyqtSignal()
    format_changed = pyqtSignal(QTextCharFormat)
    alignment_changed = pyqtSignal(Qt.AlignmentFlag)
    status_message = pyqtSignal(str)

    def __init__(self, parent=None, show_menubar=False, show_statusbar=True, 
                 compact_mode=False):
        """Initialize the enhanced rich text editor widget.
        
        Args:
            parent: Parent widget
            show_menubar: Whether to show the menu bar (default: False for embedding)
            show_statusbar: Whether to show the status bar (default: True)
            compact_mode: Whether to use compact layout (default: False)
        """
        super().__init__(parent)
        
        # Configuration
        self.show_menubar = show_menubar
        self.show_statusbar = show_statusbar
        self.compact_mode = compact_mode
        
        # State tracking
        self._is_modified = False
        
        # Initialize all components
        self._init_components()
        self._init_ui()
        self._setup_connections()
        self._setup_shortcuts()
        
        # Set up initial state
        self._update_status_bar()

    def _init_components(self):
        """Initialize all the powerful RTF editor components."""
        # Create the main text editor FIRST
        self.text_edit = QTextEdit(self)
        self.text_edit.setMinimumSize(400, 200)
        
        # Set up a nice default font
        default_font = QFont("Arial", 11)
        self.text_edit.document().setDefaultFont(default_font)
        
        # Command history for undo/redo
        self.command_history = CommandHistory()
        
        # Document manager (for advanced document operations) - now text_edit exists
        self.document_manager = DocumentManager(self)
        
        # Advanced formatting toolbar
        self.format_toolbar = FormatToolBar(self)
        
        # Table management
        self.table_manager = TableManager(self.text_edit)
        
        # Image management
        self.image_manager = ImageManager(self.text_edit, self)
        
        # Zoom management
        self.zoom_manager = ZoomManager(self.text_edit)

    def _init_ui(self):
        """Set up the user interface layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Optional menu bar
        if self.show_menubar:
            self.menubar = QMenuBar(self)
            self._setup_menubar()
            main_layout.addWidget(self.menubar)
        
        # Toolbar area
        if not self.compact_mode:
            # Full toolbar layout
            toolbar_frame = QFrame()
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(0, 0, 0, 0)
            toolbar_layout.setSpacing(2)
            
            # Format toolbar
            toolbar_layout.addWidget(self.format_toolbar)
            
            # Additional toolbar for view controls
            self.view_toolbar = QToolBar("View Controls")
            self.view_toolbar.setObjectName("ViewToolBar")
            
            # Add zoom controls to view toolbar
            self.view_toolbar.addWidget(self.zoom_manager)
            
            # Add table and image quick actions
            self._add_quick_actions_to_toolbar()
            
            toolbar_layout.addWidget(self.view_toolbar)
            main_layout.addWidget(toolbar_frame)
        else:
            # Compact mode - single toolbar
            compact_toolbar = QToolBar("Compact Formatting")
            self._setup_compact_toolbar(compact_toolbar)
            main_layout.addWidget(compact_toolbar)
        
        # Main editor area
        editor_frame = QFrame()
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(2, 2, 2, 2)
        
        # Add the text editor
        editor_layout.addWidget(self.text_edit)
        main_layout.addWidget(editor_frame)
        
        # Optional status bar
        if self.show_statusbar:
            self.status_bar = QStatusBar()
            self.status_bar.setMaximumHeight(25)
            
            # Add zoom controls to status bar if not in toolbar
            if self.compact_mode:
                self.status_bar.addPermanentWidget(self.zoom_manager)
            
            main_layout.addWidget(self.status_bar)

    def _setup_menubar(self):
        """Set up the menu bar with all RTF editor features."""
        # File menu
        file_menu = self.menubar.addMenu("&File")
        
        # New
        new_action = file_menu.addAction("&New")
        new_action.setShortcut("Ctrl+N")
        new_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        new_action.triggered.connect(self.new_document)
        
        file_menu.addSeparator()
        
        # Edit menu
        edit_menu = self.menubar.addMenu("&Edit")
        
        # Undo/Redo
        self.undo_action = edit_menu.addAction("&Undo")
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        
        self.redo_action = edit_menu.addAction("&Redo")
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        
        edit_menu.addSeparator()
        
        # Standard edit operations
        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        cut_action.triggered.connect(self.text_edit.cut)
        
        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        copy_action.triggered.connect(self.text_edit.copy)
        
        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        paste_action.triggered.connect(self.text_edit.paste)
        
        edit_menu.addSeparator()
        
        select_all_action = edit_menu.addAction("Select &All")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        select_all_action.triggered.connect(self.text_edit.selectAll)
        
        # Insert menu
        insert_menu = self.menubar.addMenu("&Insert")
        
        # Add image menu actions
        self.image_manager.add_menu_actions(self.menubar)
        
        # View menu
        view_menu = self.menubar.addMenu("&View")
        
        # Zoom submenu
        zoom_submenu = view_menu.addMenu("&Zoom")
        
        zoom_in_action = zoom_submenu.addAction("Zoom &In")
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        zoom_in_action.triggered.connect(self.zoom_manager.zoom_in)
        
        zoom_out_action = zoom_submenu.addAction("Zoom &Out")
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        zoom_out_action.triggered.connect(self.zoom_manager.zoom_out)
        
        zoom_submenu.addSeparator()
        
        reset_zoom_action = zoom_submenu.addAction("&Reset Zoom")
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        reset_zoom_action.triggered.connect(self.zoom_manager.reset_zoom)
        
        # Table menu
        self.menubar.addMenu(self.table_manager.get_table_menu())

    def _add_quick_actions_to_toolbar(self):
        """Add quick action buttons to the view toolbar."""
        self.view_toolbar.addSeparator()
        
        # Table quick actions
        insert_table_action = QAction("Insert Table", self)
        insert_table_action.setToolTip("Insert a new table")
        insert_table_action.triggered.connect(self.table_manager.insert_table)
        self.view_toolbar.addAction(insert_table_action)
        
        # Image quick actions
        insert_image_action = QAction("Insert Image", self)
        insert_image_action.setToolTip("Insert an image")
        insert_image_action.triggered.connect(self.image_manager.insert_image)
        self.view_toolbar.addAction(insert_image_action)
        
        self.view_toolbar.addSeparator()
        
        # Undo/Redo quick actions
        self.toolbar_undo_action = QAction("Undo", self)
        self.toolbar_undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.toolbar_undo_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.toolbar_undo_action.triggered.connect(self.undo)
        self.toolbar_undo_action.setEnabled(False)
        self.view_toolbar.addAction(self.toolbar_undo_action)
        
        self.toolbar_redo_action = QAction("Redo", self)
        self.toolbar_redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.toolbar_redo_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.toolbar_redo_action.triggered.connect(self.redo)
        self.toolbar_redo_action.setEnabled(False)
        self.view_toolbar.addAction(self.toolbar_redo_action)

    def _setup_compact_toolbar(self, toolbar):
        """Set up a compact toolbar with essential formatting controls."""
        # Font controls
        from PyQt6.QtWidgets import QFontComboBox, QComboBox
        
        font_combo = QFontComboBox()
        font_combo.currentFontChanged.connect(self._on_font_family_changed)
        toolbar.addWidget(font_combo)
        
        size_combo = QComboBox()
        size_combo.setEditable(True)
        sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48", "72"]
        size_combo.addItems(sizes)
        size_combo.setCurrentText("11")
        size_combo.currentTextChanged.connect(self._on_font_size_changed)
        toolbar.addWidget(size_combo)
        
        toolbar.addSeparator()
        
        # Basic formatting
        bold_action = QAction("Bold", self)
        bold_action.setCheckable(True)
        bold_action.setShortcut("Ctrl+B")
        bold_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        bold_action.triggered.connect(self._toggle_bold)
        toolbar.addAction(bold_action)
        
        italic_action = QAction("Italic", self)
        italic_action.setCheckable(True)
        italic_action.setShortcut("Ctrl+I")
        italic_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        italic_action.triggered.connect(self._toggle_italic)
        toolbar.addAction(italic_action)
        
        underline_action = QAction("Underline", self)
        underline_action.setCheckable(True)
        underline_action.setShortcut("Ctrl+U")
        underline_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        underline_action.triggered.connect(self._toggle_underline)
        toolbar.addAction(underline_action)
        
        toolbar.addSeparator()
        
        # Quick insert actions
        table_action = QAction("Table", self)
        table_action.triggered.connect(self.table_manager.insert_table)
        toolbar.addAction(table_action)
        
        image_action = QAction("Image", self)
        image_action.triggered.connect(self.image_manager.insert_image)
        toolbar.addAction(image_action)

    def _setup_connections(self):
        """Set up all signal connections."""
        # Text editor signals
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.text_edit.selectionChanged.connect(self._on_selection_changed)
        
        # Format toolbar signals
        if hasattr(self.format_toolbar, "format_changed"):
            self.format_toolbar.format_changed.connect(self._apply_format)
        if hasattr(self.format_toolbar, "alignment_changed"):
            self.format_toolbar.alignment_changed.connect(self._set_alignment)
        
        # Command history signals
        self.command_history.undo_available.connect(self._update_undo_action)
        self.command_history.redo_available.connect(self._update_redo_action)
        
        # Manager signals
        self.table_manager.table_modified.connect(self._on_text_changed)
        self.image_manager.content_changed.connect(self._on_text_changed)
        
        # Document manager signals
        self.document_manager.status_updated.connect(self._show_status_message)
        
        # Connect format toolbar to editor signals
        if hasattr(self.format_toolbar, "connect_to_editor_signals"):
            self.format_toolbar.connect_to_editor_signals()

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Zoom shortcuts
        zoom_in_shortcut = QKeySequence("Ctrl++")
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(zoom_in_shortcut)
        zoom_in_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        zoom_in_action.triggered.connect(self.zoom_manager.zoom_in)
        self.addAction(zoom_in_action)
        
        zoom_out_shortcut = QKeySequence("Ctrl+-")
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(zoom_out_shortcut)
        zoom_out_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        zoom_out_action.triggered.connect(self.zoom_manager.zoom_out)
        self.addAction(zoom_out_action)
        
        reset_zoom_shortcut = QKeySequence("Ctrl+0")
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut(reset_zoom_shortcut)
        reset_zoom_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        reset_zoom_action.triggered.connect(self.zoom_manager.reset_zoom)
        self.addAction(reset_zoom_action)

    # Event handlers
    def _on_text_changed(self):
        """Handle text change events."""
        self._is_modified = True
        self.content_changed.emit()
        self._update_status_bar()

    def _on_cursor_position_changed(self):
        """Handle cursor position changes."""
        self._update_status_bar()
        # Update format toolbar if available
        if hasattr(self.format_toolbar, "update_toolbar_state"):
            self.format_toolbar.update_toolbar_state()

    def _on_selection_changed(self):
        """Handle selection changes."""
        self._update_status_bar()

    def _apply_format(self, format_obj):
        """Apply formatting to selected text."""
        cursor = self.text_edit.textCursor()
        cursor.mergeCharFormat(format_obj)
        self.format_changed.emit(format_obj)

    def _set_alignment(self, alignment):
        """Set text alignment."""
        cursor = self.text_edit.textCursor()
        block_format = cursor.blockFormat()
        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)
        self.alignment_changed.emit(alignment)

    def _on_font_family_changed(self, font):
        """Handle font family changes in compact mode."""
        cursor = self.text_edit.textCursor()
        format_obj = QTextCharFormat()
        format_obj.setFontFamily(font.family())
        cursor.mergeCharFormat(format_obj)

    def _on_font_size_changed(self, size_text):
        """Handle font size changes in compact mode."""
        try:
            size = float(size_text)
            cursor = self.text_edit.textCursor()
            format_obj = QTextCharFormat()
            format_obj.setFontPointSize(size)
            cursor.mergeCharFormat(format_obj)
        except ValueError:
            pass

    def _toggle_bold(self):
        """Toggle bold formatting."""
        cursor = self.text_edit.textCursor()
        format_obj = cursor.charFormat()
        if format_obj.fontWeight() >= QFont.Weight.Bold:
            format_obj.setFontWeight(QFont.Weight.Normal)
        else:
            format_obj.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(format_obj)

    def _toggle_italic(self):
        """Toggle italic formatting."""
        cursor = self.text_edit.textCursor()
        format_obj = cursor.charFormat()
        format_obj.setFontItalic(not format_obj.fontItalic())
        cursor.mergeCharFormat(format_obj)

    def _toggle_underline(self):
        """Toggle underline formatting."""
        cursor = self.text_edit.textCursor()
        format_obj = cursor.charFormat()
        format_obj.setFontUnderline(not format_obj.fontUnderline())
        cursor.mergeCharFormat(format_obj)

    def _update_undo_action(self, available):
        """Update undo action availability."""
        if hasattr(self, 'undo_action'):
            self.undo_action.setEnabled(available)
        if hasattr(self, 'toolbar_undo_action'):
            self.toolbar_undo_action.setEnabled(available)

    def _update_redo_action(self, available):
        """Update redo action availability."""
        if hasattr(self, 'redo_action'):
            self.redo_action.setEnabled(available)
        if hasattr(self, 'toolbar_redo_action'):
            self.toolbar_redo_action.setEnabled(available)

    def _update_status_bar(self):
        """Update the status bar with current information."""
        if not self.show_statusbar or not hasattr(self, 'status_bar'):
            return
        
        cursor = self.text_edit.textCursor()
        
        # Get document statistics
        doc = self.text_edit.document()
        char_count = len(self.text_edit.toPlainText())
        word_count = len(self.text_edit.toPlainText().split())
        line_count = doc.lineCount()
        
        # Current position
        current_line = cursor.blockNumber() + 1
        current_col = cursor.columnNumber() + 1
        
        # Build status message
        status_parts = [
            f"Line {current_line}/{line_count}",
            f"Col {current_col}",
            f"Words: {word_count}",
            f"Chars: {char_count}"
        ]
        
        if self._is_modified:
            status_parts.insert(0, "Modified")
        
        status_text = " | ".join(status_parts)
        self.status_bar.showMessage(status_text)

    def _show_status_message(self, message):
        """Show a status message."""
        if self.show_statusbar and hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 3000)  # Show for 3 seconds
        self.status_message.emit(message)

    # Public API methods (BaseRTFEditor protocol)
    def set_html(self, html: str) -> None:
        """Set the content of the editor as HTML."""
        self.text_edit.setHtml(html)
        self._is_modified = False

    def get_html(self) -> str:
        """Get the content of the editor as HTML."""
        return self.text_edit.toHtml()

    def set_plain_text(self, text: str) -> None:
        """Set the content of the editor as plain text."""
        self.text_edit.setPlainText(text)
        self._is_modified = False

    def get_plain_text(self) -> str:
        """Get the content of the editor as plain text."""
        return self.text_edit.toPlainText()

    def is_modified(self) -> bool:
        """Check if the content has been modified since last save."""
        return self._is_modified

    def set_modified(self, modified: bool = True) -> None:
        """Set the modified state."""
        self._is_modified = modified
        self._update_status_bar()

    def get_text_edit(self):
        """Get the QTextEdit widget."""
        return self.text_edit

    # Additional public methods for enhanced functionality
    def new_document(self):
        """Create a new document."""
        self.text_edit.clear()
        self._is_modified = False
        self._update_status_bar()

    def undo(self):
        """Undo the last action."""
        if self.command_history.can_undo():
            self.command_history.undo()
        else:
            self.text_edit.undo()

    def redo(self):
        """Redo the last undone action."""
        if self.command_history.can_redo():
            self.command_history.redo()
        else:
            self.text_edit.redo()

    def insert_table(self, rows=3, cols=3):
        """Insert a table with specified dimensions."""
        self.table_manager.insert_table_with_size(rows, cols)

    def insert_image(self, image_path=None):
        """Insert an image."""
        if image_path:
            self.image_manager.insert_image_from_path(image_path)
        else:
            self.image_manager.insert_image()

    def set_zoom(self, zoom_level):
        """Set the zoom level (percentage)."""
        self.zoom_manager.set_zoom(zoom_level)

    def get_zoom(self):
        """Get the current zoom level."""
        return self.zoom_manager.current_zoom

    def set_compact_mode(self, compact):
        """Enable or disable compact mode (requires recreation)."""
        self.compact_mode = compact
        # Note: This would require recreating the widget to take effect

    def get_format_toolbar(self):
        """Get the format toolbar for external customization."""
        return self.format_toolbar

    def get_table_manager(self):
        """Get the table manager for advanced table operations."""
        return self.table_manager

    def get_image_manager(self):
        """Get the image manager for advanced image operations."""
        return self.image_manager

    def get_zoom_manager(self):
        """Get the zoom manager for zoom operations."""
        return self.zoom_manager
