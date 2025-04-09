import os  # Import os module

from PyQt6.QtCore import (
    QByteArray,
    QFile,
    QFileInfo,
    QIODevice,
    QObject,
    QTextStream,
    pyqtSignal,
)
from PyQt6.QtGui import QTextDocumentWriter
from PyQt6.QtWidgets import QFileDialog, QMessageBox

# Define the default directory relative to the current working directory
DEFAULT_DIR = os.path.join(os.getcwd(), "document_folder")
# Define a custom extension for Qt's native format
DEFAULT_EXTENSION = ".qdoc"
FILE_FILTER = f"IsopGem Documents (*{DEFAULT_EXTENSION});;All Files (*)"


class DocumentManager(QObject):
    """Manages document loading, saving, and state using Qt's native format."""

    document_loaded = pyqtSignal(str)  # Emits RTF content when loaded
    error_occurred = pyqtSignal(str)  # Emits error messages
    status_updated = pyqtSignal(str)  # Emits status messages
    modification_changed = pyqtSignal(bool)  # Emits modification status

    def __init__(self, editor_window):
        super().__init__()
        self.editor_window = editor_window
        self.current_path = None
        self.is_modified = False

        # Ensure the default directory exists
        os.makedirs(DEFAULT_DIR, exist_ok=True)

    def set_modified(self, modified=True):
        """Set the modification status of the document."""
        if self.is_modified != modified:
            self.is_modified = modified
            self.modification_changed.emit(modified)
            self.update_window_title()

    def update_window_title(self):
        """Update the editor window title based on file path and modification."""
        title = "RTF Editor"

        # For file-based documents, use the filename
        if self.current_path:
            file_name = QFileInfo(self.current_path).fileName()
            title = f"{file_name} - {title}"
        # For database documents, use the document_name if available
        elif hasattr(self, "document_id") and hasattr(self, "document_name"):
            title = f"{self.document_name} - {title}"

        if self.is_modified:
            title += " *"
        self.editor_window.setWindowTitle(title)

    def new_document(self):
        """Handle creation of a new document."""
        if not self.check_unsaved_changes():
            return

        self.current_path = None
        self.editor_window.text_edit.clear()
        self.set_modified(False)
        self.status_updated.emit("New document created.")

    def open_document(self, bypass_dialog=False):
        """Open an existing document using native format."""
        if not self.check_unsaved_changes():
            return False

        # If we already have a path and bypass_dialog is True, just open that file
        if bypass_dialog and self.current_path:
            file_path = self.current_path
        else:
            # Show file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self.editor_window, "Open Document", DEFAULT_DIR, FILE_FILTER
            )

        if file_path:
            try:
                # Open the file
                file = QFile(file_path)
                if not file.open(
                    QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
                ):
                    raise Exception(f"Cannot open file: {file.errorString()}")

                # Clear the editor first
                self.editor_window.text_edit.clear()

                print(f"Loading document from: {file_path}")

                # Check if it's our Qt native format
                if file_path.lower().endswith(DEFAULT_EXTENSION.lower()):
                    # Qt native format - load directly as HTML content
                    stream = QTextStream(file)
                    # In PyQt6, the setEncoding method may not be available or has changed
                    # Just read the content directly
                    html_content = stream.readAll()
                    self.editor_window.text_edit.setHtml(html_content)
                else:
                    # Fall back to plain text for other formats
                    plain_text = QTextStream(file).readAll()
                    self.editor_window.text_edit.setPlainText(plain_text)

                file.close()
                self.current_path = file_path
                self.set_modified(False)
                self.status_updated.emit(f"Opened: {file_path}")
                print(f"DEBUG: Finished loading document from {file_path}")
                return True

            except Exception as e:
                print(f"Error opening document: {e}")
                QMessageBox.critical(
                    self.editor_window,
                    "Error",
                    f"Could not open the document: {str(e)}",
                )
                return False
        return False

    def save_document(self):
        """Save the current document using native format."""
        if self.current_path:
            return self._save_to_path(self.current_path)
        else:
            return self.save_document_as()

    def save_document_as(self):
        """Save the current document to a new file path using native format."""
        suggested_path = os.path.join(DEFAULT_DIR, self.get_default_filename())
        file_path, _ = QFileDialog.getSaveFileName(
            self.editor_window, "Save Document As", suggested_path, FILE_FILTER
        )

        if file_path:
            # Ensure the chosen path has our default extension
            if not file_path.lower().endswith(DEFAULT_EXTENSION.lower()):
                file_path += DEFAULT_EXTENSION
            return self._save_to_path(file_path)
        return False

    def _save_to_path(self, file_path):
        """Helper function to save content using QTextDocumentWriter."""
        try:
            # Get the QTextDocument from the editor
            document = self.editor_window.text_edit.document()

            # Use QTextDocumentWriter for native Qt format
            writer = QTextDocumentWriter(file_path)
            if file_path.lower().endswith(".html"):
                # QByteArray constructor takes (size, byte_value) for a byte sequence
                # For a string, pass 0 as size and the bytes as the second argument
                writer.setFormat(QByteArray(0, b"html"))
            else:
                # Default to HTML format stored in our custom extension
                writer.setFormat(QByteArray(0, b"html"))

            success = writer.write(document)

            if not success:
                raise Exception("QTextDocumentWriter could not write the document")

            self.current_path = file_path
            self.set_modified(False)
            self.status_updated.emit(f"Saved: {file_path}")
            return True

        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            print(f"ERROR: Caught in save block: {error_msg}", flush=True)
            self.error_occurred.emit(error_msg)
            QMessageBox.critical(self.editor_window, "Error", error_msg)
            return False

    def get_default_filename(self):
        """Suggest a default filename with the custom extension."""
        if self.current_path:
            # Keep existing name but ensure correct extension
            base = QFileInfo(self.current_path).completeBaseName()
            return base + DEFAULT_EXTENSION
        return f"Untitled{DEFAULT_EXTENSION}"

    def check_unsaved_changes(self):
        """Check for unsaved changes and prompt user if necessary. Returns True if safe to proceed."""
        if not self.is_modified:
            return True

        reply = QMessageBox.warning(
            self.editor_window,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save before proceeding?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_document()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False  # Do not proceed

    def get_document_format(self):
        """Get the current document as a DocumentFormat object for database storage.

        Returns:
            DocumentFormat: The current document in DocumentFormat structure
        """
        import uuid
        from datetime import datetime

        from shared.ui.widgets.rtf_editor.models.document_format import DocumentFormat

        # Get the document from the editor
        document = self.editor_window.text_edit.document()

        # Extract HTML content
        html_content = document.toHtml()

        # Extract plain text
        plain_text = document.toPlainText()

        # Create a document ID if none exists
        doc_id = getattr(self, "document_id", None)
        if not doc_id:
            doc_id = str(uuid.uuid4())
            self.document_id = doc_id

        # Use stored document name if available
        doc_name = getattr(self, "document_name", None)

        # If no stored name, derive from file path or use default
        if not doc_name:
            if self.current_path:
                doc_name = QFileInfo(self.current_path).fileName()
                if doc_name.endswith(DEFAULT_EXTENSION):
                    doc_name = doc_name[: -len(DEFAULT_EXTENSION)]
            else:
                doc_name = "Untitled Document"
            # Store the name for future reference
            self.document_name = doc_name

        # Get word count
        word_count = len(plain_text.split()) if plain_text else 0

        # Create document format
        doc_format = DocumentFormat(
            id=doc_id,
            name=doc_name,
            html_content=html_content,
            plain_text=plain_text,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            metadata={
                "word_count": word_count,
                "character_count": len(plain_text) if plain_text else 0,
            },
        )

        return doc_format

    def load_document_format(self, doc_format):
        """Load a document from a DocumentFormat object.

        Args:
            doc_format: DocumentFormat object to load

        Returns:
            bool: True if successful, False otherwise
        """
        if not doc_format:
            self.error_occurred.emit("Invalid document format provided")
            return False

        try:
            # Store the document ID and name for future reference
            self.document_id = doc_format.id
            self.document_name = doc_format.name

            # Clear the current document
            self.editor_window.text_edit.clear()

            # Load HTML content if available
            if doc_format.html_content:
                self.editor_window.text_edit.setHtml(doc_format.html_content)
            # Fall back to plain text if no HTML
            elif doc_format.plain_text:
                self.editor_window.text_edit.setPlainText(doc_format.plain_text)

            # Set modification state to false since we just loaded
            self.set_modified(False)

            # Update UI with document name
            self.current_path = None  # It's a database document, not a file
            self.update_window_title()
            self.status_updated.emit(f"Loaded document: {doc_format.name}")

            return True
        except Exception as e:
            error_msg = f"Error loading document format: {str(e)}"
            self.error_occurred.emit(error_msg)
            QMessageBox.critical(self.editor_window, "Error", error_msg)
            return False
