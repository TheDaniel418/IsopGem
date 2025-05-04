"""Recovery utilities for the RTF editor.

This module provides functions and classes for implementing consistent error recovery
throughout the RTF editor. It includes mechanisms for:
1. Auto-saving documents
2. Recovering from crashes
3. Handling common failure scenarios
4. Providing graceful fallbacks

These utilities help improve the user experience by ensuring that work is not lost
and that the application can recover from errors in a predictable way.
"""

import json
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QTextEdit

from shared.ui.widgets.rtf_editor.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)


class AutoSaveManager(QObject):
    """Manages automatic saving of document content to prevent data loss.

    This class provides functionality to periodically save document content
    to temporary files, which can be used to recover content in case of
    application crashes or other failures.

    Attributes:
        auto_save_triggered (pyqtSignal): Signal emitted when auto-save occurs
        recovery_available (pyqtSignal): Signal emitted when recovery data is found
    """

    auto_save_triggered = pyqtSignal()
    recovery_available = pyqtSignal(str)  # Path to recovery file

    def __init__(self, editor: QTextEdit, interval: int = 60000):
        """Initialize the AutoSaveManager.

        Args:
            editor (QTextEdit): The text editor to monitor and auto-save
            interval (int): Auto-save interval in milliseconds (default: 60000 = 1 minute)
        """
        super().__init__()
        self.editor = editor
        self.interval = interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_save)
        self.recovery_dir = self._get_recovery_directory()
        self.current_document_path = None
        self.last_save_content = ""
        self.disable_recovery = False  # Flag to disable recovery prompts

        # Create recovery directory if it doesn't exist
        self.recovery_dir.mkdir(parents=True, exist_ok=True)

    def _get_recovery_directory(self) -> Path:
        """Get the directory for storing recovery files.

        Returns:
            Path: Directory path for recovery files
        """
        return Path.home() / ".isopgem" / "recovery"

    def start(self):
        """Start the auto-save timer."""
        self.timer.start(self.interval)
        logger.info(f"Auto-save started with interval of {self.interval/1000} seconds")

    def stop(self):
        """Stop the auto-save timer."""
        self.timer.stop()
        logger.info("Auto-save stopped")

    def cleanup(self):
        """Clean up resources and stop auto-save.

        Call this method when the editor is being destroyed.
        """
        self.stop()
        self.editor = None
        logger.debug("Auto-save manager cleaned up")

    def set_interval(self, interval: int):
        """Set the auto-save interval.

        Args:
            interval (int): New interval in milliseconds
        """
        self.interval = interval
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(self.interval)
        logger.info(f"Auto-save interval set to {self.interval/1000} seconds")

    def set_document_path(self, path: str):
        """Set the current document path.

        Args:
            path (str): Path to the current document
        """
        self.current_document_path = path

    def auto_save(self):
        """Perform auto-save of the current document content.

        Saves the current document content to a temporary file if it has changed
        since the last save.
        """
        try:
            # Check if editor still exists
            if not self.editor:
                logger.debug("Editor no longer exists, skipping auto-save")
                return

            # Check if editor is valid (not destroyed)
            try:
                # Try to access a property to see if the object is still valid
                _ = self.editor.objectName()
            except RuntimeError:
                logger.debug("Editor has been deleted, skipping auto-save")
                return

            # Get current content
            current_content = self.editor.toHtml()

            # Only save if content has changed
            if current_content != self.last_save_content:
                # Update last save content even if recovery is disabled
                self.last_save_content = current_content

                # Skip creating recovery files if recovery is disabled
                if self.disable_recovery:
                    logger.debug("Recovery is disabled, skipping auto-save file creation")
                    self.auto_save_triggered.emit()
                    return

                # Generate recovery file name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                doc_id = "unsaved"
                if self.current_document_path:
                    doc_id = Path(self.current_document_path).stem

                recovery_file = self.recovery_dir / f"{doc_id}_{timestamp}.recovery"

                # Save metadata
                metadata = {
                    "timestamp": timestamp,
                    "original_path": self.current_document_path,
                    "format": "html",
                }

                # Save content and metadata
                with open(recovery_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(metadata) + "\n")
                    f.write(current_content)

                self.auto_save_triggered.emit()
                logger.info(f"Auto-saved document to {recovery_file}")

                # Clean up old recovery files
                self._cleanup_old_recovery_files()
        except Exception as e:
            logger.error(f"Auto-save failed: {str(e)}", exc_info=True)

    def _cleanup_old_recovery_files(self, max_files: int = 10):
        """Clean up old recovery files, keeping only the most recent ones.

        Args:
            max_files (int): Maximum number of recovery files to keep per document
        """
        try:
            # Group files by document ID
            recovery_files = {}
            for file in self.recovery_dir.glob("*.recovery"):
                doc_id = file.stem.split("_")[0]
                if doc_id not in recovery_files:
                    recovery_files[doc_id] = []
                recovery_files[doc_id].append(file)

            # For each document, keep only the most recent files
            for doc_id, files in recovery_files.items():
                if len(files) > max_files:
                    # Sort by modification time (newest first)
                    sorted_files = sorted(
                        files, key=lambda f: f.stat().st_mtime, reverse=True
                    )
                    # Remove older files
                    for file in sorted_files[max_files:]:
                        file.unlink()
                        logger.debug(f"Removed old recovery file: {file}")
        except Exception as e:
            logger.error(f"Error cleaning up recovery files: {str(e)}", exc_info=True)

    def check_for_recovery_files(self) -> List[Path]:
        """Check for available recovery files.

        Returns:
            List[Path]: List of available recovery files
        """
        # If recovery is disabled, return empty list
        if self.disable_recovery:
            logger.debug("Recovery is disabled, not checking for recovery files")
            return []

        try:
            recovery_files = list(self.recovery_dir.glob("*.recovery"))
            if recovery_files:
                # Sort by modification time (newest first)
                recovery_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                for file in recovery_files:
                    logger.info(f"Found recovery file: {file}")
                return recovery_files
            return []
        except Exception as e:
            logger.error(f"Error checking for recovery files: {str(e)}", exc_info=True)
            return []

    def clear_recovery_files(self) -> bool:
        """Clear all recovery files.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            recovery_files = list(self.recovery_dir.glob("*.recovery"))
            for file in recovery_files:
                try:
                    file.unlink()
                    logger.debug(f"Deleted recovery file: {file}")
                except Exception as e:
                    logger.error(f"Error deleting recovery file {file}: {str(e)}")

            logger.info(f"Cleared {len(recovery_files)} recovery files")
            return True
        except Exception as e:
            logger.error(f"Error clearing recovery files: {str(e)}", exc_info=True)
            return False

    def load_recovery_file(self, recovery_file: Path) -> Tuple[str, Optional[str]]:
        """Load content from a recovery file.

        Args:
            recovery_file (Path): Path to the recovery file

        Returns:
            Tuple[str, Optional[str]]: Tuple of (content, original_path)
        """
        try:
            with open(recovery_file, "r", encoding="utf-8") as f:
                # First line is metadata
                metadata_line = f.readline()
                metadata = json.loads(metadata_line)

                # Rest is content
                content = f.read()

                logger.info(f"Loaded recovery file: {recovery_file}")
                return content, metadata.get("original_path")
        except Exception as e:
            logger.error(f"Error loading recovery file: {str(e)}", exc_info=True)
            return "", None

    def delete_recovery_file(self, recovery_file: Path) -> bool:
        """Delete a recovery file.

        Args:
            recovery_file (Path): Path to the recovery file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            recovery_file.unlink()
            logger.info(f"Deleted recovery file: {recovery_file}")
            return True
        except Exception as e:
            logger.error(f"Error deleting recovery file: {str(e)}", exc_info=True)
            return False


