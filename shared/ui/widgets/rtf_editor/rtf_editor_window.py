from datetime import datetime
from pathlib import Path

from loguru import logger
from PIL import Image
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import (
    QAction,
    QFont,
    QKeySequence,
    QTextCursor,
    QTextFormat,
    QTextImageFormat,
)
from PyQt6.QtWidgets import (
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .commands import (
    AlignmentCommand,
    CommandHistory,
    FormatCommand,
    InsertImageCommand,
)
from .document_manager import DocumentManager
from .format_toolbar import FormatToolBar
from .image_editor_dialog import ImageEditorDialog
from .image_manager import ImageManager
from .image_properties_dialog import ImagePropertiesDialog
from .table_manager import TableManager
from .zoom_manager import ZoomManager


class RTFEditorWindow(QMainWindow):
    """Main RTF editor window with full editing capabilities.

    This class serves as the main window for the RTF editor application, integrating all components:
    - Text editing area (QTextEdit)
    - Document management (loading, saving)
    - Formatting controls (toolbar and menu options)
    - Table operations
    - Image handling
    - Zoom controls
    - Undo/redo history

    It provides a complete rich text editing experience with support for text formatting,
    tables, images, and document management.

    Attributes:
        text_edit (QTextEdit): The main text editing widget
        document_manager (DocumentManager): Handles document operations
        table_manager (TableManager): Handles table operations
        image_manager (ImageManager): Handles image operations
        format_toolbar (FormatToolBar): Provides text formatting controls
        zoom_manager (ZoomManager): Handles zoom operations
        command_history (CommandHistory): Manages undo/redo operations
    """

    def __init__(self, parent=None):
        """Initialize the RTF editor window.

        Creates the main editor window and initializes all components.
        Sets up the UI, menus, toolbars, and connects signals.

        Args:
            parent (QWidget, optional): Parent widget for this window

        Returns:
            None
        """
        # Set up exception handling for the entire application
        self.setup_exception_handling()

        # Set window flags to ensure this window stays on top
        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        super().__init__(parent, flags)

        self.setWindowTitle("RTF Editor")
        self.resize(800, 600)

        # Enable delete on close to ensure proper cleanup
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize components
        self.setup_ui()

        # Initialize command history for undo/redo
        self.command_history = CommandHistory()

        # Initialize document and content managers
        self.document_manager = DocumentManager(self)
        self.table_manager = TableManager(self.text_edit)
        self.setup_menubar()
        self.setup_toolbars()

        # Initialize image manager with document ID from document manager
        document_id = None
        if hasattr(self, "document_manager") and hasattr(
            self.document_manager, "document_id"
        ):
            document_id = self.document_manager.document_id

        self.image_manager = ImageManager(self.text_edit, self, document_id)
        self.image_manager.add_menu_actions(self.menuBar())

        # Connect command history signals to UI updates
        self.command_history.undo_available.connect(self._update_undo_action)
        self.command_history.redo_available.connect(self._update_redo_action)

        # Connect signals
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.text_edit.selectionChanged.connect(self.on_selection_changed)
        self.table_manager.table_modified.connect(self.on_text_changed)
        self.image_manager.content_changed.connect(self.on_text_changed)

        # Connect document manager signals
        self.document_manager.status_updated.connect(self.show_status_message)
        self.document_manager.auto_save_completed.connect(self.on_auto_save_completed)

        # Install event filter on the text editor's viewport
        self.text_edit.viewport().installEventFilter(self)

        # Connect to text edit's document signals for tracking changes
        self.setup_document_change_tracking()

        # Setup keyboard shortcuts for zoom
        self.setup_zoom_shortcuts()

    def setup_ui(self):
        """Set up the main UI components.

        Creates and configures the central widget, layout, and text editor.
        Sets up the status bar and ensures all components are properly visible.

        Returns:
            None
        """
        logger.debug("Setting up RTF Editor UI components...")

        # Central widget
        central_widget = QWidget()
        central_widget.setVisible(True)
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Text editor with strong visibility settings
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumSize(400, 300)  # Ensure minimum size
        self.text_edit.setVisible(True)  # Explicitly make visible
        self.text_edit.setEnabled(True)

        # Set background color to make it obvious when it's rendered
        self.text_edit.setStyleSheet("background-color: white; color: black;")

        # Set up a default document with basic formatting
        self.text_edit.document().setDefaultFont(QFont("Arial", 11))

        # Add to layout
        layout.addWidget(self.text_edit)
        logger.debug("Added text_edit to layout")

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add zoom manager to status bar
        self.zoom_manager = ZoomManager(self.text_edit)
        self.status_bar.addPermanentWidget(self.zoom_manager)

        self.update_status_bar()
        logger.debug("RTF Editor UI setup complete")

    def setup_toolbars(self):
        """Set up formatting toolbars.

        Creates and configures the formatting toolbar and view toolbar.
        Connects toolbar signals to appropriate slots and adds them to the window.

        Returns:
            None
        """
        # Create and add the format toolbar
        self.format_toolbar = FormatToolBar(self)
        self.addToolBar(self.format_toolbar)

        # Connect format toolbar signals to text editor
        if hasattr(self.format_toolbar, "format_changed"):
            self.format_toolbar.format_changed.connect(self.apply_format)
        if hasattr(self.format_toolbar, "alignment_changed"):
            self.format_toolbar.alignment_changed.connect(self.set_alignment)

        # Ensure the format toolbar is connected to the text editor signals
        if hasattr(self.format_toolbar, "connect_to_editor_signals"):
            self.format_toolbar.connect_to_editor_signals()

        # Create view toolbar with zoom controls
        self.view_toolbar = QToolBar("View")
        self.view_toolbar.setObjectName("ViewToolBar")

        # Add zoom controls to view toolbar
        self.view_toolbar.addWidget(self.zoom_manager)

        # Add view toolbar to window
        self.addToolBar(self.view_toolbar)

    def setup_menubar(self):
        """Set up the menu bar with file, edit, and table operations."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New
        new_action = file_menu.addAction("&New")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.document_manager.new_document)

        # Open
        open_action = file_menu.addAction("&Open...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.document_manager.open_document)

        # Save
        save_action = file_menu.addAction("&Save")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.document_manager.save_document)

        # Save As
        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.document_manager.save_document_as)

        # Set Title (for notes)
        set_title_action = file_menu.addAction("Set &Title...")
        set_title_action.setShortcut("Ctrl+T")
        set_title_action.triggered.connect(self.set_document_title)

        # Add separator
        file_menu.addSeparator()

        # Recover Documents
        recover_action = file_menu.addAction("&Recover Documents...")
        recover_action.triggered.connect(self.show_recovery_dialog)

        # Add Edit menu with undo/redo
        edit_menu = menubar.addMenu("&Edit")

        # Undo
        self.undo_action = edit_menu.addAction("&Undo")
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)

        # Redo
        self.redo_action = edit_menu.addAction("&Redo")
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)

        edit_menu.addSeparator()

        # Cut
        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.text_edit.cut)

        # Copy
        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.text_edit.copy)

        # Paste
        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.text_edit.paste)

        edit_menu.addSeparator()

        # Select All
        select_all_action = edit_menu.addAction("Select &All")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.text_edit.selectAll)

        # Ensure Insert Menu exists (can be added to by managers)
        insert_menu = menubar.findChild(QMenu, "&Insert")
        if not insert_menu:
            insert_menu = menubar.addMenu("&Insert")

        # Add View menu
        view_menu = menubar.addMenu("&View")

        # Zoom actions
        zoom_submenu = view_menu.addMenu("&Zoom")

        zoom_in_action = zoom_submenu.addAction("Zoom &In")
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_manager.zoom_in)

        zoom_out_action = zoom_submenu.addAction("Zoom &Out")
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_manager.zoom_out)

        zoom_submenu.addSeparator()

        # Add specific zoom level actions
        zoom_50_action = zoom_submenu.addAction("50%")
        zoom_50_action.setShortcut("Ctrl+5")
        zoom_50_action.triggered.connect(lambda: self.zoom_manager.set_zoom(50))

        zoom_75_action = zoom_submenu.addAction("75%")
        zoom_75_action.setShortcut("Ctrl+4")
        zoom_75_action.triggered.connect(lambda: self.zoom_manager.set_zoom(75))

        zoom_100_action = zoom_submenu.addAction("100%")
        zoom_100_action.setShortcut("Ctrl+1")
        zoom_100_action.triggered.connect(lambda: self.zoom_manager.set_zoom(100))

        zoom_150_action = zoom_submenu.addAction("150%")
        zoom_150_action.setShortcut("Ctrl+2")
        zoom_150_action.triggered.connect(lambda: self.zoom_manager.set_zoom(150))

        zoom_200_action = zoom_submenu.addAction("200%")
        zoom_200_action.setShortcut("Ctrl+3")
        zoom_200_action.triggered.connect(lambda: self.zoom_manager.set_zoom(200))

        zoom_submenu.addSeparator()

        reset_zoom_action = zoom_submenu.addAction("&Reset Zoom")
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.zoom_manager.reset_zoom)

        # Add toggle actions for toolbars
        view_menu.addSeparator()

        # Toggle Format Toolbar action
        toggle_format_toolbar = view_menu.addAction("Show Format &Toolbar")
        toggle_format_toolbar.setCheckable(True)
        toggle_format_toolbar.setChecked(True)
        toggle_format_toolbar.triggered.connect(
            lambda checked: self.format_toolbar.setVisible(checked)
        )

        # Toggle View Toolbar action
        toggle_view_toolbar = view_menu.addAction("Show &View Toolbar")
        toggle_view_toolbar.setCheckable(True)
        toggle_view_toolbar.setChecked(True)
        toggle_view_toolbar.triggered.connect(
            lambda checked: self.view_toolbar.setVisible(checked)
        )

        # Table menu
        menubar.addMenu(self.table_manager.get_table_menu())

    def setup_zoom_shortcuts(self):
        """Set up additional keyboard shortcuts for zooming."""
        # These shortcuts will be active throughout the application

        # Ctrl+Plus for zoom in
        zoom_in_shortcut = QKeySequence("Ctrl++")
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(zoom_in_shortcut)
        zoom_in_action.triggered.connect(self.zoom_manager.zoom_in)
        self.addAction(zoom_in_action)

        # Ctrl+Minus for zoom out
        zoom_out_shortcut = QKeySequence("Ctrl+-")
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(zoom_out_shortcut)
        zoom_out_action.triggered.connect(self.zoom_manager.zoom_out)
        self.addAction(zoom_out_action)

        # Ctrl+0 for reset zoom (100%)
        reset_zoom_shortcut = QKeySequence("Ctrl+0")
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut(reset_zoom_shortcut)
        reset_zoom_action.triggered.connect(self.zoom_manager.reset_zoom)
        self.addAction(reset_zoom_action)

        # Direct zoom level shortcuts

        # Ctrl+1 for 100% zoom
        zoom_100_shortcut = QKeySequence("Ctrl+1")
        zoom_100_action = QAction("Zoom 100%", self)
        zoom_100_action.setShortcut(zoom_100_shortcut)
        zoom_100_action.triggered.connect(lambda: self.zoom_manager.set_zoom(100))
        self.addAction(zoom_100_action)

        # Ctrl+2 for 150% zoom
        zoom_150_shortcut = QKeySequence("Ctrl+2")
        zoom_150_action = QAction("Zoom 150%", self)
        zoom_150_action.setShortcut(zoom_150_shortcut)
        zoom_150_action.triggered.connect(lambda: self.zoom_manager.set_zoom(150))
        self.addAction(zoom_150_action)

        # Ctrl+3 for 200% zoom
        zoom_200_shortcut = QKeySequence("Ctrl+3")
        zoom_200_action = QAction("Zoom 200%", self)
        zoom_200_action.setShortcut(zoom_200_shortcut)
        zoom_200_action.triggered.connect(lambda: self.zoom_manager.set_zoom(200))
        self.addAction(zoom_200_action)

        # Ctrl+4 for 75% zoom
        zoom_75_shortcut = QKeySequence("Ctrl+4")
        zoom_75_action = QAction("Zoom 75%", self)
        zoom_75_action.setShortcut(zoom_75_shortcut)
        zoom_75_action.triggered.connect(lambda: self.zoom_manager.set_zoom(75))
        self.addAction(zoom_75_action)

        # Ctrl+5 for 50% zoom
        zoom_50_shortcut = QKeySequence("Ctrl+5")
        zoom_50_action = QAction("Zoom 50%", self)
        zoom_50_action.setShortcut(zoom_50_shortcut)
        zoom_50_action.triggered.connect(lambda: self.zoom_manager.set_zoom(50))
        self.addAction(zoom_50_action)

    def setup_document_change_tracking(self):
        """Set up tracking for document changes for undo/redo functionality.

        This method is intentionally empty because we handle document changes
        through our own mechanisms rather than connecting directly to the
        QTextDocument's signals, which can be too granular.

        Returns:
            None
        """
        # We handle document changes in text_edit.textChanged
        # and specific operations (format, alignment, etc.)
        pass

    def _update_undo_action(self, available):
        """Update the undo action enabled state.

        Args:
            available (bool): Whether undo is available

        Returns:
            None
        """
        if hasattr(self, "undo_action"):
            self.undo_action.setEnabled(available)

    def _update_redo_action(self, available):
        """Update the redo action enabled state.

        Args:
            available (bool): Whether redo is available

        Returns:
            None
        """
        if hasattr(self, "redo_action"):
            self.redo_action.setEnabled(available)

    def undo(self):
        """Undo the last operation.

        Returns:
            bool: True if successful, False otherwise
        """
        if self.command_history.undo():
            # Update document modification state
            self.document_manager.set_modified(True)
            # Update the status bar
            self.update_status_bar()
            return True
        return False

    def redo(self):
        """Redo the last undone operation.

        Returns:
            bool: True if successful, False otherwise
        """
        if self.command_history.redo():
            # Update document modification state
            self.document_manager.set_modified(True)
            # Update the status bar
            self.update_status_bar()
            return True
        return False

    def apply_format(self, format):
        """Apply the format to the current selection or cursor position.

        Applies character formatting to the current selection or cursor position
        with error handling to prevent crashes.

        Args:
            format (QTextCharFormat): The format to apply

        Returns:
            None
        """
        try:
            # Check if text_edit is valid
            if not self.text_edit or not self.text_edit.isVisible():
                return

            # Create and execute a FormatCommand
            command = FormatCommand(self.text_edit, format)
            self.command_history.push(command)

        except Exception as e:
            from loguru import logger

            logger.error(f"Error applying format: {e}", exc_info=True)

    def set_alignment(self, alignment):
        """Set the alignment of the current paragraph.

        Sets the alignment of the current paragraph with error handling
        to prevent crashes.

        Args:
            alignment (Qt.AlignmentFlag): The alignment to apply

        Returns:
            None
        """
        try:
            # Check if text_edit is valid
            if not self.text_edit or not self.text_edit.isVisible():
                return

            # Create and execute an AlignmentCommand
            command = AlignmentCommand(self.text_edit, alignment)
            self.command_history.push(command)

        except Exception as e:
            from loguru import logger

            logger.error(f"Error setting alignment: {e}", exc_info=True)

    def on_text_changed(self):
        """Handle text changes in the editor."""
        # Note: We don't create a command here because text editing operations
        # like typing, cutting, pasting, etc. should be handled by tracking
        # document changes through the QTextDocument signals. The Command pattern
        # should not interfere with the normal undo/redo mechanism for text edits.

        # Mark the document as modified
        self.document_manager.set_modified(True)
        self.update_status_bar()

        # Reconnect format toolbar if needed
        self.reconnect_format_toolbar()

    def reconnect_format_toolbar(self):
        """Reconnect the format toolbar to the text editor.

        This method ensures that the format toolbar is properly connected
        to the text editor signals. It's called after text changes to
        maintain the connection.

        Returns:
            None
        """
        try:
            if hasattr(self, "format_toolbar") and hasattr(
                self.format_toolbar, "connect_to_editor_signals"
            ):
                self.format_toolbar.connect_to_editor_signals()
        except Exception as e:
            from loguru import logger

            logger.error(f"Error reconnecting format toolbar: {e}", exc_info=True)

    def update_status_bar_without_toolbar(self):
        """Update the status bar with document statistics without updating the toolbar."""
        try:
            text = self.text_edit.toPlainText()
            cursor = self.text_edit.textCursor()

            # Calculate statistics
            char_count = len(text)
            word_count = len(text.split())
            line_count = text.count("\n") + 1
            col = cursor.columnNumber() + 1
            line = cursor.blockNumber() + 1

            # Update status bar
            self.status_bar.showMessage(
                f"Line: {line}, Col: {col} | "
                f"Characters: {char_count} | "
                f"Words: {word_count} | "
                f"Lines: {line_count}"
            )

        except Exception as e:
            from loguru import logger

            logger.error(f"Error updating status bar: {e}", exc_info=True)

    def update_status_bar(self):
        """Update the status bar with document statistics."""
        try:
            # Just call the version without toolbar updates to avoid segfaults
            self.update_status_bar_without_toolbar()

            # Disabled to prevent segfaults
            # Update format toolbar state
            # self._safe_update_format_toolbar()

        except Exception as e:
            from loguru import logger

            logger.error(f"Error updating status bar: {e}", exc_info=True)

    def update_format_toolbar(self):
        """Update the format toolbar state to reflect current formatting.

        This method safely updates the format toolbar state to reflect
        the formatting at the current cursor position.

        Returns:
            None
        """
        try:
            if hasattr(self, "format_toolbar") and hasattr(
                self.format_toolbar, "update_toolbar_state"
            ):
                self.format_toolbar.update_toolbar_state()
        except Exception as e:
            from loguru import logger

            logger.error(f"Error updating format toolbar: {e}", exc_info=True)

    def _safe_update_format_toolbar(self):
        """Safely update the format toolbar with additional error handling.

        This is a wrapper around update_format_toolbar that adds an extra
        layer of error handling to prevent any exceptions from propagating.

        Note: This method is currently disabled to prevent segfaults.

        Returns:
            None
        """
        # Completely disabled to prevent segfaults
        return

        # Original implementation (disabled)
        # try:
        #     self.update_format_toolbar()
        # except Exception as e:
        #     from loguru import logger
        #     logger.error(f"Error in _safe_update_format_toolbar: {e}", exc_info=True)

    def on_cursor_position_changed(self):
        """Handle cursor position changes in the editor.

        Updates the status bar when the cursor position changes.
        Format toolbar updates are disabled to prevent segfaults.

        Returns:
            None
        """
        try:
            # Update the status bar only
            self.update_status_bar_without_toolbar()

            # Format toolbar updates are disabled to prevent segfaults
            # from PyQt6.QtCore import QTimer
            # QTimer.singleShot(50, self._safe_update_format_toolbar)

        except Exception as e:
            from loguru import logger

            logger.error(f"Error handling cursor position change: {e}", exc_info=True)

    def on_selection_changed(self):
        """Handle selection changes in the editor.

        Format toolbar updates are disabled to prevent segfaults.

        Returns:
            None
        """
        # Completely disabled to prevent segfaults
        return

        # Original implementation (disabled)
        # try:
        #     # Update the format toolbar with a slight delay to ensure stability
        #     from PyQt6.QtCore import QTimer
        #     QTimer.singleShot(50, self._safe_update_format_toolbar)
        #
        # except Exception as e:
        #     from loguru import logger
        #     logger.error(f"Error handling selection change: {e}", exc_info=True)

    def set_document_title(self):
        """Set the title of the current document.

        Opens a dialog to allow the user to set or change the document title.
        This is particularly useful for notes.

        Returns:
            None
        """
        try:
            # Get current title from window title
            current_title = self.windowTitle()
            # Remove the "- RTF Editor" suffix and any modification indicator
            if " - RTF Editor" in current_title:
                current_title = current_title.split(" - RTF Editor")[0]
            if current_title.endswith(" *"):
                current_title = current_title[:-2]

            # Show input dialog
            new_title, ok = QInputDialog.getText(
                self,
                "Set Document Title",
                "Enter document title:",
                text=current_title
            )

            if ok and new_title:
                # Update window title
                modified_indicator = " *" if self.document_manager.is_modified else ""
                self.setWindowTitle(f"{new_title} - RTF Editor{modified_indicator}")

                # Store the title in document manager
                if hasattr(self.document_manager, "document_name"):
                    self.document_manager.document_name = new_title

                # Show confirmation in status bar
                self.status_bar.showMessage(f"Title set to: {new_title}", 3000)

        except Exception as e:
            from loguru import logger
            logger.error(f"Error setting document title: {e}", exc_info=True)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.document_manager.check_unsaved_changes():
            # Clean up auto-save manager before closing
            if hasattr(self.document_manager, 'auto_save_manager') and self.document_manager.auto_save_manager:
                try:
                    self.document_manager.auto_save_manager.cleanup()
                except Exception as e:
                    from loguru import logger
                    logger.error(f"Error cleaning up auto-save manager: {e}", exc_info=True)

            event.accept()
        else:
            event.ignore()

    def eventFilter(self, source, event):
        """Filter events for the text editor viewport to handle context menu."""
        if (
            source is self.text_edit.viewport()
            and event.type() == QEvent.Type.ContextMenu
        ):
            cursor = self.text_edit.cursorForPosition(event.pos())
            char_format = cursor.charFormat()  # Get format at cursor

            # --- Check for Image ---
            if char_format.isImageFormat():
                image_format = char_format.toImageFormat()
                if image_format.isValid():
                    # Debug print
                    path = image_format.name()
                    if path and path.startswith("data:"):
                        print("Found image with data URI")
                    else:
                        print(f"Found image with path: {path}")

                    self.show_image_context_menu(
                        event.globalPos(), image_format, cursor.position()
                    )
                    return True  # Event handled

            # --- Check for Table ---
            table = cursor.currentTable()
            if table:
                # If inside a table, show the table-specific context menu
                table_menu = self.table_manager.get_table_menu()
                table_menu.exec(event.globalPos())
                return True  # Indicate that the event has been handled

            # --- Standard Text Menu ---
            # Let default or standard menu show if not image or table
            pass  # Fall through to default handling

        # Pass on other events
        return super().eventFilter(source, event)

    def show_image_context_menu(self, global_pos, image_format, cursor_pos):
        """Creates and shows the context menu for a selected image."""
        menu = QMenu(self)

        # --- Add Actions ---
        edit_action = menu.addAction("Edit Image...")
        edit_action.triggered.connect(
            lambda: self.open_image_editor_dialog(image_format, cursor_pos)
        )

        props_action = menu.addAction("Image Properties...")
        props_action.triggered.connect(
            lambda: self.open_image_properties_dialog(image_format, cursor_pos)
        )

        menu.addSeparator()

        # Example: Add a resize action directly (can be moved to dialog later)
        resize_action = menu.addAction("Resize Image...")
        resize_action.triggered.connect(
            lambda: self.resize_selected_image(image_format, cursor_pos)
        )

        # --- Show Menu ---
        menu.exec(global_pos)

    def open_image_editor_dialog(self, image_format, cursor_pos):
        """Open the advanced image editor dialog for the selected image."""
        print(f"Opening image editor dialog for image at cursor position: {cursor_pos}")

        # Log original image format details
        orig_path = image_format.name()
        orig_width = image_format.width()
        orig_height = image_format.height()
        print(
            f"Original image format - Path: {orig_path[:30]}..., Size: {orig_width}x{orig_height}"
        )

        dialog = ImageEditorDialog(image_format, self)
        if dialog.exec():
            # Get the result path and dimensions
            result_path = dialog.get_result_path()
            new_width, new_height = dialog.get_new_dimensions()

            print(
                f"Dialog accepted. New path: {result_path[:30]}..., dimensions: {new_width}x{new_height}"
            )

            # Log document state before update
            doc_html_before = self.text_edit.document().toHtml()
            image_count_before = doc_html_before.count("<img ")
            print(
                f"Document before update - HTML length: {len(doc_html_before)}, Image count: {image_count_before}"
            )

            # Update the image format with the new path and dimensions
            self.apply_image_update(
                image_format, cursor_pos, result_path, new_width, new_height
            )

            # Log document state after update
            doc_html_after = self.text_edit.document().toHtml()
            image_count_after = doc_html_after.count("<img ")
            print(
                f"Document after update - HTML length: {len(doc_html_after)}, Image count: {image_count_after}"
            )
            print(f"Image count change: {image_count_after - image_count_before}")
        else:
            print("Image editor dialog cancelled")

    def open_image_properties_dialog(self, image_format, cursor_pos):
        """Open the properties dialog for the selected image."""
        dialog = ImagePropertiesDialog(image_format, self)
        if dialog.exec():
            new_width, new_height = dialog.get_new_dimensions()
            # Get current dimensions from format, default to 0 if not set
            current_width = (
                int(image_format.width())
                if image_format.hasProperty(QTextFormat.Property.ImageWidth)
                else 0
            )
            current_height = (
                int(image_format.height())
                if image_format.hasProperty(QTextFormat.Property.ImageHeight)
                else 0
            )

            # Only apply changes if dimensions actually changed
            # Or if current dimensions were unset (<=0)
            if (new_width != current_width or new_height != current_height) or (
                current_width <= 0 or current_height <= 0
            ):
                self.apply_image_resize(image_format, cursor_pos, new_width, new_height)

    def resize_selected_image(self, image_format, cursor_pos):
        """Prompt user and resize the selected image."""
        # Get original dimensions (consider reusing logic from ImagePropertiesDialog)
        original_width = int(image_format.width())
        original_height = int(image_format.height())

        # Try to load original from path if current format dimensions are invalid
        if original_width <= 0 or original_height <= 0:
            path = image_format.name()
            if path and Path(path).exists():
                try:
                    path_obj = Path(path)
                    with Image.open(path_obj) as img:
                        original_width, original_height = img.size
                except Exception as e:
                    print(
                        f"Could not load original image {path_obj} for dimensions: {e}"
                    )
                    original_width, original_height = 100, 100  # Safe default
            else:
                original_width, original_height = 100, 100  # Safe default if no path

        # Use QInputDialog to get new width
        new_width, ok = QInputDialog.getInt(
            self,
            "Resize Image",
            f"Enter new width (current: {original_width}px):",
            original_width,
            10,
            8000,
            10,
        )

        if ok and new_width != original_width:
            # Calculate new height maintaining aspect ratio
            aspect_ratio = original_height / original_width if original_width > 0 else 1
            new_height = int(new_width * aspect_ratio)
            self.apply_image_resize(image_format, cursor_pos, new_width, new_height)

    def apply_image_resize(self, image_format, cursor_pos, new_width, new_height):
        """Applies resizing by modifying the image format at the given cursor position."""
        image_path = image_format.name()  # Original path stored in the format

        # Use the more reliable complete replacement approach for resizing
        self.apply_image_update_alternative(
            cursor_pos, image_path, new_width, new_height
        )

    def apply_image_update(
        self, image_format, cursor_pos, new_path, new_width, new_height
    ):
        """Applies changes to an image, including path and dimensions."""
        try:
            print(
                f"Applying image update: path={new_path[:50]}..., width={new_width}, height={new_height}"
            )
            print(f"Cursor position when applying update: {cursor_pos}")

            # Check if new_path is a data URI or file path
            is_data_uri = new_path.startswith("data:")
            if not is_data_uri and not Path(new_path).exists():
                print(f"Warning: Image file not found at {new_path}")
                return

            # Convert regular file path to data URI for embedding
            if not is_data_uri:
                try:
                    import base64
                    import mimetypes

                    # Determine MIME type
                    mime_type, _ = mimetypes.guess_type(new_path)
                    if not mime_type:
                        if new_path.lower().endswith(
                            ".jpg"
                        ) or new_path.lower().endswith(".jpeg"):
                            mime_type = "image/jpeg"
                        elif new_path.lower().endswith(".png"):
                            mime_type = "image/png"
                        elif new_path.lower().endswith(".gif"):
                            mime_type = "image/gif"
                        else:
                            mime_type = "image/png"  # Default

                    # Read image file and convert to base64
                    with open(new_path, "rb") as img_file:
                        img_data = img_file.read()

                    img_base64 = base64.b64encode(img_data).decode("utf-8")
                    data_uri = f"data:{mime_type};base64,{img_base64}"

                    # Use data URI instead of file path
                    new_path = data_uri
                    print("Converted file path to data URI")
                except Exception as e:
                    print(f"Error converting to data URI: {e}")
                    # If conversion fails, we'll continue with file path but it may not work well

            print("Calling alternative method for image update")
            # Use the alternative method that replaces the image entirely rather than modifying in place
            self.apply_image_update_alternative(
                cursor_pos, new_path, new_width, new_height
            )

        except Exception as e:
            print(f"Error applying image update: {e}")
            QMessageBox.critical(
                self, "Error", f"Could not apply image update: {str(e)}"
            )

    def apply_image_update_alternative(
        self, cursor_pos, new_path, new_width, new_height
    ):
        """Alternative method to update an image by replacing it completely."""
        try:
            print("Using alternative approach to update image...")
            print(f"Starting cursor position: {cursor_pos}")

            # Convert to data URI if it's a file path
            if not new_path.startswith("data:"):
                try:
                    import base64
                    import mimetypes

                    # Determine MIME type
                    mime_type, _ = mimetypes.guess_type(new_path)
                    if not mime_type:
                        if new_path.lower().endswith(
                            ".jpg"
                        ) or new_path.lower().endswith(".jpeg"):
                            mime_type = "image/jpeg"
                        elif new_path.lower().endswith(".png"):
                            mime_type = "image/png"
                        elif new_path.lower().endswith(".gif"):
                            mime_type = "image/gif"
                        else:
                            mime_type = "image/png"  # Default

                    # Read image file and convert to base64
                    with open(new_path, "rb") as img_file:
                        img_data = img_file.read()

                    img_base64 = base64.b64encode(img_data).decode("utf-8")
                    new_path = f"data:{mime_type};base64,{img_base64}"
                    print("Converted file path to data URI in alternative method")
                except Exception as e:
                    print(f"Error converting to data URI in alternative method: {e}")
                    # Continue with file path if conversion fails

            # Get the document content before we make changes (for debugging)
            before_doc_html = self.text_edit.document().toHtml()
            print(f"Document before change - HTML length: {len(before_doc_html)}")
            before_img_count = before_doc_html.count("<img ")
            print(f"Image count before change: {before_img_count}")

            # Try a different approach to locate and remove the image
            image_found = False

            # Create a cursor at the position
            cursor = QTextCursor(self.text_edit.document())
            cursor.setPosition(cursor_pos)

            # Check if we're already at an image position
            cursor_format = cursor.charFormat()
            if cursor_format.isImageFormat():
                # We're already at an image position
                print("Direct hit: Cursor is already at the image position")

                # Create a selection of just this character
                selection_cursor = QTextCursor(cursor)
                selection_cursor.movePosition(
                    QTextCursor.MoveOperation.NextCharacter,
                    QTextCursor.MoveMode.KeepAnchor,
                )

                # Get the old image info for logging
                old_format = selection_cursor.charFormat().toImageFormat()
                old_path = old_format.name()
                old_width = old_format.width()
                old_height = old_format.height()

                # Delete the selected character (which is the image)
                print(f"Deleting image character at position {cursor_pos}")
                selection_cursor.deleteChar()
                image_found = True

            else:
                # Search around the cursor for the image
                # First try the next character
                next_char_cursor = QTextCursor(cursor)
                next_char_cursor.movePosition(
                    QTextCursor.MoveOperation.NextCharacter,
                    QTextCursor.MoveMode.KeepAnchor,
                )

                if next_char_cursor.charFormat().isImageFormat():
                    # Get the old image info for logging
                    old_format = next_char_cursor.charFormat().toImageFormat()
                    old_path = old_format.name()
                    old_width = old_format.width()
                    old_height = old_format.height()

                    print("Found image in next character position")
                    # Delete the image character
                    next_char_cursor.deleteChar()
                    image_found = True
                    # Reposition cursor back to the starting point
                    cursor.setPosition(cursor_pos)

                else:
                    # Try the previous character
                    prev_char_cursor = QTextCursor(cursor)
                    prev_char_cursor.movePosition(
                        QTextCursor.MoveOperation.PreviousCharacter,
                        QTextCursor.MoveMode.KeepAnchor,
                    )

                    if prev_char_cursor.charFormat().isImageFormat():
                        # Get the old image info for logging
                        old_format = prev_char_cursor.charFormat().toImageFormat()
                        old_path = old_format.name()
                        old_width = old_format.width()
                        old_height = old_format.height()

                        print("Found image in previous character position")
                        # Delete the image character
                        prev_char_cursor.deleteChar()
                        image_found = True
                        # Use the previous position for insertion
                        cursor.setPosition(cursor_pos - 1)

                    else:
                        # Try expanding the search range
                        for offset in range(1, 4):
                            # Check ahead
                            ahead_cursor = QTextCursor(self.text_edit.document())
                            ahead_cursor.setPosition(cursor_pos + offset)
                            ahead_cursor.movePosition(
                                QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor,
                            )

                            if ahead_cursor.charFormat().isImageFormat():
                                # Get the old image info for logging
                                old_format = ahead_cursor.charFormat().toImageFormat()
                                old_path = old_format.name()
                                old_width = old_format.width()
                                old_height = old_format.height()

                                print(f"Found image at position {cursor_pos + offset}")
                                ahead_cursor.deleteChar()
                                image_found = True
                                cursor.setPosition(cursor_pos + offset)
                                break

                            # Check behind
                            behind_cursor = QTextCursor(self.text_edit.document())
                            behind_cursor.setPosition(cursor_pos - offset)
                            behind_cursor.movePosition(
                                QTextCursor.MoveOperation.PreviousCharacter,
                                QTextCursor.MoveMode.KeepAnchor,
                            )

                            if behind_cursor.charFormat().isImageFormat():
                                # Get the old image info for logging
                                old_format = behind_cursor.charFormat().toImageFormat()
                                old_path = old_format.name()
                                old_width = old_format.width()
                                old_height = old_format.height()

                                print(f"Found image at position {cursor_pos - offset}")
                                behind_cursor.deleteChar()
                                image_found = True
                                cursor.setPosition(cursor_pos - offset)
                                break

            if not image_found:
                print("Error: Could not locate the image to replace")
                return

            # Check document after removal
            after_remove_html = self.text_edit.document().toHtml()
            after_img_count = after_remove_html.count("<img ")
            print(f"Document after removal - HTML length: {len(after_remove_html)}")
            print(f"Image count after removal: {after_img_count}")
            print(
                f"Removal changed HTML by: {len(before_doc_html) - len(after_remove_html)} characters"
            )
            print(f"Image count change: {after_img_count - before_img_count}")

            # Get the current cursor position after all our operations
            insert_position = cursor.position()
            print(f"Final insertion position: {insert_position}")

            # Create a fresh image format with no additional properties
            new_format = QTextImageFormat()
            new_format.setName(new_path)
            new_format.setWidth(new_width)
            new_format.setHeight(new_height)
            print(
                f"New image format created: {new_path[:30]}..., size: {new_width}x{new_height}"
            )

            # Insert the new image
            print("Inserting new image")
            cursor.insertImage(new_format)

            # Check document after insertion
            after_insert_html = self.text_edit.document().toHtml()
            after_insert_img_count = after_insert_html.count("<img ")
            print(f"Document after insertion - HTML length: {len(after_insert_html)}")
            print(f"Image count after insertion: {after_insert_img_count}")
            print(
                f"Insertion added HTML by: {len(after_insert_html) - len(after_remove_html)} characters"
            )

            # Compare with original to verify we didn't add duplicates
            size_diff = len(after_insert_html) - len(before_doc_html)
            img_count_diff = after_insert_img_count - before_img_count
            print(f"Total HTML size change: {size_diff} characters")
            print(f"Total image count change: {img_count_diff}")

            print("Alternative image update applied successfully")
            self.on_text_changed()  # Mark modified

        except Exception as e:
            print(f"Error in alternative image update: {e}")
            QMessageBox.critical(self, "Error", f"Could not update image: {str(e)}")

    def wheelEvent(self, event):
        """Handle wheel events for zooming with Ctrl+Wheel."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Forward the event to the zoom manager
            self.zoom_manager.wheelEvent(event)
        else:
            # Pass to default handler
            super().wheelEvent(event)

    def _get_mime_type_from_path(self, file_path):
        """Get MIME type from file path using pathlib.

        Args:
            file_path (str): Path to the file

        Returns:
            str: MIME type for the file
        """
        import mimetypes

        # Try using mimetypes first
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type:
            # Fallback to extension-based detection
            path_obj = Path(file_path)
            suffix = path_obj.suffix.lower()

            if suffix in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif suffix == ".png":
                mime_type = "image/png"
            elif suffix == ".gif":
                mime_type = "image/gif"
            else:
                mime_type = "image/png"  # Default

        return mime_type

    def on_auto_save_completed(self):
        """Handle completion of auto-save operation."""
        self.show_status_message("Auto-saved")

    def show_status_message(self, message):
        """Show a message on the status bar."""
        self.status_bar.showMessage(message, 3000)  # Show for 3 seconds

    def show_recovery_dialog(self):
        """Show the recovery dialog.

        Checks for available recovery files and shows a dialog allowing
        the user to select and recover from them.

        Returns:
            None
        """
        # Check for recovery files
        recovery_files = (
            self.document_manager.auto_save_manager.check_for_recovery_files()
        )

        if not recovery_files:
            QMessageBox.information(
                self, "No Recovery Files", "No recovery files were found."
            )
            return

        # Ask if the user wants to see recovery files
        response = QMessageBox.question(
            self,
            "Recovery Files Found",
            f"Found {len(recovery_files)} recovery files. Would you like to recover a document?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if response == QMessageBox.StandardButton.No:
            return

        # If there are recovery files, show a dialog to select one
        file_items = []
        filtered_recovery_files = []

        for file in recovery_files:
            # Get file info
            timestamp = file.stem.split("_")[-1]
            doc_id = "_".join(file.stem.split("_")[:-1])

            # Skip recovery files for notes if this is not the notes editor
            if "note" in doc_id.lower() and not getattr(self, "is_notes_editor", False):
                continue

            filtered_recovery_files.append(file)

            # Format timestamp for display
            try:
                # Convert YYYYMMDD_HHMMSS to a more readable format
                dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = timestamp

            # Add to list
            file_items.append(f"{doc_id} ({formatted_time})")

        if not file_items:
            QMessageBox.information(
                self, "No Relevant Recovery Files", "No relevant recovery files were found for this editor."
            )
            return

        # Show selection dialog
        selected_item, ok = QInputDialog.getItem(
            self,
            "Select Recovery File",
            "Select a recovery file to restore:",
            file_items,
            0,  # Default to first item
            False,  # Not editable
        )

        if ok and selected_item:
            # Find the corresponding file
            index = file_items.index(selected_item)
            recovery_file = filtered_recovery_files[index]

            # Recover the document
            self.document_manager.recover_document(recovery_file)

    def setup_exception_handling(self):
        """Set up custom exception handling for the application."""
        import sys

        from shared.ui.widgets.rtf_editor.utils.recovery_utils import (
            create_error_report,
        )

        # Store the original excepthook
        original_excepthook = sys.excepthook

        def custom_excepthook(exc_type, exc_value, exc_traceback):
            """Custom exception hook to handle unhandled exceptions.

            Args:
                exc_type: Exception type
                exc_value: Exception value
                exc_traceback: Exception traceback

            Returns:
                None
            """
            try:
                # Create an error report
                error_report = create_error_report(exc_value, "unhandled exception")

                # Log the exception
                logger.critical(
                    f"Unhandled exception: {exc_type.__name__}: {exc_value}",
                    exc_info=(exc_type, exc_value, exc_traceback),
                )

                # Attempt recovery
                if hasattr(self, "document_manager") and hasattr(
                    self.document_manager, "auto_save_manager"
                ):
                    # Force an auto-save
                    try:
                        self.document_manager.auto_save_manager.auto_save()
                        logger.info("Emergency auto-save completed")
                    except Exception as e:
                        logger.error(f"Emergency auto-save failed: {str(e)}")

                # Show error dialog
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.critical(
                    None,
                    "Application Error",
                    f"An unhandled error occurred: {exc_value}\n\n"
                    f"An error report has been created at: {error_report}\n\n"
                    "The application will now attempt to recover.",
                )

                # Call the original exception hook
                original_excepthook(exc_type, exc_value, exc_traceback)

            except Exception as e:
                # If our error handling fails, fall back to the original exception hook
                logger.critical(f"Error in custom exception hook: {str(e)}")
                original_excepthook(exc_type, exc_value, exc_traceback)

        # Install the custom exception hook
        sys.excepthook = custom_excepthook

    def document_loaded(self, content):
        """Handle document loading completion.

        This method is called when a document is loaded, either from a file
        or from the database. It sets the text editor content and clears
        the command history.

        Args:
            content (str): The document content (HTML)

        Returns:
            None
        """
        # Set the document content
        self.text_edit.setHtml(content)

        # Clear the command history
        self.command_history.clear()

        # Reset document modified state
        self.document_manager.set_modified(False)

        # Update UI
        self.update_status_bar()

        logger.debug("Document loaded and command history cleared")

    def image_manager_insert_image(self, image_format, position=None):
        """Insert an image using the command pattern.

        This method is called by the image manager to insert an image.
        It creates and executes an InsertImageCommand.

        Args:
            image_format (QTextImageFormat): The image format to insert
            position (int, optional): Position to insert the image at.
                If None, the current cursor position is used.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create and execute the command
            command = InsertImageCommand(self.text_edit, image_format, position)
            return self.command_history.push(command)
        except Exception as e:
            logger.error(f"Error inserting image with command: {e}")
            return False
