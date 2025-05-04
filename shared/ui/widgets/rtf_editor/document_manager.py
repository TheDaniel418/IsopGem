import os
import uuid
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import (
    QByteArray,
    QFile,
    QFileInfo,
    QIODevice,
    QObject,
    QTextStream,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QTextDocumentWriter
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger
from shared.ui.widgets.rtf_editor.utils.recovery_utils import (
    AutoSaveManager,
    create_error_report,
    recover_from_error,
)

# Initialize logger
logger = get_logger(__name__)

# Define the default directory relative to the current working directory
DEFAULT_DIR = Path.cwd() / "document_folder"
# Define a custom extension for Qt's native format
DEFAULT_EXTENSION = ".qdoc"
FILE_FILTER = f"IsopGem Documents (*{DEFAULT_EXTENSION});;All Files (*)"


class DocumentManager(QObject):
    """Manages document loading, saving, and state using Qt's native format.

    This class handles all document operations for the RTF editor, including:
    - Creating new documents
    - Opening existing documents
    - Saving documents
    - Tracking modification state
    - Converting between file and database formats

    It uses Qt's native HTML format for document storage, with a custom extension.

    Attributes:
        document_loaded (pyqtSignal): Signal emitted when a document is loaded
        error_occurred (pyqtSignal): Signal emitted when an error occurs
        status_updated (pyqtSignal): Signal emitted to update status messages
        modification_changed (pyqtSignal): Signal emitted when document modification state changes

    Signals:
        document_loaded(str): Emitted with document content when loaded
        error_occurred(str): Emitted with error message when an error occurs
        status_updated(str): Emitted with status message
        modification_changed(bool): Emitted with new modification state
    """

    document_loaded = pyqtSignal(str)  # Emits RTF content when loaded
    error_occurred = pyqtSignal(str)  # Emits error messages
    status_updated = pyqtSignal(str)  # Emits status messages
    modification_changed = pyqtSignal(bool)  # Emits modification status
    recovery_available = pyqtSignal(list)  # Emits list of recovery files
    auto_save_completed = pyqtSignal()  # Emits when auto-save completes

    def __init__(self, editor_window):
        """Initialize the DocumentManager.

        Sets up the document manager with references to the editor window
        and initializes the document state. Also sets up auto-save and
        recovery mechanisms.

        Args:
            editor_window: The main editor window containing the QTextEdit

        Raises:
            OSError: If the default directory cannot be created
        """
        super().__init__()
        self.editor_window = editor_window
        self.current_path = None
        self.is_modified = False
        self.recovery_in_progress = False
        self.last_save_time = None
        self.last_error_time = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.error_cooldown = 60  # seconds

        # Generate a unique document ID
        self.document_id = f"doc_{uuid.uuid4().hex[:8]}"
        logger.debug(
            f"DocumentManager initialized with document_id: {self.document_id}"
        )

        # Ensure the default directory exists
        os.makedirs(DEFAULT_DIR, exist_ok=True)

        # Initialize auto-save manager
        self.auto_save_manager = AutoSaveManager(self.editor_window.text_edit)
        self.auto_save_manager.auto_save_triggered.connect(self._on_auto_save_triggered)

        # Set default auto-save interval (2 minutes)
        self.auto_save_manager.set_interval(120000)

        # Start auto-save
        self.auto_save_manager.start()

        # Check for recovery files on startup
        QTimer.singleShot(1000, self.check_for_recovery_files)

    def _on_auto_save_triggered(self):
        """Handle auto-save completion.

        Called when the auto-save manager completes an auto-save operation.
        Updates the status bar and emits the auto_save_completed signal.

        Returns:
            None
        """
        self.status_updated.emit("Document auto-saved")
        self.auto_save_completed.emit()
        logger.debug("Auto-save completed")

    def check_for_recovery_files(self):
        """Check for available recovery files.

        Looks for recovery files and emits the recovery_available signal
        if any are found.

        Returns:
            None
        """
        recovery_files = self.auto_save_manager.check_for_recovery_files()
        if recovery_files:
            self.recovery_available.emit(recovery_files)
            logger.info(f"Found {len(recovery_files)} recovery files")

    def recover_document(self, recovery_file):
        """Recover document from a recovery file.

        Args:
            recovery_file (Path): Path to the recovery file

        Returns:
            bool: True if recovery was successful, False otherwise
        """
        try:
            self.recovery_in_progress = True

            # Load content from recovery file
            content, original_path = self.auto_save_manager.load_recovery_file(
                recovery_file
            )

            if content:
                # Set the document content
                self.editor_window.text_edit.setHtml(content)

                # Set the current path if available
                if original_path:
                    self.current_path = original_path
                    self.auto_save_manager.set_document_path(original_path)

                # Update status
                self.status_updated.emit(
                    f"Document recovered from {recovery_file.name}"
                )
                logger.info(f"Successfully recovered document from {recovery_file}")

                # Ask if user wants to delete the recovery file
                response = QMessageBox.question(
                    self.editor_window,
                    "Delete Recovery File",
                    "Document recovered successfully. Delete the recovery file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if response == QMessageBox.StandardButton.Yes:
                    self.auto_save_manager.delete_recovery_file(recovery_file)

                self.recovery_in_progress = False
                return True
            else:
                self.status_updated.emit("Failed to recover document")
                logger.error(f"Failed to recover document from {recovery_file}")
                self.recovery_in_progress = False
                return False

        except Exception as e:
            self.status_updated.emit(f"Error during recovery: {str(e)}")
            logger.error(f"Error recovering document: {str(e)}", exc_info=True)
            self.recovery_in_progress = False
            return False

    def set_modified(self, modified=True):
        """Set the modification status of the document.

        Updates the internal modification state and emits the modification_changed signal
        if the state has changed. Also updates the window title to reflect the new state.

        Args:
            modified (bool): The new modification state, True if modified, False otherwise

        Returns:
            None
        """
        if self.is_modified != modified:
            self.is_modified = modified
            self.modification_changed.emit(modified)

            # Update window title to show modification status
            self.update_window_title()

            # Update auto-save manager with current document path
            if self.current_path:
                self.auto_save_manager.set_document_path(self.current_path)

    def update_window_title(self):
        """Update the editor window title based on file path and modification.

        Sets the window title to include:
        - The document name (from file path or database)
        - The application name
        - A modification indicator (*) if the document has unsaved changes

        The format is: "DocumentName - RTF Editor *" for modified documents

        Returns:
            None
        """
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
        """Handle creation of a new document.

        Creates a new, empty document after checking for unsaved changes in the current document.
        If there are unsaved changes, prompts the user to save them first.

        Returns:
            None
        """
        if not self.check_unsaved_changes():
            return

        self.current_path = None
        self.editor_window.text_edit.clear()

        # Call the document_loaded method with empty content
        if hasattr(self.editor_window, "document_loaded"):
            self.editor_window.document_loaded("")

        self.set_modified(False)
        self.status_updated.emit("New document created.")

    def open_document(self, bypass_dialog=False):
        """Open an existing document using native format.

        Opens a document from a file, either by showing a file dialog or by using
        the current path if bypass_dialog is True. Checks for unsaved changes before
        opening a new document.

        Args:
            bypass_dialog (bool): If True and current_path exists, opens that file
                                 without showing a file dialog

        Returns:
            bool: True if a document was successfully opened, False otherwise

        Raises:
            Exception: Handled internally for file opening errors
        """
        if not self.check_unsaved_changes():
            return False

        # If we already have a path and bypass_dialog is True, just open that file
        if bypass_dialog and self.current_path:
            file_path = self.current_path
        else:
            # Show file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self.editor_window, "Open Document", str(DEFAULT_DIR), FILE_FILTER
            )

        if file_path:
            try:
                # Input validation
                if not file_path or not isinstance(file_path, str):
                    raise ValueError("Invalid file path provided")

                # Convert to Path object for safer manipulation
                path_obj = Path(file_path)

                # Validate file exists and is readable
                if not path_obj.exists():
                    raise FileNotFoundError(f"File not found: {path_obj}")
                if not path_obj.is_file():
                    raise IsADirectoryError(f"Not a file: {path_obj}")
                if not os.access(str(path_obj), os.R_OK):
                    raise PermissionError(f"No read permission for file: {path_obj}")

                # Check file size to prevent loading extremely large files
                max_size_mb = 10  # Maximum file size in MB
                if path_obj.stat().st_size > max_size_mb * 1024 * 1024:
                    raise ValueError(f"File too large (> {max_size_mb}MB): {path_obj}")

                # Open the file
                file = QFile(str(path_obj))
                if not file.open(
                    QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
                ):
                    raise Exception(f"Cannot open file: {file.errorString()}")

                # Clear the editor first
                self.editor_window.text_edit.clear()

                logger.info(f"Loading document from: {path_obj}")

                # Check if it's our Qt native format
                if path_obj.suffix.lower() == DEFAULT_EXTENSION.lower():
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
                self.current_path = str(path_obj)
                self.set_modified(False)
                self.status_updated.emit(f"Opened: {path_obj}")
                logger.info(f"Finished loading document from {path_obj}")

                # Disabled to prevent segfaults
                # # Update format toolbar to reflect the loaded document's formatting
                # if hasattr(self.editor_window, "_safe_update_format_toolbar"):
                #     try:
                #         # Use a timer to ensure the document is fully loaded
                #         from PyQt6.QtCore import QTimer
                #         QTimer.singleShot(100, self.editor_window._safe_update_format_toolbar)
                #     except Exception as e:
                #         logger.error(f"Error updating format toolbar after load: {str(e)}")

                return True

            except FileNotFoundError as e:
                logger.error(f"File not found: {str(e)}", exc_info=True)

                # Create error report
                error_report = create_error_report(e, "file not found")

                # Attempt recovery
                if recover_from_error(self.editor_window, e, "document open operation"):
                    # Suggest opening a different file
                    QMessageBox.warning(
                        self.editor_window,
                        "File Not Found",
                        f"The file could not be found: {path_obj}\n\n"
                        "The file may have been moved, renamed, or deleted.",
                    )
                    # Try opening a different file
                    return self.open_document(bypass_dialog=False)
                return False

            except PermissionError as e:
                logger.error(f"Permission error opening file: {str(e)}", exc_info=True)

                # Create error report
                error_report = create_error_report(e, "file permission error")

                # Attempt recovery
                if recover_from_error(self.editor_window, e, "document open operation"):
                    QMessageBox.warning(
                        self.editor_window,
                        "Permission Error",
                        f"You don't have permission to open this file: {path_obj}\n\n"
                        "Please try opening a different file.",
                    )
                    return self.open_document(bypass_dialog=False)
                return False

            except UnicodeDecodeError as e:
                logger.error(f"Unicode decode error: {str(e)}", exc_info=True)

                # Create error report
                error_report = create_error_report(e, "file encoding error")

                # Attempt recovery by trying different encodings
                encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
                for encoding in encodings:
                    try:
                        with open(str(path_obj), "r", encoding=encoding) as f:
                            content = f.read()
                            self.editor_window.text_edit.setPlainText(content)
                            self.current_path = str(path_obj)
                            self.set_modified(False)
                            self.status_updated.emit(
                                f"Opened with {encoding} encoding: {path_obj}"
                            )
                            logger.info(f"Recovered document using {encoding} encoding")
                            return True
                    except Exception:
                        continue

                # If all encodings failed, show error
                QMessageBox.critical(
                    self.editor_window,
                    "Encoding Error",
                    f"Could not decode the file: {path_obj}\n\n"
                    "The file may be in an unsupported encoding or may not be a text file.",
                )
                return False

            except Exception as e:
                logger.error(f"Error opening document: {str(e)}", exc_info=True)

                # Create error report
                error_report = create_error_report(e, "document open operation")

                # Attempt recovery
                if recover_from_error(self.editor_window, e, "document open operation"):
                    # If recovery was successful, try opening a different file
                    QMessageBox.warning(
                        self.editor_window,
                        "Open Failed",
                        f"Could not open the document: {str(e)}\n\n"
                        "Please try opening a different file.",
                    )
                    return self.open_document(bypass_dialog=False)

                # If recovery failed, show error
                QMessageBox.critical(
                    self.editor_window,
                    "Open Failed",
                    f"Could not open the document: {str(e)}\n\n"
                    f"An error report has been created at: {error_report}",
                )
                return False
        return False

    def save_document(self):
        """Save the current document using native format.

        Saves the document to its current path if one exists, otherwise
        calls save_document_as() to prompt for a new path.

        Implements error recovery for common failure scenarios:
        - Permission errors: Suggests saving to a different location
        - Disk full errors: Suggests freeing space or saving to a different drive
        - Path not found: Attempts to create the directory structure

        Returns:
            bool: True if the document was successfully saved, False otherwise
        """
        try:
            # Record save attempt time
            self.last_save_time = datetime.now()

            if self.current_path:
                result = self._save_to_path(self.current_path)
                if result:
                    # Reset consecutive error counter on success
                    self.consecutive_errors = 0
                    return True
                else:
                    # Increment error counter
                    self.consecutive_errors += 1

                    # If we've had multiple consecutive errors, try recovery
                    if self.consecutive_errors >= self.max_consecutive_errors:
                        logger.warning(
                            f"Multiple save failures ({self.consecutive_errors}), attempting recovery"
                        )
                        return self._recover_save_failure()
                    return False
            else:
                return self.save_document_as()

        except Exception as e:
            logger.error(f"Error in save_document: {str(e)}", exc_info=True)

            # Create error report
            error_report = create_error_report(e, "document save operation")

            # Attempt recovery
            if recover_from_error(self.editor_window, e, "document save operation"):
                # If recovery was successful, try save_document_as as fallback
                self.status_updated.emit(
                    "Attempting to save to a different location..."
                )
                return self.save_document_as()
            else:
                # If recovery failed, show error and suggest manual save
                QMessageBox.critical(
                    self.editor_window,
                    "Save Failed",
                    f"Could not save the document: {str(e)}\n\n"
                    f"An error report has been created at: {error_report}\n\n"
                    "Please try saving to a different location or format.",
                )
                return False

    def _recover_save_failure(self):
        """Attempt to recover from repeated save failures.

        Implements strategies for recovering from persistent save failures:
        1. Try saving to a temporary location
        2. Try saving in a different format
        3. Suggest manual intervention

        Returns:
            bool: True if recovery was successful, False otherwise
        """
        try:
            # Create a temporary file as fallback
            import tempfile

            temp_dir = Path(tempfile.gettempdir())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = temp_dir / f"rtf_editor_recovery_{timestamp}.html"

            # Ask user if they want to save to the temporary location
            response = QMessageBox.question(
                self.editor_window,
                "Save Recovery",
                f"Multiple attempts to save have failed.\n\n"
                f"Would you like to save to a temporary location?\n{temp_file}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )

            if response == QMessageBox.StandardButton.Yes:
                # Try to save to temp file
                if self._save_to_path(str(temp_file)):
                    self.status_updated.emit(
                        f"Document saved to temporary location: {temp_file}"
                    )

                    # Update current path to the temp file
                    self.current_path = str(temp_file)
                    self.auto_save_manager.set_document_path(self.current_path)
                    self.update_window_title()

                    # Reset error counter
                    self.consecutive_errors = 0
                    return True

            # If temp save failed or user declined, suggest manual save
            self.status_updated.emit(
                "Please try saving manually to a different location"
            )
            return self.save_document_as()

        except Exception as e:
            logger.error(f"Error in recovery attempt: {str(e)}", exc_info=True)
            return False

    def save_document_as(self):
        """Save the current document to a new file path using native format.

        Shows a file dialog to let the user choose a new path and filename,
        then saves the document to that path.

        Returns:
            bool: True if the document was successfully saved, False otherwise
        """
        suggested_path = DEFAULT_DIR / self.get_default_filename()
        file_path, _ = QFileDialog.getSaveFileName(
            self.editor_window, "Save Document As", str(suggested_path), FILE_FILTER
        )

        if file_path:
            # Convert to Path object for safer manipulation
            path_obj = Path(file_path)
            # Ensure the file has the correct extension
            if path_obj.suffix.lower() != DEFAULT_EXTENSION.lower():
                path_obj = Path(str(path_obj) + DEFAULT_EXTENSION)
            return self._save_to_path(str(path_obj))
        return False

    def _save_to_path(self, file_path):
        """Helper function to save content using QTextDocumentWriter.

        Implements the actual saving functionality using Qt's QTextDocumentWriter.
        Handles format selection based on file extension and updates the document state
        after successful save.

        Args:
            file_path (str): The path where the document should be saved

        Returns:
            bool: True if the document was successfully saved, False otherwise

        Raises:
            Exception: Handled internally for file writing errors
        """
        try:
            # Input validation
            if not file_path or not isinstance(file_path, str):
                raise ValueError("Invalid file path provided")

            # Convert to Path object for safer manipulation
            path_obj = Path(file_path)

            # Validate parent directory exists and is writable
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
            elif not os.access(str(parent_dir), os.W_OK):
                raise PermissionError(
                    f"No write permission for directory: {parent_dir}"
                )

            # Get the QTextDocument from the editor
            document = self.editor_window.text_edit.document()

            # Use QTextDocumentWriter for native Qt format
            writer = QTextDocumentWriter(str(path_obj))
            if path_obj.suffix.lower() == ".html":
                # QByteArray constructor takes (size, byte_value) for a byte sequence
                # For a string, pass 0 as size and the bytes as the second argument
                writer.setFormat(QByteArray(0, b"html"))
            else:
                # Default to HTML format stored in our custom extension
                writer.setFormat(QByteArray(0, b"html"))

            success = writer.write(document)

            if not success:
                raise Exception("QTextDocumentWriter could not write the document")

            self.current_path = str(path_obj)
            self.set_modified(False)
            self.status_updated.emit(f"Saved: {path_obj}")
            return True

        except PermissionError as e:
            logger.error(f"Permission error saving file: {str(e)}", exc_info=True)

            # Create error report
            error_report = create_error_report(e, "file permission error")

            # Attempt recovery
            if recover_from_error(self.editor_window, e, "document save operation"):
                # Suggest saving to a different location
                QMessageBox.warning(
                    self.editor_window,
                    "Permission Error",
                    f"You don't have permission to save to this location: {path_obj}\n\n"
                    "Please try saving to a different location.",
                )
                return self.save_document_as()
            return False

        except OSError as e:
            logger.error(f"OS error saving file: {str(e)}", exc_info=True)

            # Check for disk full error
            if "No space left on device" in str(e):
                QMessageBox.critical(
                    self.editor_window,
                    "Disk Full",
                    "There is not enough disk space to save the file.\n\n"
                    "Please free up some space or save to a different drive.",
                )
                return self.save_document_as()

            # Create error report
            error_report = create_error_report(e, "file system error")

            # Attempt recovery
            if recover_from_error(self.editor_window, e, "document save operation"):
                return self.save_document_as()
            return False

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}", exc_info=True)

            # Create error report
            error_report = create_error_report(e, "document save operation")

            # Attempt recovery
            if recover_from_error(self.editor_window, e, "document save operation"):
                # If recovery was successful, try save_document_as as fallback
                self.status_updated.emit(
                    "Attempting to save to a different location..."
                )
                return self.save_document_as()

            # If recovery failed, show error and suggest manual save
            QMessageBox.critical(
                self.editor_window,
                "Save Failed",
                f"Could not save the document: {str(e)}\n\n"
                f"An error report has been created at: {error_report}\n\n"
                "Please try saving to a different location or format.",
            )
            return False

    def get_default_filename(self):
        """Suggest a default filename with the custom extension.

        Creates a default filename for new documents or when saving as.
        If the document already has a path, uses the base name from that path.
        Otherwise, uses "Untitled" with the default extension.

        Returns:
            str: A suggested filename with the default extension
        """
        if self.current_path:
            # Convert to Path object for safer manipulation
            path_obj = Path(self.current_path)
            # Keep existing name but ensure correct extension
            return f"{path_obj.stem}{DEFAULT_EXTENSION}"
        return f"Untitled{DEFAULT_EXTENSION}"

    def check_unsaved_changes(self):
        """Check for unsaved changes and prompt user if necessary.

        If the document has unsaved changes, shows a dialog asking the user whether to:
        - Save the changes
        - Discard the changes
        - Cancel the operation

        Returns:
            bool: True if it's safe to proceed (changes saved or discarded), False otherwise
        """
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

        Converts the current document to a DocumentFormat object that can be stored
        in a database. Includes HTML content, plain text, metadata, and identifiers.

        If the document doesn't have an ID, generates a new UUID.
        If the document doesn't have a name, derives one from the file path or uses a default.

        Returns:
            DocumentFormat: The current document in DocumentFormat structure with the following fields:
                - id: Unique identifier for the document
                - name: Human-readable name for the document
                - html_content: The document content in HTML format
                - plain_text: The document content as plain text
                - created_at: Timestamp of creation
                - modified_at: Timestamp of last modification
                - metadata: Additional information like word count
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
        """Load document from a DocumentFormat model.

        Converts the document format model to HTML content and sets it as the document content.

        Args:
            doc_format (DocumentFormat): The document format to load

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract content from the document format
            content = doc_format.html_content

            # Set the content in the editor
            self.editor_window.text_edit.setHtml(content)

            # Call the document_loaded method with the content
            if hasattr(self.editor_window, "document_loaded"):
                self.editor_window.document_loaded(content)

            # Update state and store document metadata for auto-save
            self.document_id = doc_format.id
            self.document_name = doc_format.name
            self.set_modified(False)
            self.document_loaded.emit(content)
            self.status_updated.emit(f"Loaded document: {doc_format.name}")

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error loading document format: {str(e)}")
            logger.error(f"Error loading document format: {str(e)}", exc_info=True)
            return False

    def _load_file(self, file_path):
        """Load a document from a file.

        Reads the content of the file and sets it as the document content.

        Args:
            file_path (str): Path to the file to load

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not file_path or not os.path.exists(file_path):
                self.error_occurred.emit(f"File not found: {file_path}")
                return False

            # Create a QFile for reading
            file = QFile(file_path)
            if not file.open(
                QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
            ):
                self.error_occurred.emit(f"Could not open file: {file_path}")
                return False

            # Read the content
            stream = QTextStream(file)
            content = stream.readAll()
            file.close()

            # Set the document content
            self.editor_window.text_edit.setHtml(content)

            # Call the document_loaded method with the content
            if hasattr(self.editor_window, "document_loaded"):
                self.editor_window.document_loaded(content)

            # Update state
            self.current_path = file_path
            self.set_modified(False)
            self.document_loaded.emit(content)
            self.status_updated.emit(f"Loaded document: {os.path.basename(file_path)}")

            # Update auto-save path
            if hasattr(self.auto_save_manager, 'set_document_path'):
                self.auto_save_manager.set_document_path(file_path)

            return True

        except Exception as e:
            self.error_occurred.emit(f"Error loading file: {str(e)}")
            logger.error(f"Error loading file {file_path}: {str(e)}", exc_info=True)
            return False