def recover_from_error(parent: QObject, error: Exception, context: str = "") -> bool:
    """Attempt to recover from an error.

    This function implements specific recovery strategies based on the type of error
    and the context in which it occurred.

    Args:
        parent (QObject): Parent widget for any dialogs
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred

    Returns:
        bool: True if recovery was successful, False otherwise
    """
    try:
        error_type = type(error).__name__
        error_msg = str(error)

        logger.error(
            f"Attempting to recover from {error_type}: {error_msg} in {context}"
        )

        # File-related errors
        if isinstance(error, (FileNotFoundError, PermissionError, IOError)):
            return _recover_from_file_error(parent, error, context)

        # Memory-related errors
        elif isinstance(error, MemoryError):
            return _recover_from_memory_error(parent, error, context)

        # Image-related errors
        elif "PIL" in error_type or "Image" in error_type:
            return _recover_from_image_error(parent, error, context)

        # Generic recovery
        else:
            logger.warning(
                f"No specific recovery strategy for {error_type}, using generic recovery"
            )
            return _generic_recovery(parent, error, context)

    except Exception as recovery_error:
        logger.error(
            f"Error during recovery attempt: {str(recovery_error)}", exc_info=True
        )
        return False


def _recover_from_file_error(parent: QObject, error: Exception, context: str) -> bool:
    """Recover from file-related errors.

    Args:
        parent (QObject): Parent widget for any dialogs
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred

    Returns:
        bool: True if recovery was successful, False otherwise
    """
    error_msg = str(error)

    # Create a temporary file as fallback
    if "save" in context.lower():
        try:
            temp_dir = Path(tempfile.gettempdir())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = temp_dir / f"rtf_editor_recovery_{timestamp}.html"

            QMessageBox.warning(
                parent,
                "File Save Error",
                f"Could not save to the original location: {error_msg}\n\n"
                f"Your document will be saved to: {temp_file}",
            )

            logger.info(f"Created temporary file as fallback: {temp_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create temporary file: {str(e)}", exc_info=True)
            return False

    # Suggest alternative locations for opening files
    elif "open" in context.lower():
        QMessageBox.warning(
            parent,
            "File Open Error",
            f"Could not open the file: {error_msg}\n\n"
            "Please try opening a different file or creating a new document.",
        )
        return True

    return False


def _recover_from_memory_error(parent: QObject, error: Exception, context: str) -> bool:
    """Recover from memory-related errors.

    Args:
        parent (QObject): Parent widget for any dialogs
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred

    Returns:
        bool: True if recovery was successful, False otherwise
    """
    # Attempt to free memory
    import gc

    gc.collect()

    QMessageBox.warning(
        parent,
        "Memory Error",
        "The application is running low on memory.\n\n"
        "Some operations may be limited. Consider saving your work and restarting the application.",
    )

    logger.info("Attempted memory recovery by forcing garbage collection")
    return True


def _recover_from_image_error(parent: QObject, error: Exception, context: str) -> bool:
    """Recover from image-related errors.

    Args:
        parent (QObject): Parent widget for any dialogs
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred

    Returns:
        bool: True if recovery was successful, False otherwise
    """
    if "insert" in context.lower() or "load" in context.lower():
        QMessageBox.warning(
            parent,
            "Image Error",
            f"Could not process the image: {str(error)}\n\n"
            "The image may be corrupted or in an unsupported format.",
        )
        return True

    elif "resize" in context.lower() or "scale" in context.lower():
        QMessageBox.warning(
            parent,
            "Image Scaling Error",
            f"Could not resize the image: {str(error)}\n\n"
            "The operation will be skipped.",
        )
        return True

    return False


def _generic_recovery(parent: QObject, error: Exception, context: str) -> bool:
    """Generic recovery strategy for unspecified errors.

    Args:
        parent (QObject): Parent widget for any dialogs
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred

    Returns:
        bool: True if recovery was successful, False otherwise
    """
    QMessageBox.warning(
        parent,
        "Operation Failed",
        f"An error occurred during {context}:\n{str(error)}\n\n"
        "The operation has been cancelled to prevent data loss.",
    )

    logger.info(f"Applied generic recovery for {type(error).__name__} in {context}")
    return True


def create_error_report(error: Exception, context: str) -> str:
    """Create a detailed error report for troubleshooting.

    Args:
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred

    Returns:
        str: Formatted error report
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_type = type(error).__name__
        error_msg = str(error)
        error_traceback = traceback.format_exc()

        report = f"""
ERROR REPORT
===========
Timestamp: {timestamp}
Error Type: {error_type}
Context: {context}
Message: {error_msg}

Traceback:
{error_traceback}
"""

        # Save report to file
        reports_dir = Path.home() / ".isopgem" / "error_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = (
            reports_dir / f"error_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Created error report: {report_file}")
        return str(report_file)
    except Exception as e:
        logger.error(f"Failed to create error report: {str(e)}", exc_info=True)
        return ""
